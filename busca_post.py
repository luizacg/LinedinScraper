from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
from langdetect import detect_langs
from datetime import datetime
import time
import pandas as pd
import re
import emoji
from nltk import sent_tokenize
import gender_guesser.detector as gender

user = 'luizacmg2@gmail.com'
password = 'Gavop099'

def detectar_genero_genderguesser(nome_autor):
    d = gender.Detector(case_sensitive=False)
    primeiro_nome = nome_autor.split()[0]
    genero = d.get_gender(primeiro_nome)
    if genero in ['male', 'mostly_male']:
        return 'Masculino'
    elif genero in ['female', 'mostly_female']:
        return 'Feminino'
    elif genero == 'andy':
        return 'Ambíguo'
    else:
        return 'Desconhecido'

def extrair_hashtags(texto):
    hashtags = re.findall(r'#\w+', texto)
    return hashtags, len(hashtags)

def contar_urls(texto):
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', texto)
    return len(urls)

def contar_emojis(texto):
    return emoji.emoji_count(texto)

def detectar_idiomas(texto):
    try:
        frases = sent_tokenize(texto)
        idiomas_detectados = {}
        total_prob = 0
        idiomas_permitidos = ['pt', 'es', 'en', 'fr', 'de', 'it']
        for frase in frases:
            try:
                detected_langs = detect_langs(frase)
                for lang in detected_langs:
                    if lang.lang in idiomas_permitidos:
                        if lang.lang in idiomas_detectados:
                            idiomas_detectados[lang.lang] += lang.prob
                        else:
                            idiomas_detectados[lang.lang] = lang.prob
                        total_prob += lang.prob
            except:
                continue
        idiomas_formatados = ', '.join([f'{lang} ({round((prob / total_prob) * 100, 2)}%)' for lang, prob in idiomas_detectados.items()])
        return idiomas_formatados if idiomas_formatados else 'N/A'
    except Exception as e:
        return f'Erro na detecção de idiomas: {e}'

def extrair_marcados(post):
    texto_post = post.find(class_='update-components-text')
    marcados = []
    if texto_post:
        links = texto_post.find_all('a', class_='app-aware-link')
        for link in links:
            href = link.get('href')
            nome = link.get_text().strip()
            if href and ('linkedin.com/in/' in href or 'linkedin.com/company/' in href):
                marcados.append((nome, href))
    return marcados, len(marcados)

def login_linkedin(driver):
    driver.get('https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'username')))
    field_user = driver.find_element(By.ID, 'username')
    field_user.send_keys(user)
    field_password = driver.find_element(By.ID, 'password')
    field_password.send_keys(password)
    field_password.submit()
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, 'global-nav-typeahead')))

def extrair_repost(post):
    try:
        repost_section = post.find(class_='update-components-mini-update-v2') if post else None
        if repost_section:
            repost_author = repost_section.find(class_='update-components-actor__name')
            if repost_author:
                nome_oculto = repost_author.find(class_='visually-hidden')
                if nome_oculto:
                    return nome_oculto.get_text().strip()
                else:
                    return repost_author.get_text().strip()
        return None
    except Exception as e:
        print(f"Erro ao verificar repost: {e}")
        return None

def extrair_tipos_reacoes(driver):
    reacoes_dict = {
        'gostei': 0,
        'parabens': 0,
        'amei': 0,
        'apoio': 0,
        'genial': 0,
        'engracado': 0
    }
    try:
        btn_reacoes = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'social-details-social-counts__reactions-count')))
        btn_reacoes.click()
        time.sleep(5)
        modal = driver.page_source
        soup_modal = bs(modal, 'html.parser')
        botoes_reacoes = soup_modal.find_all('button', class_='artdeco-tab')
        for botao in botoes_reacoes:
            tipo_reacao = botao.get('data-js-reaction-tab', '')
            quantidade_span = botao.find_all('span')
            quantidade = int(quantidade_span[1].get_text().strip()) if len(quantidade_span) > 1 else 0
            if tipo_reacao == 'LIKE':
                reacoes_dict['gostei'] = quantidade
            elif tipo_reacao == 'PRAISE':
                reacoes_dict['parabens'] = quantidade
            elif tipo_reacao == 'EMPATHY':
                reacoes_dict['amei'] = quantidade
            elif tipo_reacao == 'INTEREST':
                reacoes_dict['genial'] = quantidade
            elif tipo_reacao == 'APPRECIATION':
                reacoes_dict['apoio'] = quantidade
            elif tipo_reacao == 'ENTERTAINMENT':
                reacoes_dict['engracado'] = quantidade
    except Exception as e:
        print(f"Erro ao extrair reações: {e}")
    finally:
        close_btn = driver.find_element(By.CLASS_NAME, 'artdeco-modal__dismiss')
        if close_btn:
            close_btn.click()
        time.sleep(1)
    return reacoes_dict

def classificar_afiliacao(cargo_autor):
    palavras_academicas = ['estudante', 'student', 'professor', 'researcher', 'pesquisador', 'docente', 'academic', 'followers']
    for palavra in palavras_academicas:
        if palavra.lower() in cargo_autor.lower():
            return 'Acadêmica'
    return 'Profissional'

