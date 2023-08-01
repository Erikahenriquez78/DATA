from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import ast
import math

def haversine_distance(lat1, lon1, lat2, lon2):
    r = 6371  # Radio medio de la Tierra en kilómetros

    # Convertir las latitudes y longitudes de grados a radianes
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Calcular las diferencias de latitud y longitud
    d_lat = lat2_rad - lat1_rad
    d_lon = lon2_rad - lon1_rad

    # Aplicar la fórmula de Haversine
    a = math.sin(d_lat/2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(d_lon/2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = r * c

    return distance

def v1_intensidad_process(intensidad):
    if intensidad == 0:
        return 2.0
    elif intensidad == 1:
        return 6.0
    elif intensidad == 2:
        return 10.0
    else:
        print('Intensidad no válida')
        

def sim_mat_plot(similarity):
    sns.heatmap(similarity, center=0)
    return plt.show()

    
def v1_query_process(edad, sexo, peso, condicion, objetivo, preferencias, posicion,
                  distancia, clima, temperatura, humedad, deportes_normalized, deportes, items):
    
    # Convertir las preferencias en una lista de deportes
    preferencias = ast.literal_eval(preferencias)
    
    # Convertir la posición del usuario a una lista de números
    posicion = ast.literal_eval(posicion)
    latitud_usuario, longitud_usuario = float(posicion[0]), float(posicion[1])

    # Convertir el diccionario en un DataFrame sin índice específico
    perfil_usuario = deportes[deportes['Actividad'].isin(preferencias)].copy()
    
    # Normalizar el perfil del usuario
    scaler = MinMaxScaler()
    perfil_usuario_normalized = pd.DataFrame(scaler.fit_transform(perfil_usuario.iloc[:, 1:]), columns=perfil_usuario.columns[1:])

    # Calcular la similitud del coseno entre el perfil del usuario y todos los deportes
    similarity_scores = cosine_similarity(perfil_usuario_normalized, deportes_normalized)

    # Obtener los índices de los deportes ordenados por similitud
    indices_similares = similarity_scores.argsort()[0][::-1]

    # Establecer el umbral de similitud
    umbral_similitud = 0.5

    # Obtener las recomendaciones finales
    recomendaciones = []
    for indice in indices_similares:
        if similarity_scores[0][indice] > umbral_similitud:
            recomendaciones.append(deportes['Actividad'].iloc[indice])

    # Convertir la posición del usuario a números
    latitud_usuario = float(posicion[0])
    longitud_usuario = float(posicion[1])

    # Filtrar los items que contengan alguna de las recomendaciones en su campo 'EQUIPAMIENTO'
    items_filtrados = items[items['EQUIPAMIENTO'].str.contains('|'.join(recomendaciones))].to_dict(orient='records')

    # Calcular la distancia a cada uno de los items en función de la posición del usuario
    for item in items_filtrados:
        item['DISTANCIA'] = haversine_distance(latitud_usuario, longitud_usuario, item['LATITUD'], item['LONGITUD'])

    # Filtrar los items_filtrados con el valor de distancia
    items_filtrados = [item for item in items_filtrados if item['DISTANCIA'] <= distancia]

    return {"Deportes recomendados para el usuario": recomendaciones, "Items filtrados": items_filtrados}


def v2_query_process(edad, sexo, peso, condicion, objetivo, preferencias,
                     posicion, distancia, clima, temperatura, humedad):
    pass