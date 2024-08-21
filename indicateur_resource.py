from flask_restful import Resource
from flask import request, make_response
import copy
from data import calculated_keys, test_indicators_keys
from dbkeys import supabase
from utils import formuleCalcules, formuleSomme, formuleDernierMois, formuleMoyenne, PerformGlobal, extraire_chiffres, indexes_by, testIndicatorsFormulas
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
        args = request.get_json()

        annee = args["annee"]
        entite = args["entite"]
        colonne = args["colonne"]
        ligne = args["ligne"]
        valeur = args["valeur"]
        type = args["type"]
        formule = args["formule"]

        id = f"{entite}_{annee}"

        responseListEcart = supabase.table('DataIndicateur').select("ecarts").eq("id", id).execute().data
        responseListAxesEnjeu = supabase.table('Indicateurs').select("axe, enjeu").order("numero",desc= False).execute().data

        dicTemp = responseListEcart[0]
        listEcart = dicTemp['ecarts']

        # L'ecart est determine a partir du realise du mois actuel (cumul jusqu'au mois actuel) et le realise de l'annee derniere

        # indicesListAxes = [16, 46, 206, 221, 280]
        # indicesListEnjeux = [16, 21, 27, 34, 46, 181, 200, 206, 221, 245, 262, 280]

        listAxes = []
        listEnjeux = []

        dataValeurListN1 = readDataJson(entite,f"{entite}_data_{annee}.json")
        dataValeurListN2 = readDataJson(entite,f"{entite}_data_{annee - 1}.json")
        dataValidationList = readDataJson(entite, f"{entite}_validation_{annee}.json")

        isValide = dataValidationList[ligne][colonne]
        realiseLastYear = dataValeurListN2[ligne][0]

        if isValide == True :
            return  {"status":False,"message":"La donnée est déja validée"}

        dataValeurListN1[ligne][colonne] = valeur

        # Formule Colonne "Réalisé" ligne primaire

        if type == "Primaire" :

            if formule == "Somme" :
                listTemp = copy.deepcopy(dataValeurListN1[ligne])
                listCalcul = listTemp[1:]
                sommeList = formuleSomme(listCalcul)
                if sommeList != None:
                    dataValeurListN1[ligne][0] = sommeList
                    if realiseLastYear != None:
                        dataEcart = ((realiseLastYear - sommeList) / realiseLastYear) * 100
                        listEcart[ligne] = dataEcart

            elif formule == "Dernier mois renseigné" :
                listTemp = copy.deepcopy(dataValeurListN1[ligne])
                listCalcul = listTemp[1:]
                dernierMoisList = formuleDernierMois(listCalcul)
                if dernierMoisList != None:
                    dataValeurListN1[ligne][0] = dernierMoisList
                    if realiseLastYear != None:
                        dataEcart = ((realiseLastYear - dernierMoisList) / realiseLastYear) * 100
                        listEcart[ligne] = dataEcart

            elif formule == "Moyenne" :
                listTemp = copy.deepcopy(dataValeurListN1[ligne])
                listCalcul = listTemp[1:]
                moyenneList = formuleMoyenne(listCalcul)
                if moyenneList != None:
                    dataValeurListN1[ligne][0] = moyenneList
                    if realiseLastYear != None:
                        dataEcart = ((realiseLastYear - moyenneList) / realiseLastYear) * 100
                        listEcart[ligne] = dataEcart

        # Formule Colonne ligne calculés
        for index in calculated_keys :

            dataRow = formuleCalcules(index, dataValeurListN1, dataValeurListN2)
            if dataRow != None:
                dataValeurListN1[index - 1] = dataRow
        
        for index in test_indicators_keys:
            dataRow = testIndicatorsFormulas(index, dataValeurListN1, dataValeurListN2)
            if dataRow != None:
                dataValeurListN1[index - 1] = dataRow

        #Calcul de la performance Globale
        globalPerfData = PerformGlobal(listEcart)

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

        
        supabase.table('Performance').update({'performs_piliers': listAxes}).eq('id',id).execute()
        supabase.table('Performance').update({'performs_enjeux': listEnjeux}).eq('id',id).execute()
        supabase.table('Performance').update({'performs_global': globalPerfData}).eq('id', id).execute()

        saveDataInJson(dataValeurListN1,entite,f"{entite}_data_{annee}.json")
        supabase.table('DataIndicateur').update({'valeurs': dataValeurListN1}).eq('id',id).execute()
        supabase.table('DataIndicateur').update({"ecarts" : listEcart}).eq('id',id).execute()

        return {"status":True}

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

        responseListEcart = supabase.table('DataIndicateur').select("ecarts").eq("id", id).execute().data
        responseListAxesEnjeu = supabase.table('Indicateurs').select("axe, enjeu").order("numero",desc= False).execute().data

        dicTemp = responseListEcart[0]
        listEcart = dicTemp['ecarts']

        # L'ecart est determine a partir du realise du mois actuel (cumul jusqu'au mois actuel) et le realise de l'annee derniere

        # indicesListAxes = [16, 46, 206, 221, 280]
        # indicesListEnjeux = [16, 21, 27, 34, 46, 181, 200, 206, 221, 245, 262, 280]

        listAxes = []
        listEnjeux = []

        dataValeurListN1 = readDataJson(entite,f"{entite}_data_{annee}.json")
        dataValeurListN2 = readDataJson(entite,f"{entite}_data_{annee - 1}.json")
        dataValidationList = readDataJson(entite, f"{entite}_validation_{annee}.json")

        isValide = dataValidationList[ligne][colonne]
        realiseLastYear = dataValeurListN2[ligne][0]

        if isValide == True :
            return  {"status":False,"message":"La donnée est déja validée"}

        dataValeurListN1[ligne][colonne] = None

        # Formule Colonne "Réalisé" ligne primaire

        if type == "Primaire" :

            if formule == "Somme" :
                listTemp = copy.deepcopy(dataValeurListN1[ligne])
                listCalcul = listTemp[1:]
                if all(x is None for x in listCalcul):
                    sommeList = None
                    listEcart[ligne] = None
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
                else:
                    moyenneList = formuleMoyenne(listCalcul)
                    if realiseLastYear != None:
                        dataEcart = ((realiseLastYear - moyenneList) / realiseLastYear) * 100
                        listEcart[ligne] = dataEcart
                dataValeurListN1[ligne][0] = moyenneList

        # Formule Colonne ligne calculés
        for index in calculated_keys :

            dataRow = formuleCalcules(index, dataValeurListN1)
            if dataRow != None:
                dataValeurListN1[index - 1] = dataRow
        
        for index in test_indicators_keys:
            dataRow = testIndicatorsFormulas(index, dataValeurListN1, dataValeurListN2)
            if dataRow != None:
                dataValeurListN1[index - 1] = dataRow

        #Calcul de la performance Globale
        globalPerfData = PerformGlobal(listEcart)

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

        
        supabase.table('Performance').update({'performs_piliers': listAxes}).eq('id',id).execute()
        supabase.table('Performance').update({'performs_enjeux': listEnjeux}).eq('id',id).execute()
        supabase.table('Performance').update({'performs_global': globalPerfData}).eq('id', id).execute()

        saveDataInJson(dataValeurListN1,entite,f"{entite}_data_{annee}.json")
        supabase.table('DataIndicateur').update({'valeurs': dataValeurListN1}).eq('id',id).execute()
        supabase.table('DataIndicateur').update({"ecarts" : listEcart}).eq('id',id).execute()

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
            dataListFromSupabase = supabase.table('DataIndicateur').select("valeurs").eq("id", idEntity).execute().data
            dataValeuListApi = readDataJson(entity, f"{entity}_data_2024.json")
            print(entity)
            dataValeuListApi = dataListFromSupabase[0]["valeurs"]
            saveDataInJson(dataValeuListApi, entity, f"{entity}_data_2024.json")
        

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

    def getJson(self,start,end,dataEntite,dataRealise, dataEntiteList, realisesSousEntitesList):
        kList = []
        for i in range(start - 1, end - 1):
            kDoc = {
                    "numero": dataEntite[i]["numero"], # i + 1
                    "reference": dataEntite[i]["reference"],
                    "intitule": dataEntite[i]["intitule"],
                    "unite": dataEntite[i]["unite"],
                    "realise": dataRealise[dataEntite[i]["numero"] -1],
                    "dataJan": dataEntiteList[dataEntite[i]["numero"] - 1][1],
                    "dataFeb": dataEntiteList[dataEntite[i]["numero"] - 1][2],
                    "dataMar": dataEntiteList[dataEntite[i]["numero"] - 1][3],
                    "dataApr": dataEntiteList[dataEntite[i]["numero"] - 1][4],
                    "dataMay": dataEntiteList[dataEntite[i]["numero"] - 1][5],
                    "dataJun": dataEntiteList[dataEntite[i]["numero"] - 1][6],
                    "dataJul": dataEntiteList[dataEntite[i]["numero"] - 1][7],
                    "dataAug": dataEntiteList[dataEntite[i]["numero"] - 1][8],
                    "dataSep": dataEntiteList[dataEntite[i]["numero"] - 1][9],
                    "dataOct": dataEntiteList[dataEntite[i]["numero"] - 1][10],
                    "dataNov": dataEntiteList[dataEntite[i]["numero"] - 1][11],
                    "dataDec": dataEntiteList[dataEntite[i]["numero"] - 1][12],
                }
            if len(realisesSousEntitesList) != 0:
                for sousEntite in realisesSousEntitesList:
                    kDoc[f"sousEntite{realisesSousEntitesList.index(sousEntite)}"] = realisesSousEntitesList[realisesSousEntitesList.index(sousEntite)][i]
            kList.append(kDoc)
        return kList

    def getDataEntite(self, idEntite, annee):
        id = f"{idEntite}_{annee}"
        response = supabase.table('DataIndicateur').select("*").eq("id", id).execute().data
        data = response[0]

        return data["valeurs"]

    def post(self):
        args = request.get_json()
        try :

            annee = args["annee"]
            entiteId = args["entiteId"]
            sousEntites = []
            dataValeursListSousEntites = []

            ###################################

            kEntite = supabase.table("Entites").select("*").eq("id_entite", entiteId).execute()
            dataEntite = kEntite.data[0]

            filiale = dataEntite["filiale"]
            entiteName = dataEntite["nom_entite"]
            color = dataEntite["couleur"]

            dataValeurList = self.getDataEntite(entiteId, annee)

            dataRealise = self.getRealise(dataValeurList)

            #################################
            
            if len(sousEntites) != 0:
                for entity in sousEntites:
                    datasSousEntite = self.getDataEntite(entity, annee)
                    realiseSousEntite = self.getRealise(datasSousEntite)
                    dataValeursListSousEntites.append(realiseSousEntite)


            #################################

            kIndicateur = supabase.table("Indicateurs").select("*").order("axe, index_ordering, reference", desc=False).execute()
            dataEntite = kIndicateur.data

            ## Général

            allRows = self.getJson(1,288,dataEntite,dataRealise, dataValeurList, dataValeursListSousEntites)

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

    def getJson(self,start,end,dataEntite,dataRealise, dataEntiteList, realisesSousEntitesList):
        kList = []
        for i in range(start - 1, end - 1):
            kDoc = {
                    "numero": dataEntite[i]["numero"],
                    "reference": dataEntite[i]["reference"],
                    "intitule": dataEntite[i]["intitule"],
                    "unite": dataEntite[i]["unite"],
                    "realise": dataRealise[dataEntite[i]["numero"] -1],
                    "dataJan": dataEntiteList[dataEntite[i]["numero"] - 1][1],
                    "dataFeb": dataEntiteList[dataEntite[i]["numero"] - 1][2],
                    "dataMar": dataEntiteList[dataEntite[i]["numero"] - 1][3],
                    "dataApr": dataEntiteList[dataEntite[i]["numero"] - 1][4],
                    "dataMay": dataEntiteList[dataEntite[i]["numero"] - 1][5],
                    "dataJun": dataEntiteList[dataEntite[i]["numero"] - 1][6],
                    "dataJul": dataEntiteList[dataEntite[i]["numero"] - 1][7],
                    "dataAug": dataEntiteList[dataEntite[i]["numero"] - 1][8],
                    "dataSep": dataEntiteList[dataEntite[i]["numero"] - 1][9],
                    "dataOct": dataEntiteList[dataEntite[i]["numero"] - 1][10],
                    "dataNov": dataEntiteList[dataEntite[i]["numero"] - 1][11],
                    "dataDec": dataEntiteList[dataEntite[i]["numero"] - 1][12],
                }
            if len(realisesSousEntitesList) != 0:
                for sousEntite in realisesSousEntitesList:
                    kDoc[f"sousEntite{realisesSousEntitesList.index(sousEntite)}"] = realisesSousEntitesList[realisesSousEntitesList.index(sousEntite)][i]
            kList.append(kDoc)
        return kList

    def getDataEntite(self, idEntite, annee):
        id = f"{idEntite}_{annee}"
        response = supabase.table('DataIndicateur').select("*").eq("id", id).execute().data
        data = response[0]

        return data["valeurs"]

    def post(self):
        args = request.get_json()
        try :

            annee = args["annee"]
            entiteId = args["entiteId"]
            sousEntites = []
            dataValeursListSousEntites = []

            ###################################

            kEntite = supabase.table("Entites").select("*").eq("id_entite", entiteId).execute()
            dataEntite = kEntite.data[0]

            filiale = dataEntite["filiale"]
            entiteName = dataEntite["nom_entite"]
            color = dataEntite["couleur"]

            dataValeurList = self.getDataEntite(entiteId, annee)

            dataRealise = self.getRealise(dataValeurList)

            #################################
            
            if len(sousEntites) != 0:
                for entity in sousEntites:
                    datasSousEntite = self.getDataEntite(entity, annee)
                    realiseSousEntite = self.getRealise(datasSousEntite)
                    dataValeursListSousEntites.append(realiseSousEntite)


            #################################

            kIndicateur = supabase.table("Indicateurs_en").select("*").order("axe, index_ordering, reference", desc=False).execute()
            dataEntite = kIndicateur.data

            ## Général

            allRows = self.getJson(1,288,dataEntite,dataRealise, dataValeurList, dataValeursListSousEntites)

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