def classificar_tipo_postagem(cargo_autor):
    if "followers" in cargo_autor.lower():
        return "Institucional"
    else:
        return "Individual"

def extrair_dados_post(driver, url_post):
    try:
        driver.get(url_post)
        time.sleep(5)
        publicacao = {}
        source = driver.page_source
        html_dom = bs(source.encode('utf-8'), 'html.parser')
        post = html_dom.find(class_='feed-shared-update-v2')
        nome_autor = post.find(class_='update-components-actor__name') if post else None
        if nome_autor:
            nome_autor_hidden = nome_autor.find(class_='visually-hidden')
            publicacao['nome_autor'] = nome_autor_hidden.get_text().strip() if nome_autor_hidden else 'N/A'
        else:
            publicacao['nome_autor'] = 'N/A'
        cargo_autor = post.find(class_='update-components-actor__description') if post else None
        if cargo_autor:
            cargo_autor_hidden = cargo_autor.find(class_='visually-hidden')
            if cargo_autor_hidden:
                ocupacao_e_local = cargo_autor_hidden.get_text().strip()
                if " at " in ocupacao_e_local:
                    ocupacao, local_trabalho = ocupacao_e_local.split(" at ", 1)
                elif " of " in ocupacao_e_local:
                    ocupacao, local_trabalho = ocupacao_e_local.split(" of ", 1)
                elif " na " in ocupacao_e_local:
                    ocupacao, local_trabalho = ocupacao_e_local.split(" na ", 1)
                elif " no " in ocupacao_e_local:
                    ocupacao, local_trabalho = ocupacao_e_local.split(" no ", 1)
                else:
                    ocupacao = ocupacao_e_local
                    local_trabalho = 'N/A'
                publicacao['cargo_autor'] = ocupacao
                publicacao['local_trabalho'] = local_trabalho
            else:
                publicacao['cargo_autor'] = 'N/A'
                publicacao['local_trabalho'] = 'N/A'
        else:
            publicacao['cargo_autor'] = 'N/A'
            publicacao['local_trabalho'] = 'N/A'
        publicacao['afiliacao_autor'] = classificar_afiliacao(publicacao['cargo_autor'])
        publicacao['tipo_postagem'] = classificar_tipo_postagem(publicacao['cargo_autor'])
        repost_author = extrair_repost(post)
        publicacao['repost_autor'] = repost_author if repost_author else 'Não é repost'
        texto_publicacao = post.find(class_='update-components-text') if post else None
        if texto_publicacao:
            publicacao['texto_postagem'] = texto_publicacao.get_text().strip()
            if len(publicacao['texto_postagem']) > 10:
                publicacao['idiomas_postagem'] = detectar_idiomas(publicacao['texto_postagem'])
            else:
                publicacao['idiomas_postagem'] = 'N/A'
            publicacao['tamanho_texto_postagem'] = len(publicacao['texto_postagem'])
            hashtags, num_hashtags = extrair_hashtags(publicacao['texto_postagem'])
            publicacao['hashtags'] = ', '.join(hashtags)
            publicacao['num_hashtags'] = num_hashtags
            publicacao['num_urls'] = contar_urls(publicacao['texto_postagem'])
            publicacao['num_emojis'] = contar_emojis(publicacao['texto_postagem'])
            nomes_marcados, num_marcados = extrair_marcados(post)
            publicacao['marcados'] = ', '.join([nome for nome, href in nomes_marcados])
            publicacao['num_marcados'] = num_marcados
        else:
            publicacao['texto_postagem'] = ' '
            publicacao['idiomas_postagem'] = 'N/A'
            publicacao['tamanho_texto_postagem'] = 0
            publicacao['hashtags'] = ''
            publicacao['num_hashtags'] = 0
            publicacao['num_urls'] = 0
            publicacao['num_emojis'] = 0
            publicacao['marcados'] = ''
            publicacao['num_marcados'] = 0
        reacoes = post.find(class_='social-details-social-counts__reactions-count') if post else None
        if reacoes:
            publicacao['num_reacoes'] = int(re.sub(r'\D', '', reacoes.get_text().strip()))
            reacoes_detalhadas = extrair_tipos_reacoes(driver)
            publicacao.update(reacoes_detalhadas)
        else:
            publicacao['num_reacoes'] = 0
        num_comentarios = post.find(class_='social-details-social-counts__comments')
        publicacao['num_comentarios'] = int(re.sub(r'\D', '', num_comentarios.get_text())) if num_comentarios else 0
        num_compartilhamentos = post.select('.social-details-social-counts__item .ember-view')
        publicacao['num_compartilhamentos'] = int(re.sub(r'\D', '', num_compartilhamentos[0].get_text())) if num_compartilhamentos else 0
        publicacao['num_imagens'] = len(post.select('.update-components-image__image')) if post else 0
        url_perfil = post.find('a', href=True) if post else None
        if url_perfil:
            publicacao['url_perfil'] = url_perfil['href']
        else:
            publicacao['url_perfil'] = 'N/A'
        return publicacao
    except Exception as e:
        print(f"Erro ao extrair dados do post: {e}")
        return {}

