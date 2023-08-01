from datetime import date
from flask import Flask, jsonify, request, send_file
from google.cloud import bigquery
from google.oauth2 import service_account
import io
import matplotlib.pyplot as plt
from src.data_processing import *
import pandas as pd
import os
import pickle
import seaborn as sns


os.chdir(os.path.dirname(__file__))

app = Flask(__name__)
app.config['DEBUG'] = False


# Cargar archivos
with open('models/deportes_normalized.pkl', 'rb') as f:
    deportes_normalized = pickle.load(f)

# with open('models/randomforest.pkl', 'rb') as f:
#     modelo = pickle.load(f)

deportes = pd.read_csv('data/deportes.csv', index_col=0)
items = pd.read_csv('data/items.csv', index_col=0)
similarity = pd.read_csv('data/similarity.csv', index_col=0)


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
    similitud = float(request.args.get('similitud', None)) # entre 0 y 1



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
    humedad is None or \
    similitud is None:

        return "Missing args, the input values are needed to predict"
    
    else:
        return v1_query_process(preferencias, posicion, distancia, similitud, deportes_normalized, deportes, items)

# @app.route('/v2', methods=['GET'])
# def v2():
#     edad = int(request.args.get('edad', None))
#     sexo = int(request.args.get('sexo', None))
#     peso = float(request.args.get('peso', None))
#     condicion = int(request.args.get('condicion', None)) # baja media alta
#     objetivo = int(request.args.get('objetivo', None)) # suave medio intenso
#     preferencias = request.args.get('preferencias', None) # listado deportes preferidos
#     posicion = request.args.get('posicion', None) # [lat, lon]
#     distancia = int(request.args.get('distancia', None)) # en km
#     clima = int(request.args.get('clima', None)) # soleado nublado lluvioso
#     temperatura = float(request.args.get('temperatura', None)) # ºC
#     humedad = int(request.args.get('humedad', None))
#     # deporte = str(request.args.get('preferencias', None))

#     if edad is None or \
#     sexo is None or \
#     peso is None or \
#     condicion is None or \
#     objetivo is None or \
#     preferencias is None or \
#     posicion is None or \
#     distancia is None or \
#     clima is None or \
#     temperatura is None or \
#     humedad is None:

#         return "Missing args, the input values are needed to predict"
    
#     else:
#         preferencias_list = ast.literal_eval(preferencias)  # Convertir preferencias a una lista
#         return jsonify(v2_query_process(edad, sexo, peso, condicion, objetivo, preferencias_list,
#                                         posicion, distancia, clima, temperatura, humedad, modelo))
        
    # edad = int(request.args.get('edad', None))
    # sexo = int(request.args.get('sexo', None))
    # peso = int(request.args.get('peso', None)).round(2)
    # condicion = int(request.args.get('condicion', None)) # baja media alta
    # objetivo = int(request.args.get('objetivo', None)) # suave medio intenso
    # preferencias = request.args.get('preferencias', None) # listado deportes preferidos
    # posicion = request.args.get('posicion', None) # [lat, lon]
    # distancia = int(request.args.get('distancia', None)) # en km
    # clima = int(request.args.get('clima', None)) # soleado nublado lluvioso
    # temperatura = int(request.args.get('temperatura', None)) # ºC
    # humedad = int(request.args.get('humedad', None))

    # if edad is None or \
    # sexo is None or \
    # peso is None or \
    # condicion is None or \
    # objetivo is None or \
    # preferencias is None or \
    # posicion is None or \
    # distancia is None or \
    # clima is None or \
    # temperatura is None or \
    # humedad is None:

    #     return "Missing args, the input values are needed to predict"
    
    # else:
    #     return v2_query_process(edad, sexo, peso, condicion, objetivo, preferencias,
    #                             posicion, distancia, clima, temperatura, humedad,modelo)



@app.route('/similitud', methods=['GET'])
def similitud():
    similarity = pd.read_csv('data/similarity.csv', index_col=0)
    simil = similarity.T
    plt.figure(figsize=(25, 25))
    sns.heatmap(simil, xticklabels=False, cmap="Blues", linewidths=0.5)
    plt.title('Similitud Entre Deportes Estudiados')
    plt.ylabel('Deportes');

    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png') 
    plt.close()

    img_data = img_buf.getvalue()
    return send_file(io.BytesIO(img_data), mimetype='image/png')

@app.route("/actividades", methods=['GET'])
def actividades():

    hoy = date.today().strftime("%Y-%m-%d")
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

app.run(debug=False, host='0.0.0.0', port=os.environ.get("PORT", 5000))

