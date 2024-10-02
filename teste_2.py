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

def extrair_urls_posts(url):

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

        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'global-nav-typeahead')))
        driver.get(url)

        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(7)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(5)

        urls_posts = []

        posts = driver.find_elements(By.CLASS_NAME, 'feed-shared-update-v2')
        for post in posts:
            try:
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(3)

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

                    url_post = driver.execute_script("return navigator.clipboard.readText()")
                    urls_posts.append({'url_post': url_post})

            except Exception as e:
                print(e)
            time.sleep(1)

        df_urls = pd.DataFrame(urls_posts)
        nome_arquivo_urls = f'./urls_international-conference-on-software-engineering-{datetime.today().strftime("%Y-%m-%dT%H%M%S")}.xlsx'
        df_urls.to_excel(nome_arquivo_urls, index=False)
        print(f"URLs salvas em {nome_arquivo_urls}")

    finally:
        driver.quit()

# URL da pesquisa
url = 'https://www.linkedin.com/search/results/content/?keywords=%22international%20conference%20on%20software%20engineering%22&origin=FACETED_SEARCH&sid=K!g&sortBy=%22date_posted%22'
extrair_urls_posts(url)

