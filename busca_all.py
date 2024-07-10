from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
from langdetect import detect
from datetime import datetime
import time
import pandas as pd

user = 'luizacmg2@gmail.com'
password = 'Gavop099'

def get_publicacoes(url):

    driver = webdriver.Chrome()
    driver.get('https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin')
    try:
        if user and password:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, 'username'))
            )
            field_user = driver.find_element(By.ID, 'username')
            field_user.send_keys(user)
            field_password = driver.find_element(By.ID, 'password')
            field_password.send_keys(password)
            field_password.submit()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'global-nav-typeahead')))

        driver.get(url)

        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(7)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Rolar de volta ao topo da página
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)

        lista_posts = []

        source = driver.page_source
        html_dom = bs(source.encode('utf-8'), 'html.parser')

        posts = html_dom.find_all(class_='feed-shared-update-v2')

        for post in posts:
            publicacao = {}

            nome_autor = post.find(class_='update-components-actor__name')
            if nome_autor:
                nome_autor_hidden = nome_autor.find(class_='visually-hidden')
                publicacao['nome_autor'] = nome_autor_hidden.get_text().strip() if nome_autor_hidden else 'N/A'
            else:
                publicacao['nome_autor'] = 'N/A'

            cargo_autor = post.find(class_='update-components-actor__description')
            if cargo_autor:
                cargo_autor_hidden = cargo_autor.find(class_='visually-hidden')
                publicacao['cargo_autor'] = cargo_autor_hidden.get_text().strip() if cargo_autor_hidden else 'N/A'
            else:
                publicacao['cargo_autor'] = 'N/A'

            texto_publicacao = post.find(class_='update-components-text')
            if texto_publicacao:
                publicacao['texto_postagem'] = texto_publicacao.get_text().strip()
                if len(publicacao['texto_postagem']) > 10:
                    publicacao['idioma_postagem'] = detect(publicacao['texto_postagem'])
                else:
                    publicacao['idioma_postagem'] = 'N/A'
                publicacao['tamanho_texto_postagem'] = len(publicacao['texto_postagem'])

            else:
                publicacao['texto_postagem'] = ' '
                publicacao['idioma_postagem'] = 'N/A'
                publicacao['tamanho_texto_postagem'] = 0

            reacoes = post.find(class_='social-details-social-counts__social-proof-fallback-number')
            if reacoes:
                publicacao['num_reacoes'] = reacoes.get_text().strip()
            else:
                reacoes = post.find(class_='social-details-social-counts__reactions-count')
                publicacao['num_reacoes'] = reacoes.get_text().strip() if reacoes else 0

            publicacao['num_comentarios'] = 0
            comentarios = post.find(class_='social-details-social-counts__comments')
            if comentarios:
                publicacao['num_comentarios'] = comentarios.get_text().strip().split(' ')[0]

            publicacao['num_compartilhamentos'] = 0
            compartilhamentos = post.select('.social-details-social-counts__item .ember-view')
            if compartilhamentos:
                publicacao['num_compartilhamentos'] = compartilhamentos[0].get_text().strip().split(' ')[0]

            publicacao['num_imagens'] = len(post.select('.update-components-image__image'))

            url_perfil = post.find('a', href=True)
            if url_perfil:
                publicacao['url_perfil'] = url_perfil['href']
            else:
                publicacao['url_perfil'] = 'N/A'

            lista_posts.append(publicacao)

        posts = driver.find_elements(By.CLASS_NAME, 'feed-shared-update-v2')
        for i, post in enumerate(posts):
            try:
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(2)

                menu_button = WebDriverWait(post, 20).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.feed-shared-control-menu__trigger'))
                )
                menu_button.click()
                time.sleep(10)

                menu_options = WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'artdeco-dropdown__content-inner')]//li"))
                )
                if len(menu_options) > 1:
                    second_option = menu_options[1]
                    second_option.click()
                    time.sleep(5)

                    lista_posts[i]['url_post'] = driver.execute_script("return navigator.clipboard.readText()")

            except Exception as e:
                print(e)

            time.sleep(1)

        df = pd.DataFrame(lista_posts)

        nome_arquivo = f'./cibse_artigo-{datetime.today().strftime("%Y-%m-%dT%H%M%S")}.xlsx'
        df.to_excel(nome_arquivo, index=False)

        return lista_posts

    finally:
        driver.quit()

url = 'https://www.linkedin.com/search/results/content/?keywords=cibse%20artigo&origin=FACETED_SEARCH&sid=pTA&sortBy=%22date_posted%22'
publicacoes = get_publicacoes(url)
print(publicacoes)
