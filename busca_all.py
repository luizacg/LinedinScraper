import os
import pandas as pd

def combinar_arquivos_excel(diretorio_arquivos):
    dataframes = []
    for arquivo in os.listdir(diretorio_arquivos):
        if arquivo.endswith('.xlsx'):
            caminho_arquivo = os.path.join(diretorio_arquivos, arquivo)
            df = pd.read_excel(caminho_arquivo)
            dataframes.append(df)
    df_combinado = pd.concat(dataframes, ignore_index=True)
    arquivo_saida = os.path.join(diretorio_arquivos, 'arquivo_combinado.xlsx')
    df_combinado.to_excel(arquivo_saida, index=False)
    print(f"Todos os arquivos foram concatenados em: {arquivo_saida}")

diretorio_arquivos = r'\Users\user\Desktop\mçm\LinkedinScrape'

combinar_arquivos_excel(diretorio_arquivos)
