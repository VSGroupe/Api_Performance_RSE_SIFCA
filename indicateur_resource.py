
from flask_restful import Resource
from flask import request, make_response
import copy
from data import calculated_keys, test_indicators_keys
from dbkeys import supabase
from utils import ecartCalculatedKeys, formuleCalcules, formuleSomme, formuleDernierMois, formuleMoyenne, PerformGlobal, extraire_chiffres, indexes_by, testIndicatorsFormulas
from utils_data import readDataJson, saveDataInJson

class GetDataEntiteIndicateur(Resource):
    # Appel des données indicateurs
    def post(self):
        args = request.get_json()
        annee = args["annee"]
        entite = args["entite"]

        try:
            # Essayer d'abord les fichiers locaux
            try:
                dataValeurList = readDataJson(entite, f"{entite}_data_{annee}.json")
                dataValidationList = readDataJson(entite, f"{entite}_validation_{annee}.json")
                return {
                    "status": True,
                    "entite": entite,
                    "annee": annee,
                    "valeurs": dataValeurList,
                    "validations": dataValidationList
                }
            except FileNotFoundError:
                pass  # Passer à Supabase si fichier non trouvé

            # Récupération depuis Supabase
            supabase_data = supabase.table('DataIndicateur').select("*").eq("id", f"{entite}_{annee}").execute()
            
            if not supabase_data.data:
                return {"status": False, "message": "Données non trouvées"}, 404
            
            dataValeurList = supabase_data.data[0]['valeurs']
            dataValidationList = supabase_data.data[0]['validations']
            
            # Sauvegarde locale
            saveDataInJson(dataValeurList, entite, f"{entite}_data_{annee}.json")
            saveDataInJson(dataValidationList, entite, f"{entite}_validation_{annee}.json")

            return {
                "status": True,
                "entite": entite,
                "annee": annee,
                "valeurs": dataValeurList,
                "validations": dataValidationList
            }

        except Exception as e:
            return {"status": False, "message": f"Erreur: {str(e)}"}, 500


