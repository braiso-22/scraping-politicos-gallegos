from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

url_inicial = "https://transparencia.xunta.gal/"


def get_driver():
    options = Options()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options)
    return driver


def ir_a_principal(driver):
    url = url_inicial + 'tema/transparencia-institucional/goberno-e-altos-cargos/administracion-xeral'
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


def ir_a_biografia(driver, persona):
    url = persona["url"]
    driver.get(url)
    WebDriverWait(driver, 10).until(lambda x: x.find_element(By.ID, "audioContido"))
    return driver


def main():
    driver = get_driver()
    ir_a_principal(driver)
    elementos_con_titulo = obtener_lista(driver)
    lista = obtener_lista_cargos(elementos_con_titulo)

    [print(item) for item in lista]
    pass


if __name__ == '__main__':
    main()
