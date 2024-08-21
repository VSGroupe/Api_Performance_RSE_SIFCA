from flask import Flask, request, make_response
from flask_cors import CORS
from flask_restful import Api, Resource

from consolidation_ressource import ScriptConsolidation
from indicateur_resource import ChangeStatusEntityIndic, DeleteDataEntiteIndicateur, EntiteExportENAllData, GetDataEntiteIndicateur, UpdateDataEntiteIndicateur, UpdateAllDataEntiteIndicateur, UpdateDataInApiDB, \
    UpdateValidationEntiteIndicateur, EntiteExportAllData, UpdateDataEntiteIndicateurFromSupabase
from suivi_indicateur import SuiviDataIndicateur

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 15 * 1024 * 1024

api = Api(app)

# CORS(app, resources={
#     r"/*": {
#         "origins": ["https://sifca-performance-rse.web.app/", "http://localhost:49430", "http://localhost:51938"]
#     }
# })
CORS(app, resources={r"/*": {"origins": "*"}})


class HelloWorld(Resource):
    def get(self):
        return {'version': '1.2.0'}

class EntiteAccueil(Resource):
    def post(self):
        return {
            "entite":"sucrivoire",
            "entiteName":"SUCRIVOIRE",
            "annee":2023,
            "suivi":[
                {
                    "axe":"Axe 1",
                    "nombre":200,
                    "collecte":100,
                    "ordre":1
                },
                {
                    "axe": "Axe 2",
                    "nombre": 200,
                    "collecte": 50,
                    "ordre": 2
                },
                {
                    "axe": "Axe 3",
                    "nombre": 200,
                    "collecte": 10,
                    "ordre": 3
                },
                {
                    "axe": "Axe 1",
                    "nombre": 200,
                    "collecte": 150,
                    "ordre": 4
                },

            ],
            "contriuteurs":[
                {
                    "nom":"Fabrice HOUESSOU",
                    "email":"fabricehouessou@gmail.com",
                    "entité":"Sucrivore-Siège",
                    "filiale":"SUCRIVOIRE"
                }
            ],
            "comparaison":[
                {
                    "entite":"Entite 1",
                    "progres1":55,
                    "progres2":60
                },
                {
                    "entite": "Entite 1",
                    "progres1": 55,
                    "progres2": 60
                },
                {
                    "entite": "Entite 1",
                    "progres1": 55,
                    "progres2": 60
                },
                {
                    "entite": "Entite 1",
                    "progres1": 55,
                    "progres2": 60
                }
            ],
        }

class EntiteSuivi(Resource):
    def get(self):
        return {'version': '1.2.0'}

class EntitePerformance(Resource):
    def get(self):
        return {'version': '1.2.0'}

class EntiteHistorique(Resource):
    def get(self):
        return {'version': '1.2.0'}

api.add_resource(HelloWorld, '/')

api.add_resource(GetDataEntiteIndicateur, '/data-entite-indicateur/get')
api.add_resource(UpdateDataEntiteIndicateur, '/data-entite-indicateur/update-data')
api.add_resource(DeleteDataEntiteIndicateur, '/data-entite-indicateur/delete-data')
api.add_resource(UpdateAllDataEntiteIndicateur, '/data-entite-indicateur/update-all-data')
api.add_resource(UpdateDataEntiteIndicateurFromSupabase, '/data-entite-indicateur/update-data-from-supabase')
api.add_resource(UpdateValidationEntiteIndicateur, '/data-entite-indicateur/update-validation')
api.add_resource(EntiteExportAllData, '/data-entite-indicateur/export-all-data')
api.add_resource(EntiteExportENAllData, '/data-entite-indicateur/export-en-all-data')

api.add_resource(ScriptConsolidation, '/data-entite-indicateur/consolidation')
api.add_resource(SuiviDataIndicateur, '/data-entite-suivi')
#api.add_resource(ComputePerformsEntite, '/data-entite-indicateur/compute-performs')
api.add_resource(ChangeStatusEntityIndic, '/data-entite-indicateur/change-entity-indic-status')
api.add_resource(UpdateDataInApiDB, '/data-entite-indicateur/update-api-bd')

if __name__ == '__main__':
    context = ('ssl/cert.pem', 'ssl/key.pem')
    app.run() #debug=True,port=4444,host="0.0.0.0"