class UpdateDataEntiteIndicateur(Resource):
    def post(self):
        try:
            args = request.get_json()
            required_fields = ["annee", "entite", "colonne", "ligne", "valeur", "type", "formule"]
            if not all(field in args for field in required_fields):
                return {"status": False, "message": "Champs requis manquants"}, 400

            annee = args["annee"]
            entite = args["entite"]
            colonne = int(args["colonne"])  # Convertir en int pour éviter les erreurs
            ligne = int(args["ligne"])      # Convertir en int
            valeur = args["valeur"]
            type_ind = args["type"]
            formule = args["formule"]

            id = f"{entite}_{annee}"
            id_next_year = f"{entite}_{annee + 1}"

            # 1. Récupération des données
            try:
                # Récupérer depuis Supabase
                data_response = supabase.table('DataIndicateur').select("*").eq("id", id).execute()
                if not data_response.data:
                    return {"status": False, "message": "Données non trouvées"}, 404
                    
                current_data = data_response.data[0]
                data_values = current_data['valeurs']
                data_ecarts = current_data['ecarts']
                data_validations = current_data['validations']

                # Vérifier que les index sont valides
                if ligne >= len(data_values) or colonne >= len(data_values[0]):
                    return {"status": False, "message": "Index ligne/colonne invalide"}, 400

                # Vérifier si la donnée est déjà validée
                if data_validations[ligne][colonne]:
                    return {"status": False, "message": "Donnée déjà validée"}, 400

                # Créer des copies profondes
                data_values_copy = copy.deepcopy(data_values)
                data_ecarts_copy = copy.deepcopy(data_ecarts)

                # 2. Mise à jour de la valeur
                data_values_copy[ligne][colonne] = valeur

                # 3. Charger les données des années précédentes/suivantes
                try:
                    data_last_year = readDataJson(entite, f"{entite}_data_{annee - 1}.json")
                    realise_last_year = data_last_year[ligne][0] if data_last_year and len(data_last_year) > ligne else None
                except:
                    realise_last_year = None

                try:
                    data_next_year = readDataJson(entite, f"{entite}_data_{annee + 1}.json")
                    realise_next_year = data_next_year[ligne][0] if data_next_year and len(data_next_year) > ligne else None
                except:
                    realise_next_year = None

                # 4. Recalcul selon le type et formule
                if type_ind == "Primaire":
                    if formule == "Somme":
                        somme = formuleSomme(data_values_copy[ligne][1:])
                        data_values_copy[ligne][0] = somme
                        if somme is not None and realise_last_year is not None and realise_last_year != 0:
                            data_ecarts_copy[ligne] = ((realise_last_year - somme) / realise_last_year) * 100
                        else:
                            data_ecarts_copy[ligne] = None

                    elif formule == "Dernier mois renseigné":
                        dernier_mois = formuleDernierMois(data_values_copy[ligne][1:])
                        data_values_copy[ligne][0] = dernier_mois
                        if dernier_mois is not None and realise_last_year is not None and realise_last_year != 0:
                            data_ecarts_copy[ligne] = ((realise_last_year - dernier_mois) / realise_last_year) * 100
                        else:
                            data_ecarts_copy[ligne] = None

                    elif formule == "Moyenne":
                        moyenne = formuleMoyenne(data_values_copy[ligne][1:])
                        data_values_copy[ligne][0] = moyenne
                        if moyenne is not None and realise_last_year is not None and realise_last_year != 0:
                            data_ecarts_copy[ligne] = ((realise_last_year - moyenne) / realise_last_year) * 100
                        else:
                            data_ecarts_copy[ligne] = None

                # 5. Recalcul des indicateurs calculés
                for index in calculated_keys:
                    if index - 1 < len(data_values_copy):  # Vérification de l'index
                        new_row = formuleCalcules(index, data_values_copy, data_last_year)
                        if new_row is not None:
                            data_values_copy[index - 1] = new_row
                        
                        ecart_data = ecartCalculatedKeys(index, data_values_copy, realise_last_year, realise_next_year)
                        if ecart_data:
                            data_ecarts_copy[index - 1] = ecart_data.get("completedYear")

                # 6. Recalcul des indicateurs de test
                for index in test_indicators_keys:
                    if index - 1 < len(data_values_copy):  # Vérification de l'index
                        new_row = testIndicatorsFormulas(index, data_values_copy, data_last_year)
                        if new_row is not None:
                            data_values_copy[index - 1] = new_row

                # 7. Mise à jour dans Supabase
                update_data = {
                    'valeurs': data_values_copy,
                    'ecarts': data_ecarts_copy
                }
                
                supabase.table('DataIndicateur').update(update_data).eq('id', id).execute()

                # 8. Sauvegarde locale
                saveDataInJson(data_values_copy, entite, f"{entite}_data_{annee}.json")

                return {"status": True, "message": "Donnée mise à jour avec succès"}

            except Exception as e:
                return {"status": False, "message": f"Erreur lors de la mise à jour: {str(e)}"}, 500

        except Exception as e:
            return {"status": False, "message": f"Erreur inattendue: {str(e)}"}, 500
