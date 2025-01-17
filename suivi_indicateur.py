from dbkeys import supabase
from utils_data import readDataJson
from utils import checkProcessValue, indexes_by
from flask_restful import Resource
from flask import request, make_response


class SuiviDataIndicateur(Resource):

    def updateSuiviIndicateur(self,entiteId, annee, processus, numeroLigne, colonne):

        try:
            processDic = {
                "Agricole": "Agricole",
                "Finances": "Finances",
                "Juridique": "Juridique",
                "Achats": "Achats",
                "Emissions": "Emissions",
                "Usine": "Usine",
                "Infrastructures": "Infrastructures",
                "Médecin": "Médecin",
                "Ressources Humaines": "Ressources Humaines",
                "Ressources Humaines / Juridique": "Ressources Humaines / Juridique",
                "Développement Durable": "Développement Durable",
                "Gestion des Stocks / Logistique": "Gestion des Stocks / Logistique",
                
                "Agricultural": "Agricole",
                "Sustainable development": "Développement Durable",
                "Finance": "Finances",
                "Purchases": "Achats",
                "Legal": "Juridique",
                "Human ressources": "Ressources Humaines",
                "Doctor": "Médecin",
                "Infrastructure": "Infrastructures",
                "Human ressources / Legal": "Ressources Humaines / Juridique",
                "Stock Management / Logistics": "Gestion des Stocks / Logistique",
                "Emissions": "Emissions",
                "Factory": "Usine"
                }
            processus = processDic[processus]
            suiviMap = {"indicateur_total": 288, "indicateur_valides": 0, "indicateur_collectes": 0,
                        "suivi_mensuel": {},"suivi_axe": {}, "suivi_processus": {}}
            ########################
            entiteList = supabase.table('Entites').select("nom_entite").eq("id_entite", entiteId).execute().data
            nomEntite = entiteList[0]["nom_entite"]
            print("suivi de " f"{entiteId}")

            responseListAxesEnjeu = supabase.table('Indicateurs').select("axe, enjeu, processus").order("numero",desc= False).execute().data
            listAxesIndex = indexes_by(responseListAxesEnjeu, value= "axe")

            totalElementInAxe = []
            for listIndex in listAxesIndex[1:]:
                totalElementInAxe.append(len(listIndex))

            idSuivi = f"{entiteId}_{annee}"
            isExist = supabase.table('SuiviData').select("*").eq("id_suivi", idSuivi).execute().data

            if isExist == []:
                supabase.table('SuiviData').insert({
                    "id_suivi": idSuivi, "annee": annee,
                    "id_entite": entiteId, "nom_entite": nomEntite,
                }).execute()

            ########################

            dataValeurList = readDataJson(entiteId, f"{entiteId}_data_{annee}.json")
            dataValidationList = readDataJson(entiteId, f"{entiteId}_validation_{annee}.json")

            # Suivi par processus
            listProcessus = supabase.table('Indicateurs').select("processus").order('numero', desc=False).execute().data

            value = checkProcessValue(numeroLigne, listProcessus)
            #print(value)

            if(value):
                suiviDicProcessus = isExist[0]['suivi_processus']
                indexesProcessus = []

                for index, dico in enumerate(listProcessus):
                    if dico.get('processus') == f'{processus}':
                        indexesProcessus.append(index)
                dataProcessSuivi = 0
                for index in indexesProcessus:
                    if dataValeurList[index][colonne] != None:
                        dataProcessSuivi += 1
                if suiviDicProcessus[f'{processus}'][f'{colonne}'] != dataProcessSuivi:
                    suiviDicProcessus[f'{processus}'][f'{colonne}'] = dataProcessSuivi
                suiviMap["suivi_processus"] = suiviDicProcessus
                #print(suiviDicProcessus)
            ####################

            axesMap = {}

            dataAxe1 = []
            for rowData in dataValeurList:
                # start = 16 -1
                # end = 46
                if dataValeurList.index(rowData) in listAxesIndex[1]:
                    kData = rowData[0]
                    if kData != None:
                        dataAxe1.append(kData)
                    axesMap["axe_1"] = {
                        "indicateur_total": totalElementInAxe[0],
                        "indicateur_collectes": len(dataAxe1)
                    }
            if not dataAxe1:
                axesMap["axe_1"] = {
                    "indicateur_total": totalElementInAxe[0],
                    "indicateur_collectes": 0
                }

            dataAxe2 = []
            for rowData in dataValeurList:
                # start = 47 -1
                # end = 206
                if dataValeurList.index(rowData) in listAxesIndex[2]:
                    kData = rowData[0]
                    if kData != None:
                        dataAxe2.append(kData)
                    axesMap["axe_2"] = {
                        "indicateur_total": totalElementInAxe[1],
                        "indicateur_collectes": len(dataAxe2)
                    }
            if not dataAxe2:
                axesMap["axe_2"] = {
                    "indicateur_total": totalElementInAxe[1],
                    "indicateur_collectes": 0
                }

            dataAxe3 = []
            for rowData in dataValeurList:
                # start = 207 -1
                # end = 221
                if dataValeurList.index(rowData) in listAxesIndex[3]:
                    kData = rowData[0]
                    if kData != None:
                        dataAxe3.append(kData)
                    axesMap["axe_3"] = {
                        "indicateur_total": totalElementInAxe[2],
                        "indicateur_collectes": len(dataAxe3)
                    }
            if not dataAxe3:
                axesMap["axe_3"] = {
                    "indicateur_total": totalElementInAxe[2],
                    "indicateur_collectes": 0
                }

            dataAxe4 = []
            for rowData in dataValeurList:
                # start = 222 -1
                # end = 280
                if dataValeurList.index(rowData) in listAxesIndex[1]:
                    kData = rowData[0]
                    if kData != None:
                        dataAxe4.append(kData)
                    axesMap["axe_4"] = {
                        "indicateur_total": totalElementInAxe[3],
                        "indicateur_collectes": len(dataAxe4)
                    }
            if not dataAxe4:
                axesMap["axe_4"] = {
                    "indicateur_total": totalElementInAxe[3],
                    "indicateur_collectes": 0
                }

            suiviDataRealise = []

            for rowData in dataValeurList:
                kData = rowData[0]
                if kData != None:
                    suiviDataRealise.append(kData)

            suiviValidationRealise = []

            for rowData in dataValidationList:
                kValidation = rowData[0]
                if kValidation == True:
                    suiviValidationRealise.append(kValidation)

            suiviMensuel = {}
            for mois in range(1, 13):
                mapMois = {
                    "indicateur_valides": 0,
                    "indicateur_collectes": 0
                }
                ksuiviDataRealise = []

                for rowData in dataValeurList:
                    kData = rowData[mois]
                    if kData != None:
                        ksuiviDataRealise.append(kData)

                ksuiviValidationRealise = []

                for rowData in dataValidationList:
                    kValidation = rowData[mois]
                    if kValidation == True:
                        ksuiviValidationRealise.append(kValidation)

                mapMois["indicateur_collectes"] = len(ksuiviDataRealise)
                mapMois["indicateur_valides"] = len(ksuiviValidationRealise)

                suiviMensuel[f"{mois}"] = mapMois
            print(f'{entiteId}: {axesMap}')
            suiviMap["indicateur_total"] = len(dataValeurList)
            suiviMap["indicateur_collectes"] = len(suiviDataRealise)
            suiviMap["indicateur_valides"] = len(suiviValidationRealise)
            suiviMap["suivi_mensuel"] = suiviMensuel
            suiviMap["suivi_axe"] = axesMap

            supabase.table('SuiviData').update(suiviMap).eq('id_suivi', idSuivi).execute()

            return True
        except:
            return False

    def post(self):
        args = request.get_json()

        annee = args["annee"]
        entite = args["entite"]
        processus = args["processus"]
        numeroLigne = args["numeroLigne"]
        colonne = args["colonne"]

        self.updateSuiviIndicateur(entite,annee, processus, numeroLigne, colonne)


        return {"status":True}