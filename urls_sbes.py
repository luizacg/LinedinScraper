import time
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup as bs
from langdetect import detect
from selenium import webdriver
from selenium.webdriver.common.by import By

lista_publicacoes = []

user = ''
password = ''

driver = webdriver.Chrome()
driver.get('https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin')

field_user = driver.find_element(By.ID, 'username')
field_user.send_keys(user)
field_password = driver.find_element(By.ID, 'password')
field_password.send_keys(password)
field_password.submit()

df = pd.read_excel('urls.xlsx')

for index, row in df.iterrows():
    driver.get(row['url'])
    time.sleep(0.1)
    source = driver.page_source
    html_dom = bs(source.encode('utf-8'), 'html.parser')
    html_dom.prettify()

    publicacao = {}

    nome_autor = html_dom.find(class_='update-components-actor__name')
    if nome_autor:
        nome_autor_hidden = nome_autor.find(class_='visually-hidden')
        publicacao['nome_autor'] = nome_autor_hidden.get_text().strip() if nome_autor_hidden else 'N/A'
    else:
        publicacao['nome_autor'] = 'N/A'

    cargo_autor = html_dom.find(class_='update-components-actor__description')
    if cargo_autor:
        cargo_autor_hidden = cargo_autor.find(class_='visually-hidden')
        publicacao['cargo_autor'] = cargo_autor_hidden.get_text().strip() if cargo_autor_hidden else 'N/A'
    else:
        publicacao['cargo_autor'] = 'N/A'

    texto_publicacao = html_dom.find(class_='update-components-text')
    if texto_publicacao:
        publicacao['texto_postagem'] = texto_publicacao.get_text().strip()
        publicacao['idioma_postagem'] = detect(publicacao['texto_postagem'])
        publicacao['tamanho_texto_postagem'] = len(publicacao['texto_postagem'])
    else:
        publicacao['texto_postagem'] = ' '
        publicacao['idioma_postagem'] = 'N/A'
        publicacao['tamanho_texto_postagem'] = 0

    reacoes = html_dom.find(class_='social-details-social-counts__social-proof-fallback-number')
    if reacoes:
        publicacao['num_reacoes'] = reacoes.get_text().strip()
    else:
        reacoes = html_dom.find(class_='social-details-social-counts__reactions-count')
        publicacao['num_reacoes'] = reacoes.get_text().strip() if reacoes else 0

    publicacao['num_comentarios'] = 0
    comentarios = html_dom.find(class_='social-details-social-counts__comments')
    if comentarios:
        publicacao['num_comentarios'] = comentarios.get_text().strip().split(' ')[0]

    publicacao['num_compartilhamentos'] = 0
    compartilhamentos = html_dom.select('.social-details-social-counts__item .ember-view')
    if compartilhamentos:
        publicacao['num_compartilhamentos'] = compartilhamentos[0].get_text().strip().split(' ')[0]

    publicacao['num_imagens'] = len(html_dom.select('.update-components-image__image'))

    lista_publicacoes.append(publicacao)

    time.sleep(1)

df_novo = pd.DataFrame(lista_publicacoes)
df = pd.concat([df, df_novo], axis=1)
nome_arquivo = f'./urls-{datetime.today().strftime("%Y-%m-%dT%H%M%S")}.xlsx'
df.to_excel(nome_arquivo, index=False)

driver.quit()