class DeleteDataEntiteIndicateur(Resource):
    def post(self):
        try:
            args = request.get_json()

            # Validate required fields
            required_fields = ["annee", "entite", "colonne", "ligne"]
            for field in required_fields:
                if field not in args:
                    return {"status": False, "message": f"Champ requis manquant: {field}"}, 400

            annee = args["annee"]
            entite = args["entite"]
            colonne = args["colonne"]
            ligne = args["ligne"]
            type = args.get("type", "Primaire")  # Optional with default
            formule = args.get("formule")  # Optional

            id = f"{entite}_{annee}"
            idNextYear = f"{entite}_{annee + 1}"

            # Get current data
            try:
                data_response = supabase.table('DataIndicateur').select("valeurs, ecarts, validations").eq("id", id).execute()
                data_next_year = supabase.table('DataIndicateur').select("ecarts").eq("id", idNextYear).execute()
                indicateurs_info = supabase.table('Indicateurs').select("axe, enjeu").order("numero", desc=False).execute()
            except Exception as e:
                return {"status": False, "message": f"Erreur Supabase: {str(e)}"}, 500

            # Extract data
            current_data = data_response.data[0]
            data_values = current_data['valeurs']
            data_ecarts = current_data['ecarts']
            data_validations = current_data['validations']
            data_ecarts_next_year = data_next_year.data[0]['ecarts']

            # Check if data is already validated
            if data_validations[ligne][colonne]:
                return {"status": False, "message": "La donnée est déjà validée"}, 400

            # Create a copy of the data to modify
            data_values_copy = copy.deepcopy(data_values)
            
            # Delete only the specified value (set to None)
            data_values_copy[ligne][colonne] = None

            # Get reference values from previous and next year
            try:
                data_last_year = readDataJson(entite, f"{entite}_data_{annee - 1}.json")
                data_next_year = readDataJson(entite, f"{entite}_data_{annee + 1}.json")
            except Exception as e:
                return {"status": False, "message": f"Erreur lecture données historiques: {str(e)}"}, 500

            realise_last_year = data_last_year[ligne][0] if data_last_year else None
            realise_next_year = data_next_year[ligne][0] if data_next_year else None

            # Recalculate values based on type and formula
            if type == "Primaire" and formule:
                if formule == "Somme":
                    list_temp = data_values_copy[ligne][1:]  # Exclude realized value
                    new_value = formuleSomme(list_temp)
                    data_values_copy[ligne][0] = new_value
                    
                elif formule == "Dernier mois renseigné":
                    list_temp = data_values_copy[ligne][1:]
                    new_value = formuleDernierMois(list_temp)
                    data_values_copy[ligne][0] = new_value
                    
                elif formule == "Moyenne":
                    list_temp = data_values_copy[ligne][1:]
                    new_value = formuleMoyenne(list_temp)
                    data_values_copy[ligne][0] = new_value

                # Recalculate ecart if we have a new value and reference
                if data_values_copy[ligne][0] is not None and realise_last_year is not None and realise_last_year != 0:
                    data_ecarts[ligne] = ((realise_last_year - data_values_copy[ligne][0]) / realise_last_year) * 100
                else:
                    data_ecarts[ligne] = None

            # Recalculate calculated indicators
            for index in calculated_keys:
                new_row = formuleCalcules(index, data_values_copy, data_last_year)
                if new_row is not None:
                    data_values_copy[index - 1] = new_row
                
                ecart_data = ecartCalculatedKeys(index, data_values_copy, realise_last_year, realise_next_year)
                if ecart_data:
                    data_ecarts[index - 1] = ecart_data.get("completedYear")
                    data_ecarts_next_year[index - 1] = ecart_data.get("completedNextYear")

            # Recalculate test indicators
            for index in test_indicators_keys:
                new_row = testIndicatorsFormulas(index, data_values_copy, data_last_year)
                if new_row is not None:
                    data_values_copy[index - 1] = new_row

            # Calculate global performance
            global_perf = PerformGlobal(data_ecarts)
            global_perf_next_year = PerformGlobal(data_ecarts_next_year)

            # Calculate axes and enjeux performance
            def calculate_performance(response_list, ecart_list, field):
                result = []
                indices = indexes_by(response_list, value=field)
                for group in indices:
                    values = [ecart_list[i] for i in group if ecart_list[i] is not None]
                    avg = sum(values) / len(values) if values else None
                    result.append(avg)
                return [100 if x is None else x for x in result[1:]]  # Skip first item

            axes_perf = calculate_performance(indicateurs_info.data, data_ecarts, "axe")
            enjeux_perf = calculate_performance(indicateurs_info.data, data_ecarts, "enjeu")
            axes_perf_next = calculate_performance(indicateurs_info.data, data_ecarts_next_year, "axe")
            enjeux_perf_next = calculate_performance(indicateurs_info.data, data_ecarts_next_year, "enjeu")

            # Update database
            try:
                # Update current year
                supabase.table('Performance').update({
                    'performs_piliers': axes_perf,
                    'performs_enjeux': enjeux_perf,
                    'performs_global': global_perf
                }).eq('id', id).execute()

                # Update next year
                supabase.table('Performance').update({
                    'performs_piliers': axes_perf_next,
                    'performs_enjeux': enjeux_perf_next,
                    'performs_global': global_perf_next_year
                }).eq('id', idNextYear).execute()

                # Update DataIndicateur
                supabase.table('DataIndicateur').update({
                    'valeurs': data_values_copy,
                    'ecarts': data_ecarts
                }).eq('id', id).execute()

                supabase.table('DataIndicateur').update({
                    'ecarts': data_ecarts_next_year
                }).eq('id', idNextYear).execute()

                # Save to JSON
                saveDataInJson(data_values_copy, entite, f"{entite}_data_{annee}.json")

            except Exception as e:
                return {"status": False, "message": f"Erreur mise à jour Supabase: {str(e)}"}, 500

            return {"status": True, "message": "Donnée supprimée avec succès"}

        except Exception as e:
            return {"status": False, "message": f"Erreur inattendue: {str(e)}"}, 500
