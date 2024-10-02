from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
from datetime import datetime
import time
import pandas as pd

def login_linkedin(driver, user, password):
    driver.get('https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'username')))
    field_user = driver.find_element(By.ID, 'username')
    field_user.send_keys(user)
    field_password = driver.find_element(By.ID, 'password')
    field_password.send_keys(password)
    field_password.submit()
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, 'global-nav-typeahead')))

def rolar_ate_carregar_todos_comentarios(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    scrolling = True
    while scrolling:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            scrolling = False
        last_height = new_height

def extrair_comentarios(driver, url_post):
    try:
        driver.get(url_post)
        time.sleep(5)
        rolar_ate_carregar_todos_comentarios(driver)
        page_source = driver.page_source
        soup = bs(page_source, 'html.parser')
        comentarios_section = soup.find('div', class_='comments-comments-list')
        comentarios = []
        if comentarios_section:
            comentario_items = comentarios_section.find_all('article', class_='comments-comment-entity')
            for comentario_item in comentario_items:
                try:
                    autor_elem = comentario_item.find('span', class_='comments-comment-meta__description-title')
                    comentario_text_elem = comentario_item.find('div', class_='update-components-text')
                    autor = autor_elem.get_text().strip() if autor_elem else 'Autor desconhecido'
                    comentario_texto = comentario_text_elem.get_text().strip() if comentario_text_elem else 'Comentário vazio'
                    comentarios.append(f'{autor}: {comentario_texto}')
                except Exception as e:
                    print(f"Erro ao extrair comentário: {e}")
        return ', '.join(comentarios) if comentarios else 'Sem comentários'
    except Exception as e:
        print(f"Erro ao extrair comentários do post {url_post}: {e}")
        return 'Erro ao extrair comentários'

arquivo_entrada = 'posts_brazilian symposium on software engineering_com_cidades-2024-09-24T200218.xlsx'
df = pd.read_excel(arquivo_entrada)
df['comentarios'] = ''

user = 'caltic.ufsc@gmail.com'
password = 'ticUFSC.24'

driver = webdriver.Chrome()

try:
    login_linkedin(driver, user, password)
    for index, row in df.iterrows():
        url_post = row['url_post']
        comentarios = extrair_comentarios(driver, url_post)
        df.at[index, 'comentarios'] = comentarios
finally:
    driver.quit()

novo_arquivo = f'brazilian symposium on software engineering_com_comenntarios-{datetime.today().strftime("%Y-%m-%dT%H%M%S")}.xlsx'
df.to_excel(novo_arquivo, index=False)
print(f'Arquivo com comentários salvo como: {novo_arquivo}')
