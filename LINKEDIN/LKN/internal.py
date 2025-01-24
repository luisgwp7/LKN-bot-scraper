import pandas as pd 
import re 
import os
import time
import random
import json
import pyautogui
from datetime import datetime, timedelta
from IPython.display import display, HTML

from selenium                          import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by      import By  
from selenium.common.exceptions        import NoSuchElementException

# import own modules 
from .directories import driver_directory


def get_current_time():
    return datetime.now()

def randomtime():
    #Tiempos
    inicio = 3.0
    fin = 5.0
    tiempo = random.uniform(inicio, fin)
    return tiempo


# Función auxiliar para extraer datos
def extract_data(driver):
    try:
        h1_nombre = driver.find_elements(By.XPATH, "//h1[contains(@class, 'inline t-24 v-align-middle break-words')]")
        div_banner = driver.find_elements(By.XPATH, "//div[contains(@class, 'ph5 pb5')]")
        div_about = driver.find_elements(By.XPATH, "//div[contains(@class, 'display-flex full-width')]")
        section_experience = driver.find_elements(By.XPATH, "//section[.//div[@id='experience']]")

        return {
            "nombre": [elem.text for elem in h1_nombre],
            "banner": [elem.text for elem in div_banner],
            "about": [elem.text for elem in div_about],
            "experience": [elem.text for elem in section_experience],
        }
    except Exception as e:
        print(f"Error al extraer datos: {e}")
        return {}

def wsLinkedin(df, auth_profile, auth_code):
    #Driver directory:
    driver_path = os.path.abspath(driver_directory())
    DRIVER = driver_path
    print(DRIVER)
    tiempo         = randomtime()
    minutes = 5
    driver         = None  
    # Opciones del webdriver. No abrimos ventanas ni cargamos imagenes
    service = Service(f'{DRIVER}')
    options = webdriver.ChromeOptions()
    #options.add_argument("--headless")  
    #options.add_argument("--no-sandbox")  
    #options.add_argument("--disable-popup-blocking") 
    #prefs = {
    #        "profile.managed_default_content_settings.images": 2,
    #        "profile.managed_default_content_settings.fonts":2
    #}
    #options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(service=service, options=options)


    total_enlaces = len(df)
    enlaces_procesados = 0
    enlaces_procesados_desde_ultima_cierre = 0
    last_reset_time = get_current_time()
    
    driver.get('https://www.linkedin.com/')
    time.sleep(tiempo)
    
    next_button = driver.find_element(By.XPATH, "//a[contains(@class, 'nav__button-secondary btn-secondary-emphasis btn-md')]")
    driver.execute_script("arguments[0].click();", next_button)
    time.sleep(tiempo)

    ####################################
    #
    # PASO 1
    #
    ####################################
    
    # Locate the input element by its ID
    username_input = driver.find_element(By.ID, "username")
    username_input.clear()
    username_input.send_keys(auth_profile) 

    time.sleep(tiempo*1.2)
    
    # Locate the input element by its ID
    username_input = driver.find_element(By.ID, "password")
    username_input.clear()
    username_input.send_keys(auth_code) 

    time.sleep(tiempo*1.2)

    # Login 
    login_button = driver.find_element(By.CSS_SELECTOR, "button[data-litms-control-urn='login-submit']")
    login_button.click()

    ####################################
    #
    # PASO 2
    #
    ####################################
    
    time.sleep(tiempo*0.5)
    driver.get('https://www.linkedin.com/in/luis-gwp7/')
    
    # Variables iniciales
    data_list = []
    enlaces_procesados = 0
    last_reset_time = datetime.now()
    minutes = 5  # Reinicia el driver cada 5 minutos
    options = webdriver.ChromeOptions()
    service = None  # Configura tu servicio según tu entorno
    
    try:
        start_time = datetime.now()
        print(f"El proceso de scraping ha comenzado a las {start_time.strftime('%H:%M')} del {start_time.strftime('%d/%m/%Y')}")
    
        index = 0
        continue_scraping = True
    
        while continue_scraping and index < len(df):
            tiempo = randomtime()
            row = df.iloc[index]
            enlaces_procesados += 1
            link = row['Enlace']
    
            current_time = datetime.now()
            elapsed_time = current_time - last_reset_time
    
            if elapsed_time >= timedelta(minutes=minutes):
                try:
                    driver.quit()
                    print("Han pasado 5 minutos. Reiniciando el driver...")
                    driver = webdriver.Chrome(service=service, options=options)
                    last_reset_time = datetime.now()
                except Exception as quit_exception:
                    print(f"Error al cerrar o abrir el driver: {quit_exception}")
    
            if enlaces_procesados % 50 == 0:
                print(f"Enlaces procesados: {enlaces_procesados} de {len(df)}")
    
            try:
                driver.get(link)
                print(f"Navegando a: {link}")
                time.sleep(tiempo * 1.2)
    
                # Primer clic con PyAutoGUI
                x1 = random.uniform(450, 550)
                y1 = random.uniform(500, 600)
                pyautogui.moveTo(x1, y1, duration=1)
                pyautogui.click()
                print(f"Primer clic realizado en ({x1:.2f}, {y1:.2f})")
                time.sleep(tiempo * 1.1)
    
                # Extraer información después del primer clic
                data_1 = extract_data(driver)
    
                # Regresar a la página anterior
                driver.back()
                print("Regresando a la página anterior...")
                time.sleep(tiempo)
    
                # Segundo clic con PyAutoGUI
                x2 = random.uniform(550, 600)
                y2 = random.uniform(700, 800)
                pyautogui.moveTo(x2, y2, duration=1)
                pyautogui.click()
                print(f"Segundo clic realizado en ({x2:.2f}, {y2:.2f})")
                time.sleep(tiempo * 1.1)
    
                # Extraer información después del segundo clic
                data_2 = extract_data(driver)
    
                # Agregar los datos recopilados a la lista
                combined_data = {
                    "Url": link,
                    "nombre_1": data_1.get("nombre", []),
                    "banner_1": data_1.get("banner", []),
                    "about_1": data_1.get("about", []),
                    "experience_1": data_1.get("experience", []),
                    "nombre_2": data_2.get("nombre", []),
                    "banner_2": data_2.get("banner", []),
                    "about_2": data_2.get("about", []),
                    "experience_2": data_2.get("experience", []),
                }
                data_list.append(combined_data)
    
            except Exception as e:
                print(f"Se produjo un error al cargar el enlace: {link}")
                print(f"Excepción: {str(e)}")
                print("Reiniciando el driver y continuando con el próximo enlace...")
                driver = webdriver.Chrome(service=service, options=options)
    
            else:
                index += 1
    
    except Exception as e:
        print(f"Se produjo un error en el scraping: {e}")
    
    finally:
        try:
            driver.quit()
        except Exception as quit_exception:
            print(f"Error al cerrar el driver en finally: {quit_exception}")
    
    # Crear DataFrame a partir de los datos recopilados
    df_result = pd.DataFrame(data_list)

    aviso = f"¡El DataFrame de tamaño {df_result.shape} df_inmobiliarias de FINCA RAIZ está disponible para su análisis!"
    display(HTML(f"<div style='background-color: #b8daba; padding: 10px; border: 1px solid #007723; border-radius: 5px;'><strong>IMBUEBLES DISPONIBLE:</strong> {aviso}</div>"))

    return df_result
    