# # class ComputePerformsEntite(Resource):
#     def post(self):
#         args = request.get_json()

#         annee = args["annee"]
#         entite = args["entite"]
#         colonne = args["colonne"]
#         ligne = args["ligne"]
#         valeurCible = args["datacible"]
#         type = args["type"]
#         formule = args["formule"]

#         id = f"{entite}_{annee}"

#         responseListEcart = supabase.table('DataIndicateur').select("ecarts").eq("id", id).execute().data
#         dicTemp = responseListEcart[0]
#         listEcart = dicTemp['ecarts']
#         responseRealise = supabase.table('DataIndicateur').select("valeurs").eq("id", id).execute().data
#         dicTemp = responseRealise[0]
#         listValeurs = dicTemp['valeurs']
#         dataRealise = listValeurs[ligne][0]

#         indicesList = [16, 46, 207, 222, 280]
#         indicesListEnjeux = [16, 21, 27, 34, 46, 181, 200, 206, 221, 245, 262, 280]

#         listAxes = []
#         listEnjeux = []

#         if type == "Primaire":

#             if formule == "Somme":
#                 if dataRealise != None:
#                     dataEcart = ((valeurCible - dataRealise) / valeurCible) * 100
#                     listEcart[ligne] = dataEcart
            
#             elif formule == "Dernier mois renseigné":
#                 if dataRealise != None:
#                     dataEcart = ((valeurCible - dataRealise) / valeurCible) * 100
#                     listEcart[ligne] = dataEcart

#             elif formule == "Moyenne":
#                 if dataRealise != None:
#                     dataEcart = ((valeurCible - dataRealise) / valeurCible) * 100
#                     listEcart[ligne] = dataEcart

#         globalPerfData = PerformGlobal(listEcart)

#         #decoupage de listEcart pous definir listes des Axes pour performances
#         for i in range(len(indicesList) - 1):
#             axeList = listEcart[indicesList[i]:indicesList[i + 1]]
#             listAxes.append(axeList)
#         for index, item in enumerate(listAxes):
#             l = []
#             count = 0
#             for data in item:
#                 if data != None:
#                     l.append(data)
#                     count += 1
#             if l != [] :
#                 listAxes[index] = sum(l) / count
#             else:
#                 listAxes[index] = None

#         #decoupage de listEcart pous definir listes des Enjeux pour performances Enjeux
#         for i in range(len(indicesListEnjeux) - 1):
#             enjeuList = listEcart[indicesListEnjeux[i]:indicesListEnjeux[i + 1]]
#             listEnjeux.append(enjeuList)
#         for index, item in enumerate(listEnjeux):
#             l = []
#             count = 0
#             for data in item:
#                 if data != None:
#                     l.append(data)
#                     count += 1
#             if l != [] :
#                 listEnjeux[index] = sum(l) / count
#             else:
#                 listEnjeux[index] = None
        
#         supabase.table('Performance').update({'performs_piliers': listAxes}).eq('id',id).execute()
#         supabase.table('Performance').update({'performs_enjeux': listEnjeux}).eq('id',id).execute()
#         supabase.table('Performance').update({'performs_global': globalPerfData}).eq('id', id).execute()
#         supabase.table('DataIndicateur').update({"ecarts" : listEcart}).eq('id',id).execute()

#         return {"status":True}
class ChangeStatusEntityIndic(Resource):
    def post(self):
        args = request.get_json()

        annee = args["annee"]
        entite = args["entite"]
        indexValue = args["statusButton"]
        numeroLigne = args["ligne"]

        id = f"{entite}_{annee}"

        responseListStatus = supabase.table('DataIndicateur').select("status_entity").eq("id", id).execute().data
        dicTemp = responseListStatus[0]
        listStatus = dicTemp['status_entity']
        if indexValue == 0:
            listStatus[numeroLigne] = False
        else:
            listStatus[numeroLigne] = True
        
        supabase.table('DataIndicateur').update({"status_entity": listStatus}).eq('id', id).execute()

        return {"status":True}
    
