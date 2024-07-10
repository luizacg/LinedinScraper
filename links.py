from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
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

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'global-nav-typeahead')))

        driver.get(url)

        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(7)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Scroll back to the top of the page
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)

        lista_posts = []

        # Capture page source after scrolling back to the top
        source = driver.page_source

        posts = driver.find_elements(By.CLASS_NAME, 'feed-shared-update-v2')
        for post in posts:
            publicacao = {}
            try:
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

                    publicacao['link'] = driver.execute_script("return navigator.clipboard.readText()")

            except Exception as e:
                print(e)

            lista_posts.append(publicacao)
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
