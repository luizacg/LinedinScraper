import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
import time
import re
from datetime import datetime

def login_linkedin(driver, user, password):
    driver.get('https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'username')))
    field_user = driver.find_element(By.ID, 'username')
    field_user.send_keys(user)
    field_password = driver.find_element(By.ID, 'password')
    field_password.send_keys(password)
    field_password.submit()
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, 'global-nav-typeahead')))
    print("Login realizado com sucesso!")

def verificar_formato_cidade(texto):
    padrao = r"^[A-Za-z\s]+,\s?[A-Za-z\s]+"
    return bool(re.match(padrao, texto))

def extrair_cidade_perfil(driver, url_perfil):
    try:
        driver.get(url_perfil)
        time.sleep(5)
        source = driver.page_source
        soup = bs(source, 'html.parser')
        divs_info_item = soup.find_all('div', class_='org-top-card-summary-info-list__info-item')
        for div in divs_info_item:
            texto = div.get_text().strip()
            if verificar_formato_cidade(texto):
                return texto
        cidade_pessoal = soup.find('span', class_='text-body-small inline t-black--light break-words')
        return cidade_pessoal.get_text().strip() if cidade_pessoal else 'Cidade não encontrada'
    except Exception as e:
        print(f"Erro ao extrair cidade: {e}")
        return 'Erro ao extrair cidade'

arquivo_gerado = 'posts_ibero american conference on software engineering_com_datas-2024-09-23T200914.xlsx'
df = pd.read_excel(arquivo_gerado)

driver = webdriver.Chrome()

user = 'caltic.ufsc@gmail.com'
password = 'ticUFSC.24'

login_linkedin(driver, user, password)

df['cidade'] = ''

try:
    for index, row in df.iterrows():
        url_perfil = row['url_perfil']
        if url_perfil and url_perfil != 'N/A':
            cidade = extrair_cidade_perfil(driver, url_perfil)
            df.at[index, 'cidade'] = cidade
        else:
            df.at[index, 'cidade'] = 'N/A'
finally:
    driver.quit()

novo_arquivo_cidades = f'ibero american conference on software engineering_com_cidades-{datetime.today().strftime("%Y-%m-%dT%H%M%S")}.xlsx'
df.to_excel(novo_arquivo_cidades, index=False)
print(f'Dados atualizados com cidade salvos em: {novo_arquivo_cidades}')