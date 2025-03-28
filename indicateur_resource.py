
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

        dataValeurList = readDataJson(entite,f"{entite}_data_{annee}.json")
        dataValidationList = readDataJson(entite, f"{entite}_validation_{annee}.json")


        return {"entite":entite,"annee":annee,"valeurs":dataValeurList,"validations": dataValidationList}

class UpdateDataEntiteIndicateur(Resource):
    # Mise à jour des données indicateurs
    def post(self):
        try:
            args = request.get_json()

            annee = args["annee"]
            entite = args["entite"]
            colonne = args["colonne"]
            ligne = args["ligne"]
            valeur = args["valeur"]
            type = args["type"]
            formule = args["formule"]

            id = f"{entite}_{annee}"
            idNextYear = f"{entite}_{annee + 1}"
            
            try:
                responseListEcart = supabase.table('DataIndicateur').select("ecarts").eq("id", id).execute().data
                responseListEcartNextYear = supabase.table('DataIndicateur').select("ecarts").eq("id", idNextYear).execute().data
                responseListAxesEnjeu = supabase.table('Indicateurs').select("axe, enjeu").order("numero",desc= False).execute().data
            except Exception as e:
                return {"status": False, "message":f"Erreur lors de l'acces: {str(e)}"}, 500

            dicTemp = responseListEcart[0]
            listEcart = dicTemp['ecarts']
            dicTemp = responseListEcartNextYear[0]
            listEcartNextYear = dicTemp['ecarts']
            listAxes = []
            listEnjeux = []

            try:
                dataValeurListN1 = readDataJson(entite,f"{entite}_data_{annee}.json")
                dataValeurListN2 = readDataJson(entite,f"{entite}_data_{annee - 1}.json")
                dataValeurListN3 = readDataJson(entite, f"{entite}_data_{annee + 1}.json")
                dataValidationList = readDataJson(entite, f"{entite}_validation_{annee}.json")
            except FileNotFoundError as e:
                return {"status": False, "message":f"erreur: {str(e)}"}, 500
            
            try:
                isValide = dataValidationList[ligne][colonne]
                realiseLastYear = dataValeurListN2[ligne][0]
                realiseNextYear = dataValeurListN3[ligne][0]

                dataValeurListN1_copy = copy.deepcopy(dataValeurListN1)
                
                if isValide == True:
                    return {"status": False, "message": "La donnée est déja validée"}

                dataValeurListN1_copy[ligne][colonne] = valeur

                if type == "Primaire":
                    if formule == "Somme":
                        listTemp = copy.deepcopy(dataValeurListN1_copy[ligne])
                        listCalcul = listTemp[1:]
                        sommeList = formuleSomme(listCalcul)
                        if sommeList is not None:
                            dataValeurListN1_copy[ligne][0] = sommeList
                            if realiseLastYear is not None and realiseLastYear != 0:  # Ajout de la vérification != 0
                                dataEcart = ((realiseLastYear - sommeList) / realiseLastYear) * 100
                                listEcart[ligne] = dataEcart
                        else: 
                            if realiseNextYear is not None:
                                dataEcart = ((valeur - realiseNextYear) / valeur) * 100 if valeur != 0 else 0  # Protection division par zéro
                                listEcartNextYear[ligne] = dataEcart

                    elif formule == "Dernier mois renseigné":
                        listTemp = copy.deepcopy(dataValeurListN1_copy[ligne])
                        listCalcul = listTemp[1:]
                        dernierMoisList = formuleDernierMois(listCalcul)
                        if dernierMoisList is not None:
                            dataValeurListN1_copy[ligne][0] = dernierMoisList
                            if realiseLastYear is not None and realiseLastYear != 0:
                                dataEcart = ((realiseLastYear - dernierMoisList) / realiseLastYear) * 100
                                listEcart[ligne] = dataEcart
                        else: 
                            if realiseNextYear is not None:
                                dataEcart = ((valeur - realiseNextYear) / valeur) * 100 if valeur != 0 else 0
                                listEcartNextYear[ligne] = dataEcart

                    elif formule == "Moyenne":
                        listTemp = copy.deepcopy(dataValeurListN1_copy[ligne])
                        listCalcul = listTemp[1:]
                        moyenneList = formuleMoyenne(listCalcul)
                        if moyenneList is not None:
                            dataValeurListN1_copy[ligne][0] = moyenneList
                            if realiseLastYear is not None and realiseLastYear != 0:
                                dataEcart = ((realiseLastYear - moyenneList) / realiseLastYear) * 100
                                listEcart[ligne] = dataEcart
                        else: 
                            if realiseNextYear is not None:
                                dataEcart = ((valeur - realiseNextYear) / valeur) * 100 if valeur != 0 else 0
                                listEcartNextYear[ligne] = dataEcart

                # Formule Colonne ligne calculés
                for index in calculated_keys:
                    dataMapEcart = ecartCalculatedKeys(index, dataValeurListN1_copy, dataValeurListN2, dataValeurListN3)
                    dataRow = formuleCalcules(index, dataValeurListN1_copy, dataValeurListN2)

                    # Vérification que dataMapEcart n'est pas None avant accès
                    if dataMapEcart is not None:
                        if dataValeurListN1[index - 1][0] is not None and dataValeurListN2[index - 1][0] is not None:
                            listEcart[index - 1] = dataMapEcart.get("completedYear")  # Utilisation de get pour éviter KeyError

                        if dataValeurListN1_copy[index - 1][0] is not None and dataValeurListN3[index - 1][0] is not None:
                            listEcartNextYear[index - 1] = dataMapEcart.get("completedNextYear")

                    if dataRow is not None:
                        dataValeurListN1_copy[index - 1] = dataRow
                
                for index in test_indicators_keys:
                    dataRow = testIndicatorsFormulas(index, dataValeurListN1_copy, dataValeurListN2)
                    if dataRow is not None:
                        dataValeurListN1_copy[index - 1] = dataRow

                # Calcul de la performance Globale
                globalPerfData = PerformGlobal(listEcart)
                globalPerfDataNextYear = PerformGlobal(listEcartNextYear)

                def extract_data(response_list, list_ecart, value):
                    """Extracts data from response_list based on value and calculates average."""
                    result_list = []
                    list_index = indexes_by(response_list, value=value)
                    for index_list in list_index:
                        temp_list = []
                        for index in index_list:
                            temp_list.append(list_ecart[index])
                        result_list.append(temp_list)
                    for index, item in enumerate(result_list):
                        l = []
                        count = 0
                        for data in item:
                            if data is not None:
                                l.append(data)
                                count += 1
                        if l:
                            result_list[index] = sum(l) / count
                        else:
                            result_list[index] = None
                    return result_list

                resultlistAxes = extract_data(responseListAxesEnjeu, listEcart, "axe")
                listAxes = [100 if x is None else x for x in resultlistAxes[1:]]
                resultlistEnjeux = extract_data(responseListAxesEnjeu, listEcart, "enjeu")
                listEnjeux = [100 if x is None else x for x in resultlistEnjeux[1:]]

                resultlistAxesNextYear = extract_data(responseListAxesEnjeu, listEcartNextYear, "axe")
                listAxesNextYear = [100 if x is None else x for x in resultlistAxesNextYear[1:]]
                resultlistEnjeuxNextYear = extract_data(responseListAxesEnjeu, listEcartNextYear, "enjeu")
                listEnjeuxNextYear = [100 if x is None else x for x in resultlistEnjeuxNextYear[1:]]
            except (IndexError, KeyError) as e:
                return {"status": False, "message": f"Erreur:{str(e)}"}, 500
            
            try:
                supabase.table('Performance').update({'performs_piliers': listAxes}).eq('id', id).execute()
                supabase.table('Performance').update({'performs_enjeux': listEnjeux}).eq('id', id).execute()
                supabase.table('Performance').update({'performs_global': globalPerfData}).eq('id', id).execute()
                supabase.table('Performance').update({'performs_global': globalPerfDataNextYear}).eq('id', idNextYear).execute()

                supabase.table('Performance').update({'performs_piliers': listAxesNextYear}).eq('id', idNextYear).execute()
                supabase.table('Performance').update({'performs_enjeux': listEnjeuxNextYear}).eq('id', idNextYear).execute()

                saveDataInJson(dataValeurListN1_copy, entite, f"{entite}_data_{annee}.json")
                supabase.table('DataIndicateur').update({'valeurs': dataValeurListN1_copy}).eq('id', id).execute()
                supabase.table('DataIndicateur').update({"ecarts": listEcart}).eq('id', id).execute()
                supabase.table('DataIndicateur').update({"ecarts": listEcartNextYear}).eq('id', idNextYear).execute()
            except Exception as e:
                return {"status": False, "message": f"Erreur lors de la mise a jour: {str(e)}"}, 500
            
            return {"status": True}
        except Exception as e:
            return {"status": False, "message": f"Une erreur inattendue s'est produite: {str(e)}"}, 500
