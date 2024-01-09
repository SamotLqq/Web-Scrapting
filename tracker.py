# modulos web scrapting
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# modulos mail
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# modulos generales
import time
import re

# configuraciones
from config import ctr_app, mail_app, tolerancia, page_url

def enviar_mail(emisoraAcc, emisorPass, receptorAcc, body):
    # Configuración del servidor SMTP de Gmail
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = emisoraAcc
    smtp_password = emisorPass

    # Configuración del correo electrónico
    sender_email = emisoraAcc
    receiver_email = receptorAcc
    subject = "Mu"

    # Construir el mensaje de correo electrónico
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    # Conectar al servidor SMTP de Gmail y enviar el correo
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            # Iniciar sesión en el servidor (con inicio de sesión seguro, TLS)
            server.starttls()
            server.login(smtp_username, smtp_password)

            # Enviar el correo electrónico
            server.sendmail(sender_email, receiver_email, message.as_string())

        print("Correo enviado exitosamente.")
    except Exception as e:
        print("Error al enviar el correo:", e)

def configurar_driver(url):
    options = Options()
    options.add_argument('--headless') # ocultar esta linea y la sig para ver navegacion.
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    return driver

def login_in_page(driver, username, password):
    
    boton_login = driver.find_element(By.CLASS_NAME, "open_modal")
    boton_login.click()

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "input-re")))

# Login
    inputs_login = driver.find_elements(By.CLASS_NAME, "input-re")
    input_username = inputs_login[0]
    input_password = inputs_login[1]
    boton_login = driver.find_element(By.NAME, "webengineLogin_submit")
    input_username.send_keys(username)
    input_password.send_keys(password)
    boton_login.click()
    return driver

def extraer_posiciones(driver):
    # Extracciòn de posiciones
    position_dirty = driver.find_elements(By.CLASS_NAME, "myaccount-character-block-location")
    position_dirty = position_dirty[0].text
    patron = re.compile(r'(\d+), (\d+)')
    coincidencias = patron.search(position_dirty)
    x = int(coincidencias.group(1))
    y = int(coincidencias.group(2))
    return [x,y]

def verificar_coordenadas(driver, original_x, original_y):
    # Bucle tracker
    estado = True
    while (estado):
        # Refrescar la página
        time.sleep(300)
        driver.refresh()
        posiciones_actuales = extraer_posiciones(driver)
        actual_x = posiciones_actuales[0]
        actual_y = posiciones_actuales[1]
        if (abs(original_x - actual_x) > tolerancia or abs(original_y - actual_y) > tolerancia):
            estado = False
    return [actual_x, actual_y]

def main():
    try:
        username = input("Ingrese su usuario: ")
        password = input("Ingrese su contraseña: ")
        mail = input("Ingrese su mail: ")

        # cargar datos pagina
        driver = configurar_driver(page_url)

        # login
        driver = login_in_page(driver, username, password)

        # cargar posicion inicial
        posiciones_originales = extraer_posiciones(driver)
        original_x = posiciones_originales[0]
        original_y = posiciones_originales[1]
        print("Las coordenadas originales son: ", original_x, ", ", original_y)

        # verificar posicion actual
        posiciones_finales = verificar_coordenadas(driver, original_x, original_y)
        final_x = posiciones_finales[0]
        final_y = posiciones_finales[1]

        # enviar mail
        body = "Usuario: " + username + " - Coordenadas originales: " + original_x + ", " + original_y + " - Coordenadas finales: " + final_x + ", " + final_y + "."
        enviar_mail(mail_app, ctr_app, mail, body)
        print("Las coordenadas finales son: ", final_x, ", ", final_y)
        driver.close()
    except:
        print("Usuario, Contraseña o Mail no valido")

main()