class UpdateDataInApiDB(Resource):
    def post(self):

        entitiesList = ["sucrivoire-siege", "sucrivoire-borotou-koro", "sucrivoire-zuenoula",
        "grel-tsibu","grel-apimenim",
        "saph-siege","saph-bettie","saph-bongo","saph-loeth","saph-ph-cc",
                "saph-rapides-grah","saph-toupah","saph-yacoli",
        "palmci-siege","palmci-blidouba","palmci-boubo","palmci-ehania","palmci-gbapet",
        "palmci-iboke","palmci-irobo","palmci-neka","palmci-toumanguie",
        "sucrivoire",
        "palmci", "sania", "mopp", "golden-sifca", "thsp",
        "siph","crc","renl","saph","grel",
        "sucre","oleagineux","caoutchouc-naturel","sifca-holding", "groupe-sifca", "comex"]

        for entity in entitiesList:
            idEntity = f"{entity}_2024"
            dataListFromSupabase = supabase.table('DataIndicateur').select("valeurs", "validations").eq("id", idEntity).execute().data
            dataValeuListApi = readDataJson(entity, f"{entity}_data_2024.json")
            dataValidationsApi = readDataJson(entity, f"{entity}_validation_2024.json")
            print(entity)
            dataValeuListApi = dataListFromSupabase[0]["valeurs"]
            dataValidationsApi = dataListFromSupabase[0]["validations"]
            saveDataInJson(dataValeuListApi, entity, f"{entity}_data_2024.json")
            saveDataInJson(dataValidationsApi, entity, f"{entity}_validation_2024.json")
        

        return {"status": True}




class UpdateAllDataEntiteIndicateur(Resource):
    # Mise à jour des données indicateurs
    def post(self):
        args = request.get_json()

        annee = args["annee"]
        entite = args["entite"]
        dataValeurList = args["valeurs"]
        dataValidationsList = args["validations"]

        saveDataInJson(dataValeurList,entite,f"{entite}_data_{annee}.json")
        saveDataInJson(dataValidationsList, entite, f"{entite}_validation_{annee}.json")

        return {"status":True}

class UpdateDataEntiteIndicateurFromSupabase(Resource):
    # Mise à jour des données indicateurs
    def post(self):

        args = request.get_json()

        id = args["id"]
        annee = extraire_chiffres(id)

        response = supabase.table('DataIndicateur').select("*").eq("id",id).execute().data
        data = response[0]

        entite = data["entite"]
        dataValeurList = data["valeurs"]
        dataValidationsList = data["validations"]

        saveDataInJson(dataValeurList,entite,f"{entite}_data_{annee}.json")
        saveDataInJson(dataValidationsList, entite, f"{entite}_validation_{annee}.json")

        return {"status":True}

class UpdateValidationEntiteIndicateur(Resource):
    def post(self):
        try:
            args = request.get_json()
            annee = args["annee"]
            entite = args["entite"]
            colonne = args["colonne"]
            ligne = args["ligne"]
            valide = args["valide"]

            id = f"{entite}_{annee}"

            # 1. Récupérer les données actuelles de Supabase
            current_data = supabase.table('DataIndicateur').select("*").eq("id", id).execute().data
            if not current_data:
                return {"status": False, "message": "Données non trouvées"}, 404
                
            current_validations = current_data[0]['validations']

            # 2. Vérifier que la valeur actuelle est différente avant mise à jour
            if current_validations[ligne][colonne] == valide:
                return {"status": True, "message": "Aucun changement nécessaire"}

            # 3. Mettre à jour uniquement le champ spécifique
            current_validations[ligne][colonne] = valide

            # 4. Mettre à jour Supabase en premier
            update_response = supabase.table('DataIndicateur').update(
                {'validations': current_validations}
            ).eq('id', id).execute()

            # 5. Vérifier que la mise à jour Supabase a réussi
            if not update_response.data:
                return {"status": False, "message": "Échec de la mise à jour Supabase"}, 500

            # 6. Mettre à jour le fichier JSON local
            saveDataInJson(current_validations, entite, f"{entite}_validation_{annee}.json")

            return {"status": True}

        except Exception as e:
            return {"status": False, "message": f"Erreur: {str(e)}"}, 500



