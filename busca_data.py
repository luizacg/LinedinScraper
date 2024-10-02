from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
from datetime import datetime, timezone
import time
import pandas as pd

def extrair_data_post_via_site(driver, post_url):
    try:
        driver.get('https://ollie-boyd.github.io/Linkedin-post-timestamp-extractor')
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'url')))
        input_field = driver.find_element(By.ID, 'url')
        input_field.clear()
        input_field.send_keys(post_url)
        button = driver.find_element(By.TAG_NAME, 'button')
        button.click()
        time.sleep(3)
        source = driver.page_source
        html_dom = bs(source.encode('utf-8'), 'html.parser')
        post_date_string = html_dom.find(id='date').get_text().strip()
        date_obj = datetime.strptime(post_date_string, '%a, %d %b %Y %H:%M:%S %Z (UTC)')
        return date_obj.date().isoformat()
    except Exception as e:
        print(f"Erro ao extrair data da URL {post_url}: {e}")
        return 'Erro ao extrair data'

arquivo_urls = 'posts_simposio-brasileiro-de-qualidade-de-software-2024-09-19T005544.xlsx'
df_urls = pd.read_excel(arquivo_urls)
df_urls['data_postagem'] = ''

driver = webdriver.Chrome()

try:
    for index, row in df_urls.iterrows():
        url_post = row['url_post']
        data_postagem = extrair_data_post_via_site(driver, url_post)
        df_urls.at[index, 'data_postagem'] = data_postagem
finally:
    driver.quit()

novo_arquivo = f'posts_simposio-brasileiro-de-qualidade-de-software_com_datas-{datetime.today().strftime("%Y-%m-%dT%H%M%S")}.xlsx'
df_urls.to_excel(novo_arquivo, index=False)
print(f'Dados extraídos e salvos em: {novo_arquivo}')
