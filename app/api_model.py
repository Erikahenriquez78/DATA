from datetime import date
from flask import Flask, jsonify, request
from google.cloud import bigquery
from google.oauth2 import service_account
from src.data_processing import *
import pandas as pd
import os
import pickle


os.chdir(os.path.dirname(__file__))

app = Flask(__name__)
app.config['DEBUG'] = False


# Cargar el DataFrame deportes_normalized desde el archivo
with open('models/deportes_normalized.pkl', 'rb') as f:
    deportes_normalized = pickle.load(f)

deportes = pd.read_csv('data/deportes.csv', index_col=0)
items = pd.read_csv('data/items.csv', index_col=0)


@app.route("/", methods=['GET'])
def hello():
    return "Bienvenido a la API del Grupo 5 - Desafío de Tripulaciones"

@app.route('/v1', methods=['GET'])
def v1():

    edad = int(request.args.get('edad', None))
    sexo = int(request.args.get('sexo', None))
    peso = float(request.args.get('peso', None))
    condicion = int(request.args.get('condicion', None)) # baja media alta
    objetivo = int(request.args.get('objetivo', None)) # suave medio intenso
    preferencias = request.args.get('preferencias', None) # listado deportes preferidos
    posicion = request.args.get('posicion', None) # [lat, lon]
    distancia = float(request.args.get('distancia', None)) # en km
    clima = int(request.args.get('clima', None)) # soleado nublado lluvioso
    temperatura = float(request.args.get('temperatura', None)) # ºC
    humedad = float(request.args.get('humedad', None))



    if edad is None or \
    sexo is None or \
    peso is None or \
    condicion is None or \
    objetivo is None or \
    preferencias is None or \
    posicion is None or \
    distancia is None or \
    clima is None or \
    temperatura is None or \
    humedad is None:

        return "Missing args, the input values are needed to predict"
    
    else:
        return v1_query_process(edad, sexo, peso, condicion, objetivo, preferencias, posicion,
                             distancia, clima, temperatura, humedad, deportes_normalized, deportes, items)

@app.route("/actividades", methods=['GET'])
def actividades():
    hoy = date.today().strftime("%d-%m-%Y")
    key_path = "key.json"
    credentials = service_account.Credentials.from_service_account_file(key_path)
    client = bigquery.Client(credentials=credentials, project=credentials.project_id,)

    query = f'''
    SELECT *
    FROM tripulacionesgrupo5.app_dataset.actividades
    WHERE Fecha = '{hoy}'
    '''
    query_job = client.query(query)
    results = query_job.result()

    listadehoy = pd.DataFrame([dict(row) for row in results])

    return jsonify(listadehoy.to_dict(orient='records'))

# @app.route('/v2/ingest_data', methods=['POST'])
# def ingest_data():
#     tv = request.args.get('tv', None)
#     radio = request.args.get('radio', None)
#     newspaper = request.args.get('newspaper', None)
#     sales = request.args.get('sales', None)

#     connection = sqlite3.connect('data/ingest_data.db')
#     cursor = connection.cursor()
#     query = f'''
#             INSERT INTO advertising (tv, radio, newpaper, sales)
#             VALUES ({tv}, {radio}, {newspaper}, {sales})
#             '''
#     result = cursor.execute(query).fetchall()
    
#     connection.commit()
#     connection.close()

#     return "Data ingested successfully!"

# @app.route('/v2/retrain', methods=['PUT'])
# def retrian():
#     connection = sqlite3.connect('data/ingest_data.db')
#     cursor = connection.cursor()
#     query = 'SELECT * FROM advertising'
#     result = cursor.execute(query).fetchall()

#     X = []
#     y = []
#     for row in result:
#         tv, radio, newspaper, sales = row
#         X.append([tv, radio, newspaper])
#         y.append(sales)

#     with open('data/advertising_model', 'rb') as f:
#         model = pickle.load(f)

#     model.fit(X,y)

#     with open('data/advertising_model', 'wb') as f:
#         pickle.dump(model, f)


#     connection.close()

#     return "Retraining completed!"

app.run(debug=False, host='0.0.0.0', port=os.environ.get("PORT", 5000))