class EntiteExportAllData(Resource):

    def getRealise(self,dataValeurs):
        result = []
        for data in dataValeurs :
            result.append(data[0])
        return result

    def getJson(self,start,end,dataEntite, dataRealise, realiseValidationEntite,  dataEntiteList, validationsEntite, realisesSousEntitesList, validationSousEntites, sousEntitesStringList):
        kList = []
        for i in range(start - 1, end - 1):
            index = dataEntite[i]["numero"] - 1
            kDoc = {
                    "numero": dataEntite[i]["numero"], # i + 1
                    "reference": dataEntite[i]["reference"],
                    "intitule": dataEntite[i]["intitule"],
                    "processus": dataEntite[i]["processus"],
                    "unite": dataEntite[i]["unite"],
                    "type": dataEntite[i]["type"],
                    "realise": dataRealise[index],
                    "dataJan": dataEntiteList[index][1],
                    "dataFeb": dataEntiteList[index][2],
                    "dataMar": dataEntiteList[index][3],
                    "dataApr": dataEntiteList[index][4],
                    "dataMay": dataEntiteList[index][5],
                    "dataJun": dataEntiteList[index][6],
                    "dataJul": dataEntiteList[index][7],
                    "dataAug": dataEntiteList[index][8],
                    "dataSep": dataEntiteList[index][9],
                    "dataOct": dataEntiteList[index][10],
                    "dataNov": dataEntiteList[index][11],
                    "dataDec": dataEntiteList[index][12],
                    "allValidationsList": [realiseValidationEntite[index], validationsEntite[index][1], validationsEntite[index][2], validationsEntite[index][3], validationsEntite[index][4], validationsEntite[index][5], validationsEntite[index][6], validationsEntite[index][7], validationsEntite[index][8], validationsEntite[index][9], validationsEntite[index][10], validationsEntite[index][11], validationsEntite[index][12]]
                }
            if len(sousEntitesStringList) != 0:
                for sousEntite in sousEntitesStringList:
                    kDoc[f"sousEntite{sousEntitesStringList.index(sousEntite)}"] = realisesSousEntitesList[sousEntitesStringList.index(sousEntite)][i]
                    kDoc["allValidationsList"].append(validationSousEntites[sousEntitesStringList.index(sousEntite)][i])
            kList.append(kDoc)
        return kList

    def getDataEntite(self, idEntite, annee):
        id = f"{idEntite}_{annee}"
        response = supabase.table('DataIndicateur').select("*").eq("id", id).execute().data
        data = response[0]

        return data["valeurs"]

    def getValidationEntite(self, idEntite, annee):
        id = f"{idEntite}_{annee}"
        response = supabase.table('DataIndicateur').select("*").eq("id", id).execute().data
        data = response[0]

        return data["validations"]

    def post(self):
        args = request.get_json()
        try :

            annee = args["annee"]
            entiteId = args["entiteId"]
            sousEntites = args["sousEntites"]
            dataValeursListSousEntites = []
            dataValidationSousEntites = []

            ###################################

            kEntite = supabase.table("Entites").select("*").eq("id_entite", entiteId).execute()
            dataEntite = kEntite.data[0]

            filiale = dataEntite["filiale"]
            entiteName = dataEntite["nom_entite"]
            color = dataEntite["couleur"]

            dataValeurList = self.getDataEntite(entiteId, annee)

            dataValidationList = self.getValidationEntite(entiteId, annee)

            dataRealise = self.getRealise(dataValeurList)

            dataValidationRealise = self.getRealise(dataValidationList)

            #################################
            
            if len(sousEntites) != 0:
                for entity in sousEntites:
                    datasSousEntite = self.getDataEntite(entity, annee)
                    validationSousEntite = self.getValidationEntite(entity, annee)
                    realiseSousEntite = self.getRealise(datasSousEntite)
                    realiseValidationSousEntite = self.getRealise(validationSousEntite)
                    dataValeursListSousEntites.append(realiseSousEntite)
                    dataValidationSousEntites.append(realiseValidationSousEntite)


            #################################

            kIndicateur = supabase.table("Indicateurs").select("*").order("axe, index_ordering, reference", desc=False).execute()
            dataEntite = kIndicateur.data

            ## Général

            allRows = self.getJson(1,288,dataEntite,dataRealise, dataValidationRealise, dataValeurList, dataValidationList, dataValeursListSousEntites, dataValidationSousEntites, sousEntites)

            return {
                "entreprise": "Groupe SIFCA",
                "filiale": f"{filiale}",
                "entite": f"{entiteName}",
                "annee": annee,
                "color":color,
                "data": allRows
            }
        except Exception as e :
            print(e)
            return make_response({"status":False},404)

