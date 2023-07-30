from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np

def intensidad_process(intensidad):
    if intensidad == 0:
        return 2.0
    elif intensidad == 1:
        return 6.0
    elif intensidad == 2:
        return 10.0
    else:
        print('Intensidad no válida')

    
def v1_query_process(edad, sexo, peso, condicion, objetivo, preferencias, posicion,
                  distancia, clima, temperatura, humedad, deportes_normalized, deportes, items):
    
    # Convertir preferencias en una lista de deportes (quitar la conversión a float)
    preferencias = preferencias.strip('[]').split(',')

    # Convertir posición del usuario en una lista de números (quitar la conversión a float)
    posicion = [float(coord) for coord in posicion.strip('[]').split(',')]

    # Codificar el clima usando one-hot encoding
    clima = pd.get_dummies([clima], prefix='clima', drop_first=True)

    # Crear el perfil del usuario
    perfil_usuario = [edad, sexo, peso, condicion, objetivo] + [1 if deporte in preferencias else 0 for deporte in deportes['Actividad']] + posicion + [distancia] + list(clima.iloc[0]) + [temperatura, humedad]
    scaler = MinMaxScaler()
    perfil_usuario_normalized = scaler.fit_transform([perfil_usuario])

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

    return "Deportes recomendados para el usuario:", recomendaciones


def v2_query_process(intensidad, equipo, equipamiento, contacto, pelota, raqueta, aire_libre, deportes_normalized, deportes):
    intensidad = intensidad_process(intensidad)
    
    # Crear el perfil del usuario como un diccionario
    perfil_usuario = {
        'intensidad': intensidad,
        'equipo': equipo,
        'equipamiento': equipamiento,
        'contacto': contacto,
        'pelota': pelota,
        'raqueta': raqueta,
        'aire_libre': aire_libre
    }
    
    # Convertir el diccionario en un DataFrame sin índice específico
    perfil_usuario = pd.DataFrame(perfil_usuario)
    
    # Normalizar el perfil del usuario
    scaler = MinMaxScaler()
    perfil_usuario_normalized = scaler.fit_transform(perfil_usuario)

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

    return "Deportes recomendados para el usuario:", recomendaciones