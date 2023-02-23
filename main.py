from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import requests

url_inicial = "https://transparencia.xunta.gal"


def get_driver():
    options = Options()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options)
    return driver


def ir_a_principal(driver):
    url = url_inicial + '/tema/transparencia-institucional/goberno-e-altos-cargos/administracion-xeral'
    driver.get(url)


def obtener_lista(driver):
    section = driver.find_element(By.ID, "audioContido")
    h4s = section.find_elements(By.TAG_NAME, "h4")
    listas = section.find_elements(By.TAG_NAME, "ul")
    lista_con_titulo = []
    for i in range(len(h4s)):
        lista_con_titulo.append([h4s[i], listas[i]])

    return lista_con_titulo


def obtener_valores_item(institucion_h4, li):
    try:
        a = li.find_element(By.TAG_NAME, "a")
        url = a.get_attribute("href")
        nombre = a.text
        cargo_e_institucion = li.text.replace(nombre, "")
        array = cargo_e_institucion.split("-")
        cargo = array[1].strip()

    except Exception as e:
        url = ""
        datos_persona = li.text.split("-")
        nombre = datos_persona[0].strip()
        cargo = datos_persona[1].strip()
        print(f"La persona {nombre} no tiene url")

    valores = {
        "institucion": institucion_h4.text,
        "cargo": cargo,
        "url": url,
        "nombre": nombre
    }
    return valores


def obtener_lista_cargos(elementos_con_titulo):
    lista = []
    for par in elementos_con_titulo:
        titulo_h4 = par[0]
        for li in par[1].find_elements(By.TAG_NAME, "li"):
            lista.append(obtener_valores_item(titulo_h4, li))
    return lista


def obtener_biografia(driver: WebDriver):
    biografia: WebElement = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(driver.find_element(By.ID, "audioContido"))
    )
    text_biografia = ""
    for ul in biografia.find_elements(By.TAG_NAME, "ul"):
        for li in ul.find_elements(By.TAG_NAME, "li"):
            text_biografia += li.text + "\n"
    for p in biografia.find_elements(By.TAG_NAME, "p"):
        if p.text:
            text_biografia += p.text + "\n"
    return text_biografia


def obtener_url_foto(driver: WebDriver):
    try:
        img = driver.find_element(By.ID, "owlImaxes").find_element(By.TAG_NAME, "img")
        src = img.get_attribute("src")
        division = src.split("=")
        src = division[0] + "=" + str(int(division[1]) + 1)
        return src
    except Exception as e:
        print("sin foto")
        return ""
    pass


def obtener_contacto(contacto_y_retribucion):
    contactos_enlaces = contacto_y_retribucion.find_elements(By.TAG_NAME, "a")
    contactos = {}
    for contacto in contactos_enlaces:
        if "mailto:" in contacto.get_attribute("href"):
            contactos["correo"] = contacto.get_attribute("href").replace("mailto:", "")
            continue
        contactos[contacto.text] = contacto.get_attribute("href")
    if "Tel.:" in contacto_y_retribucion.text:
        contactos["telefono"] = contacto_y_retribucion.text.split("Tel.: ")[1].split("\n")[0].strip()
    return contactos


def obtener_retribuciones(contacto_y_retribucion: str):
    retribucion = contacto_y_retribucion.split("Retribución anual:")[1]
    retribucion_anual = "Retribución anual:" + retribucion.strip()
    retribuciones = {}
    if "Salario:" in retribucion_anual:
        retribuciones["salario"] = retribucion_anual.split("Salario:")[1].split("€")[0].strip()
    if "Salario bruto anual:" in retribucion_anual:
        retribuciones["salario bruto anual"] = retribucion_anual.split("Salario bruto anual:")[1].split("€")[0].strip()
    if "Trienios:" in retribucion_anual:
        retribuciones["trienios"] = retribucion_anual.split("Trienios:")[1].split("€")[0].strip()
    if "Complemento de carreira:" in retribucion_anual:
        retribuciones["Complemento de carreira"] = retribucion_anual.split("Complemento de carreira:")[1].split("€")[
            0].strip()
    if "total anual" in retribucion_anual:
        retribuciones["total anual"] = retribucion_anual.split("Total anual:")[1].split("€")[0].strip(),
    return retribuciones


def obtener_datos_interesantes(driver: WebDriver):
    biografia = obtener_biografia(driver)
    foto = obtener_url_foto(driver)
    contacto_y_retribucion = driver.find_element(By.TAG_NAME, "blockquote")
    contactos = obtener_contacto(contacto_y_retribucion)
    retribuciones = obtener_retribuciones(contacto_y_retribucion.text)
    return {
        "biografia": biografia,
        "foto": foto,
        "contacto": contactos,
        "retribucion": retribuciones,
    }

    pass


def main():
    driver: WebDriver = get_driver()
    ir_a_principal(driver)
    elementos_con_titulo = obtener_lista(driver)
    lista = obtener_lista_cargos(elementos_con_titulo)
    for persona in lista:
        url = persona["url"]
        if url == "":
            continue
        print(persona["nombre"])
        driver.get(url)
        persona["datos"] = obtener_datos_interesantes(driver)

    [print(item, ",") for item in lista]
    pass


if __name__ == '__main__':
    main()
