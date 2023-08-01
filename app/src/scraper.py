from datetime import date
from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account
import os
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
load_dotenv()

# Comienza el scraping automático.

contacto = pd.read_csv('../data/contacto.csv')
options  = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)

url = 'https://sede.madrid.es/portal/site/tramites/menuitem.62876cb64654a55e2dbd7003a8a409a0/?vgnextoid=e3b0234be7924710VgnVCM2000001f4a900aRCRD&vgnextchannel=b59637c190180210VgnVCM100000c90da8c0RCRD&vgnextfmt=pd'
driver.get(url)

rechazar = driver.find_element(By.XPATH, '//*[@id="iam-cookie-control-modal-action-secondary"]')
rechazar.click()

en_linea = driver.find_element(By.XPATH, '//*[@id="verTodas"]/div/div[1]/p/a')
en_linea.click()

driver.close()
driver.switch_to.window(driver.window_handles[0])

usuario_contrasena = driver.find_element(By.XPATH, '//*[@id="ContentFixedSection_uSecciones_divSections"]/section[1]/div[2]/div/div/div[2]/article[1]')
usuario_contrasena.click()

acceso = driver.find_element(By.XPATH, '//*[@id="acceso_pass"]')
acceso.click()

usuario = driver.find_element(By.XPATH, '//*[@id="correoelectronico"]')
usuario.send_keys(os.environ.get('user'))

contrasena = driver.find_element(By.XPATH, '//*[@id="contrasenia"]')
contrasena.send_keys(os.environ.get('pass'))
contrasena.submit()

driver.execute_script("window.scrollBy(0, 100);")
actividades_dia_centro = driver.find_element(By.XPATH, '//*[@id="ContentFixedSection_uSecciones_divSections"]/section[3]/div[2]/div/div/div[2]/article[1]/div')
actividades_dia_centro.click()

disponibilidad = driver.find_element(By.XPATH, '//*[@id="ContentFixedSection_uAltaEventos_uCentrosSeleccionar_availability_filter_on"]')
disponibilidad.click()

# driver.execute_script("document.body.style.zoom = '25%';")
time.sleep(1)
centros = driver.find_elements(By.XPATH, "//li[contains(@class, 'media pull-left')]")

columnas = ["Actividad", "Horario", "Rango_de_edad", "Duracion", "Centro", "Direccion", ]
df = pd.DataFrame(columns=columnas)

for i in range(len(centros)):
    centro = centros[i]
    time.sleep(3)
    centro.click()
    time.sleep(3)

    nombre = driver.find_element(By.XPATH, '//*[@id="ContentFixedSection_uAltaEventos_divFacility"]/div/h2')
    direccion = driver.find_element(By.XPATH, '//*[@id="ContentFixedSection_uAltaEventos_divFacility"]/div/div[2]')
    elementos_h4 = driver.find_elements(By.XPATH, '//div[@class="collapse in"]//h4')

    actividades_con_info_adicional = []

    rango_edad_actual = None
    duracion_actual = None

    patron_rango_edad_flexible = re.compile(r"(?i)\b(?:De\s*)?(\d+)\s*a\s*(\d+)\s*años\b")
    patron_rango_edad_apartirde = re.compile(r"(?i)\bA\s*partir\s+de\s+(\d+)\s+años\b")
    patron_duracion = r"(\d+)\s*[´'`]"
    patron_hora = r"\d{1,2}:\d{2}"

    for elemento in elementos_h4:
        texto = elemento.text
        
        if re.match(patron_hora, texto):
            actividades_con_info_adicional[-1][1].append(texto)
        else:
            titulo_actual = texto
            rango_edad_actual = None
            duracion_actual = None
            elementos_p = elemento.find_elements(By.XPATH, './following-sibling::p')
            
            for elem_p in elementos_p:
                texto_p = elem_p.text
                resultado_rango_edad = re.search(patron_rango_edad_flexible, texto_p)
                
                if resultado_rango_edad:
                    rango_edad_actual = f"De {resultado_rango_edad.group(1)} a {resultado_rango_edad.group(2)} años"

                else:
                    resultado_rango_edad_apartirde = re.search(patron_rango_edad_apartirde, texto_p)
                    if resultado_rango_edad_apartirde:
                        rango_edad_actual = f"A partir de {resultado_rango_edad_apartirde.group(1)} años"
                        
                resultado_duracion = re.search(patron_duracion, texto_p)
                if resultado_duracion:
                    duracion_actual = f"{resultado_duracion.group(1)}'"

            actividades_con_info_adicional.append([titulo_actual, [], rango_edad_actual, duracion_actual])

    for actividad in actividades_con_info_adicional:
        titulo = actividad[0]
        horas = actividad[1]
        rango_edad = actividad[2]
        duracion = actividad[3]
        df.loc[len(df)] = [titulo, horas, rango_edad, duracion, nombre.text, direccion.text]

    back = driver.find_element(By.XPATH, '//*[@id="ContentFixedSection_uAltaEventos_divFacility"]/div/div[1]/span')
    back.click()
driver.quit()

# Modificación del dataframe

df.insert(0, 'Fecha', date.today().strftime("%d-%m-%Y"))
df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d-%m-%Y')
df.Horario = df.Horario.apply(lambda x: ', '.join(x))
df.Duracion = df.Duracion.str.replace("'", " minutos")

df = pd.merge(df, contacto, on='Centro', how='left')

# Guardar una copia en local

df.to_csv(f'../data/{date.today().strftime("%d-%m-%Y")}.csv', index=False)

# Subida a la base de datos en Big Query

key_path = '../key.json'
credentials = service_account.Credentials.from_service_account_file(key_path)
client = bigquery.Client(credentials=credentials, project=credentials.project_id,)

df.to_gbq(destination_table= 'tripulacionesgrupo5.app_dataset.actividades',
          if_exists='append',
          table_schema = [{'name': 'Fecha', 'type': 'DATE'},
                          {'name': 'Actividad', 'type': 'STRING'},
                          {'name': 'Horario', 'type': 'STRING'},
                          {'name': 'Rango_de_edad', 'type': 'STRING'},
                          {'name': 'Duracion', 'type': 'STRING'},
                          {'name': 'Centro', 'type': 'STRING'},
                          {'name': 'Direccion', 'type': 'STRING'},
                          {'name': 'Distrito', 'type': 'STRING'},
                          {'name': 'Telefono', 'type': 'INTEGER'}],
          credentials= credentials)