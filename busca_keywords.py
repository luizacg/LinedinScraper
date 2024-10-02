from selenium import webdriver
from bs4 import BeautifulSoup as bs
from datetime import datetime
import pandas as pd
from rake_nltk import Rake

def extrair_palavras_chave(texto):
    if not isinstance(texto, str) or len(texto.strip()) == 0:
        return 'Sem texto'
    rake = Rake()
    rake.extract_keywords_from_text(texto)
    palavras_chave = rake.get_ranked_phrases()
    return ', '.join(palavras_chave)

arquivo_urls = 'urls_posts_atualizados-2024-09-16T213754.xlsx'
df_urls = pd.read_excel(arquivo_urls)

df_urls['palavras_chave'] = ''

for index, row in df_urls.iterrows():
    texto_postagem = row['texto_postagem']
    palavras_chave = extrair_palavras_chave(texto_postagem)
    df_urls.at[index, 'palavras_chave'] = palavras_chave

novo_arquivo = f'urls_posts_atualizados_com_palavras_chave-{datetime.today().strftime("%Y-%m-%dT%H%M%S")}.xlsx'
df_urls.to_excel(novo_arquivo, index=False)
print(f'Dados extraídos e salvos em: {novo_arquivo}')