class EntiteExportENAllData(Resource):

    def getRealise(self,dataValeurs):
        result = []
        for data in dataValeurs :
            result.append(data[0])
        return result

    def getJson(self,start,end,dataEntite, dataRealise, realiseValidationEntite,  dataEntiteList, validationsEntite, realisesSousEntitesList, validationSousEntites, sousEntitesStringList):
        kList = []
        for i in range(start - 1, end - 1):
            index = dataEntite[i]["numero"] - 1
            kDoc = {
                    "numero": dataEntite[i]["numero"],
                    "reference": dataEntite[i]["reference"],
                    "intitule": dataEntite[i]["intitule"],
                    "processus": dataEntite[i]["processus"],
                    "unite": dataEntite[i]["unite"],
                    "type": dataEntite[i]["type"],
                    "realise": dataRealise[index],
                    "dataJan": dataEntiteList[index][1],
                    "dataFeb": dataEntiteList[index][2],
                    "dataMar": dataEntiteList[index][3],
                    "dataApr": dataEntiteList[index][4],
                    "dataMay": dataEntiteList[index][5],
                    "dataJun": dataEntiteList[index][6],
                    "dataJul": dataEntiteList[index][7],
                    "dataAug": dataEntiteList[index][8],
                    "dataSep": dataEntiteList[index][9],
                    "dataOct": dataEntiteList[index][10],
                    "dataNov": dataEntiteList[index][11],
                    "dataDec": dataEntiteList[index][12],
                    "allValidationsList": [realiseValidationEntite[index], validationsEntite[index][1], validationsEntite[index][2], validationsEntite[index][3], validationsEntite[index][4], validationsEntite[index][5], validationsEntite[index][6], validationsEntite[index][7], validationsEntite[index][8], validationsEntite[index][9], validationsEntite[index][10], validationsEntite[index][11], validationsEntite[index][12]]
                }
            if len(sousEntitesStringList) != 0:
                for sousEntite in sousEntitesStringList:
                    kDoc[f"sousEntite{sousEntitesStringList.index(sousEntite)}"] = realisesSousEntitesList[sousEntitesStringList.index(sousEntite)][i]
                    kDoc["allValidationsList"].append(validationSousEntites[sousEntitesStringList.index(sousEntite)][i])
            kList.append(kDoc)
        return kList

    def getDataEntite(self, idEntite, annee):
        id = f"{idEntite}_{annee}"
        response = supabase.table('DataIndicateur').select("*").eq("id", id).execute().data
        data = response[0]

        return data["valeurs"]

    def getValidationEntite(self, idEntite, annee):
        id = f"{idEntite}_{annee}"
        response = supabase.table('DataIndicateur').select("*").eq("id", id).execute().data
        data = response[0]

        return data["validations"]

    def post(self):
        args = request.get_json()
        try :

            annee = args["annee"]
            entiteId = args["entiteId"]
            sousEntites = args["sousEntites"]
            dataValeursListSousEntites = []
            dataValidationSousEntites = []

            ###################################

            kEntite = supabase.table("Entites").select("*").eq("id_entite", entiteId).execute()
            dataEntite = kEntite.data[0]

            filiale = dataEntite["filiale"]
            entiteName = dataEntite["nom_entite"]
            color = dataEntite["couleur"]

            dataValeurList = self.getDataEntite(entiteId, annee)

            dataValidationList = self.getValidationEntite(entiteId, annee)

            dataRealise = self.getRealise(dataValeurList)

            dataValidationRealise = self.getRealise(dataValidationList)

            #################################
            
            if len(sousEntites) != 0:
                for entity in sousEntites:
                    datasSousEntite = self.getDataEntite(entity, annee)
                    validationSousEntite = self.getValidationEntite(entity, annee)
                    realiseSousEntite = self.getRealise(datasSousEntite)
                    realiseValidationSousEntite = self.getRealise(validationSousEntite)
                    dataValeursListSousEntites.append(realiseSousEntite)
                    dataValidationSousEntites.append(realiseValidationSousEntite)


            #################################

            kIndicateur = supabase.table("Indicateurs_en").select("*").order("axe, index_ordering, reference", desc=False).execute()
            dataEntite = kIndicateur.data

            ## Général

            allRows = self.getJson(1,288,dataEntite,dataRealise, dataValidationRealise, dataValeurList, dataValidationList, dataValeursListSousEntites, dataValidationSousEntites, sousEntites)

            return {
                "entreprise": "SIFCA Group",
                "filiale": f"{filiale}",
                "entite": f"{entiteName}",
                "annee": annee,
                "color":color,
                "data": allRows
            }
        except Exception as e :
            print(e)
            return make_response({"status":False},404)
