from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import ast

def v2_intensidad_process(intensidad):
    if intensidad == 0:
        return 2.0
    elif intensidad == 1:
        return 6.0
    elif intensidad == 2:
        return 10.0
    else:
        print('Intensidad no válida')
        

def sim_mat_plot(similarity):
    sns.heatmap(similarity, cmap='coolwarm', center=0)
    return plt.show()

    
def v1_query_process(edad, sexo, peso, condicion, objetivo, preferencias, posicion,
                  distancia, clima, temperatura, humedad, deportes_normalized, deportes, items):
    
    preferencias = ast.literal_eval(preferencias)
    
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

    return {"Deportes recomendados para el usuario": recomendaciones}


def v2_query_process(edad, sexo, peso, condicion, objetivo, preferencias,
                      posicion,distancia, clima, temperatura, humedad,modelo):

    x = pd.DataFrame({
        'Clima': int(clima),
        'Temperatura (°C)': int(temperatura),
        'Humedad': int(humedad),
        'Edad': int(edad),
        'Genero': int(sexo),
        'Peso (Kg)': int(peso),
        'ObjetivoCalorico': int(objetivo),
        'Distancia (Km)': int(distancia),
        'CondicionFisica': int(condicion),
        'DeportePracticado': str(preferencias)
        
        },index=[0])
    
    clima_dummies = pd.get_dummies(x['Clima'], prefix='Clima')   
    x = pd.concat([x, clima_dummies], axis=1)

    genero_dummies = pd.get_dummies(x['Genero'], prefix='Genero')
    x = pd.concat([x, genero_dummies], axis=1)

    # Convertir columna de condición física en variables dummy
    condicion_fisica_dummies = pd.get_dummies(x['CondicionFisica'], prefix='Condicion')
    x = pd.concat([x, condicion_fisica_dummies], axis=1)

    # Convertir columna de objetivo calórico en variables dummy
    objetivos_caloricos_dummies = pd.get_dummies(x['ObjetivoCalorico'], prefix='Objetivo')
    x = pd.concat([x, objetivos_caloricos_dummies], axis=1)


    # Convertir columna de deportes practicados en variables dummy
    deporte_practicado_dummies = x['DeportePracticado'].apply(lambda x: '|'.join(x)).str.get_dummies()
    x = pd.concat([x, deporte_practicado_dummies], axis=1)

    # Eliminar columnas originales que ya no son necesarias
    x.drop(['Clima', 'CondicionFisica', 'ObjetivoCalorico','Genero','DeportePracticado'], axis=1, inplace=True)
    print(x.shape)
    print(x)
    y_pred = modelo.predict(x)
        
        
        

    return {y_pred}