class DeleteDataEntiteIndicateur(Resource):
    # Mise à jour des données indicateurs
    def post(self):
        args = request.get_json()

        annee = args["annee"]
        entite = args["entite"]
        colonne = args["colonne"]
        ligne = args["ligne"]
        type = args["type"]
        formule = args["formule"]

        id = f"{entite}_{annee}"
        idNextYear = f"{entite}_{annee + 1}"

        responseListEcart = supabase.table('DataIndicateur').select("ecarts").eq("id", id).execute().data
        responseListEcartNextYear = supabase.table('DataIndicateur').select("ecarts").eq("id", idNextYear).execute().data
        responseListAxesEnjeu = supabase.table('Indicateurs').select("axe, enjeu").order("numero",desc= False).execute().data

        dicTemp = responseListEcart[0]
        listEcart = dicTemp['ecarts']
        dicTemp = responseListEcartNextYear[0]
        listEcartNextYear = dicTemp['ecarts']

        # L'ecart est determine a partir du realise du mois actuel (cumul jusqu'au mois actuel) et le realise de l'annee derniere

        # indicesListAxes = [16, 46, 206, 221, 280]
        # indicesListEnjeux = [16, 21, 27, 34, 46, 181, 200, 206, 221, 245, 262, 280]

        listAxes = []
        listEnjeux = []

        dataValeurListN1 = readDataJson(entite,f"{entite}_data_{annee}.json")
        dataValeurListN2 = readDataJson(entite,f"{entite}_data_{annee - 1}.json")
        dataValeurListN3 = readDataJson(entite, f"{entite}_data_{annee + 1}.json")
        dataValidationList = readDataJson(entite, f"{entite}_validation_{annee}.json")

        isValide = dataValidationList[ligne][colonne]
        realiseLastYear = dataValeurListN2[ligne][0]
        realiseNextYear = dataValeurListN3[ligne][0]
        dataValeurListN1_copy = copy.deepcopy(dataValeurListN1)
        if isValide == True :
            return  {"status":False,"message":"La donnée est déja validée"}

        dataValeurListN1_copy[ligne][colonne] = valeur

        # Formule Colonne "Réalisé" ligne primaire

        if type == "Primaire" :

            if formule == "Somme" :
                listTemp = copy.deepcopy(dataValeurListN1[ligne])
                listCalcul = listTemp[1:]
                if all(x is None for x in listCalcul):
                    sommeList = None
                    listEcart[ligne] = None
                    listEcartNextYear[ligne] = None
                else:
                    sommeList = formuleSomme(listCalcul)
                    if realiseLastYear != None:
                        dataEcart = ((realiseLastYear - sommeList) / realiseLastYear) * 100
                        listEcart[ligne] = dataEcart
                dataValeurListN1[ligne][0] = sommeList

            elif formule == "Dernier mois renseigné" :
                listTemp = copy.deepcopy(dataValeurListN1[ligne])
                listCalcul = listTemp[1:]
                if all(x is None for x in listCalcul):
                    dernierMoisList = None
                    listEcart[ligne] = None
                    listEcartNextYear[ligne] = None
                else:
                    dernierMoisList = formuleDernierMois(listCalcul)
                    if realiseLastYear != None:
                        dataEcart = ((realiseLastYear - dernierMoisList) / realiseLastYear) * 100
                        listEcart[ligne] = dataEcart
                dataValeurListN1[ligne][0] = dernierMoisList

            elif formule == "Moyenne" :
                listTemp = copy.deepcopy(dataValeurListN1[ligne])
                listCalcul = listTemp[1:]
                if all(x is None for x in listCalcul):
                    moyenneList = None
                    listEcart[ligne] = None
                    listEcartNextYear[ligne] = None
                else:
                    moyenneList = formuleMoyenne(listCalcul)
                    if realiseLastYear != None:
                        dataEcart = ((realiseLastYear - moyenneList) / realiseLastYear) * 100
                        listEcart[ligne] = dataEcart
                dataValeurListN1[ligne][0] = moyenneList

        # Formule Colonne ligne calculés
        for index in calculated_keys :
            dataMapEcart = {}
            dataRow = formuleCalcules(index, dataValeurListN1, dataValeurListN2)
            dataMapEcart = ecartCalculatedKeys(index, dataValeurListN1, realiseLastYear, realiseNextYear)

            if dataRow != None:
                dataValeurListN1[index - 1] = dataRow

            if (dataValeurListN1[index - 1][0] is not None and dataValeurListN2[index - 1][0] is not None and dataMapEcart is not None):
                 listEcart[index - 1] = dataMapEcart["completedYear"]
            else:
                listEcart[index - 1] = None

            if (dataValeurListN1[index - 1][0] is not None and  dataValeurListN3[index - 1][0] is not None and  dataMapEcart is not None):
                listEcartNextYear[index - 1] = dataMapEcart["completedNextYear"]
            else:
                listEcartNextYear[index - 1] = None
        
        for index in test_indicators_keys:
            dataRow = testIndicatorsFormulas(index, dataValeurListN1, dataValeurListN2)
            if dataRow != None:
                dataValeurListN1[index - 1] = dataRow

        #Calcul de la performance Globale
        globalPerfData = PerformGlobal(listEcart)
        globalPerfDataNextYear = PerformGlobal(listEcartNextYear)

        def extract_data(response_list, list_ecart, value):
            """Extracts data from response_list based on value and calculates average."""
            result_list = []
            list_index = indexes_by(response_list, value=value)
            for index_list in list_index:
                temp_list = []
                for index in index_list:
                    temp_list.append(list_ecart[index])
                result_list.append(temp_list)
            for index, item in enumerate(result_list):
                l = []
                count = 0
                for data in item:
                    if data != None:
                        l.append(data)
                        count += 1
                if l != []:
                    result_list[index] = sum(l) / count
                else:
                    result_list[index] = None
            return result_list

        resultlistAxes = extract_data(responseListAxesEnjeu, listEcart, "axe")
        listAxes = [100 if x is None else x for x in resultlistAxes[1:]]
        resultlistEnjeux = extract_data(responseListAxesEnjeu, listEcart, "enjeu")
        listEnjeux = [100 if x is None else x for x in resultlistEnjeux[1:]]

        resultlistAxesNextYear = extract_data(responseListAxesEnjeu, listEcartNextYear, "axe")
        listAxesNextYear = [100 if x is None else x for x in resultlistAxesNextYear[1:]]
        resultlistEnjeuxNextYear = extract_data(responseListAxesEnjeu, listEcartNextYear, "enjeu")
        listEnjeuxNextYear = [100 if x is None else x for x in resultlistEnjeuxNextYear[1:]]

        
        supabase.table('Performance').update({'performs_piliers': listAxes}).eq('id',id).execute()
        supabase.table('Performance').update({'performs_enjeux': listEnjeux}).eq('id',id).execute()
        supabase.table('Performance').update({'performs_global': globalPerfData}).eq('id', id).execute()
        supabase.table('Performance').update({'performs_global': globalPerfDataNextYear}).eq('id', idNextYear).execute()

        supabase.table('Performance').update({'performs_piliers': listAxesNextYear}).eq('id',idNextYear).execute()
        supabase.table('Performance').update({'performs_enjeux': listEnjeuxNextYear}).eq('id',idNextYear).execute()

        saveDataInJson(dataValeurListN1_copy,entite,f"{entite}_data_{annee}.json")
        supabase.table('DataIndicateur').update({'valeurs': dataValeurListN1_copy}).eq('id',id).execute()
        supabase.table('DataIndicateur').update({"ecarts" : listEcart}).eq('id',id).execute()
        supabase.table('DataIndicateur').update({"ecarts" : listEcartNextYear}).eq('id',idNextYear).execute()

        return {"status":True}


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
    # Mise à jour des données indicateurs
    def post(self):
        args = request.get_json()

        annee = args["annee"]
        entite = args["entite"]
        colonne = args["colonne"]
        ligne = args["ligne"]
        valide = args["valide"]

        id = f"{entite}_{annee}"


        dataValidationsList = readDataJson(entite,f"{entite}_validation_{annee}.json")
        dataValidationsList[ligne][colonne] = valide
        saveDataInJson(dataValidationsList,entite,f"{entite}_validation_{annee}.json")
        supabase.table('DataIndicateur').update({'validations': dataValidationsList}).eq('id', id).execute()

        return {"status":True}



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