arquivo_urls = 'urls_international-conference-on-software-engineering-2024-09-18T010730.xlsx'
df_urls = pd.read_excel(arquivo_urls)

df_urls['nome_evento'] = 'International Conference on Software Engineering (ICSE)'
df_urls['busca_string'] = 'international conference on software engineering'
df_urls['nome_autor'] = ''
df_urls['cargo_autor'] = ''
df_urls['local_trabalho'] = ''
df_urls['texto_postagem'] = ''
df_urls['idiomas_postagem'] = ''
df_urls['tamanho_texto_postagem'] = ''
df_urls['hashtags'] = ''
df_urls['num_hashtags'] = 0
df_urls['num_urls'] = 0
df_urls['num_emojis'] = 0
df_urls['num_reacoes'] = 0
df_urls['gostei'] = 0
df_urls['parabens'] = 0
df_urls['amei'] = 0
df_urls['apoio'] = 0
df_urls['genial'] = 0
df_urls['engracado'] = 0
df_urls['num_comentarios'] = 0
df_urls['num_compartilhamentos'] = 0
df_urls['num_imagens'] = 0
df_urls['marcados'] = ''
df_urls['num_marcados'] = 0
df_urls['url_perfil'] = ''
df_urls['repost_autor'] = ''
df_urls['genero_autor'] = ''
df_urls['afiliacao_autor'] = ''
df_urls['tipo_postagem'] = ''


driver = webdriver.Chrome()

try:
    login_linkedin(driver)

    for index, row in df_urls.iterrows():
        url_post = row['url_post']
        dados_post = extrair_dados_post(driver, url_post)
        df_urls.at[index, 'nome_autor'] = dados_post.get('nome_autor', 'N/A')
        df_urls.at[index, 'cargo_autor'] = dados_post.get('cargo_autor', 'N/A')
        df_urls.at[index, 'local_trabalho'] = dados_post.get('local_trabalho', 'N/A')
        df_urls.at[index, 'texto_postagem'] = dados_post.get('texto_postagem', ' ')
        df_urls.at[index, 'idiomas_postagem'] = dados_post.get('idiomas_postagem', 'N/A')
        df_urls.at[index, 'tamanho_texto_postagem'] = dados_post.get('tamanho_texto_postagem', 0)
        df_urls.at[index, 'hashtags'] = dados_post.get('hashtags', '')
        df_urls.at[index, 'num_hashtags'] = dados_post.get('num_hashtags', 0)
        df_urls.at[index, 'num_urls'] = dados_post.get('num_urls', 0)
        df_urls.at[index, 'num_emojis'] = dados_post.get('num_emojis', 0)
        df_urls.at[index, 'num_reacoes'] = dados_post.get('num_reacoes', 0)
        df_urls.at[index, 'gostei'] = dados_post.get('gostei', 0)
        df_urls.at[index, 'parabens'] = dados_post.get('parabens', 0)
        df_urls.at[index, 'amei'] = dados_post.get('amei', 0)
        df_urls.at[index, 'apoio'] = dados_post.get('apoio', 0)
        df_urls.at[index, 'genial'] = dados_post.get('genial', 0)
        df_urls.at[index, 'engracado'] = dados_post.get('engracado', 0)
        df_urls.at[index, 'num_comentarios'] = dados_post.get('num_comentarios', 0)
        df_urls.at[index, 'num_compartilhamentos'] = dados_post.get('num_compartilhamentos', 0)
        df_urls.at[index, 'num_imagens'] = dados_post.get('num_imagens', 0)
        df_urls.at[index, 'marcados'] = dados_post.get('marcados', '')
        df_urls.at[index, 'num_marcados'] = dados_post.get('num_marcados', 0)
        df_urls.at[index, 'url_perfil'] = dados_post.get('url_perfil', 'N/A')
        df_urls.at[index, 'repost_autor'] = dados_post.get('repost_autor', 'Não é repost')
        nome_autor = dados_post.get('nome_autor', 'N/A')
        if nome_autor != 'N/A':
            genero_autor = detectar_genero_genderguesser(nome_autor)
            df_urls.at[index, 'genero_autor'] = genero_autor
        cargo_autor = dados_post.get('cargo_autor', 'N/A')
        afiliacao_autor = classificar_afiliacao(cargo_autor)
        df_urls.at[index, 'afiliacao_autor'] = afiliacao_autor
        tipo_postagem = classificar_tipo_postagem(cargo_autor)
        df_urls.at[index, 'tipo_postagem'] = tipo_postagem
finally:
    driver.quit()

novo_arquivo = f'posts_international conference on software engineering.xlsx-{datetime.today().strftime("%Y-%m-%dT%H%M%S")}.xlsx'
df_urls.to_excel(novo_arquivo, index=False)
print(f'Dados extraídos e salvos em: {novo_arquivo}')
