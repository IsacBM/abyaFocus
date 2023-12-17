import requests
import pandas as pd
import folium
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup
import os

# Desativar os avisos sobre certificado SSL
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# URL da página que contém os links para os arquivos CSV
url_pagina = 'https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/10min/'

# URL da imagem personalizada (substitua pela URL da imagem que você deseja usar)
url_imagem_fogo = 'https://cdn-icons-png.flaticon.com/512/8989/8989449.png'

# Função para baixar o arquivo CSV mais recente
def baixar_arquivo_csv(url_pagina):
    response = requests.get(url_pagina, verify=False)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        links_csv = soup.find_all('a', href=True)
        links_csv = [link for link in links_csv if link['href'].startswith('focos_10min_')]
        if links_csv:
            links_csv.sort(reverse=True, key=lambda link: link['href'])
            url_csv_mais_recente = 'https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/10min/' + links_csv[0]['href']
            response_csv = requests.get(url_csv_mais_recente, verify=False)
            if response_csv.status_code == 200:
                with open('focos_de_incendio.csv', 'wb') as arquivo:
                    arquivo.write(response_csv.content)
                print('Arquivo CSV baixado com sucesso:', url_csv_mais_recente)

                # Verifica se o arquivo contém coordenadas
                df = pd.read_csv('focos_de_incendio.csv')
                if 'lat' not in df.columns or 'lon' not in df.columns:
                    # O arquivo não contém coordenadas, tenta a versão anterior
                    baixar_versao_anterior(url_pagina, links_csv)
                else:
                    print('O arquivo CSV contém coordenadas.')
            else:
                print('Falha ao baixar o arquivo CSV:', response_csv.status_code)
        else:
            print('Nenhum arquivo CSV encontrado na página.')
    else:
        print('Falha ao acessar a página:', response.status_code)

# Função para baixar a versão anterior
def baixar_versao_anterior(url_pagina, links_csv):
    if len(links_csv) > 1:
        url_versao_anterior = 'https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/10min/' + links_csv[1]['href']
        response_versao_anterior = requests.get(url_versao_anterior, verify=False)
        if response_versao_anterior.status_code == 200:
            with open('focos_de_incendio.csv', 'wb') as arquivo:
                arquivo.write(response_versao_anterior.content)
            print('Arquivo CSV da versão anterior baixado com sucesso:', url_versao_anterior)
        else:
            print('Falha ao baixar o arquivo CSV da versão anterior:', response_versao_anterior.status_code)
    else:
        print('Não há versão anterior disponível.')

# Função para analisar coordenadas e exibir em um mapa
def analisar_e_exibir_mapa():
    # Ler o arquivo CSV
    df = pd.read_csv('focos_de_incendio.csv')

    # Extrair as coordenadas
    latitude = df['lat']
    longitude = df['lon']

    # Criar um mapa
    mapa = folium.Map(location=[latitude.mean(), longitude.mean()], zoom_start=5)

    # Adicionar marcadores para cada foco de incêndio com ícone personalizado
    for lat, lon in zip(latitude, longitude):
        folium.Marker([lat, lon], icon=folium.CustomIcon(icon_image=url_imagem_fogo, icon_size=(32, 32))).add_to(mapa)

    # Salvar o mapa em um arquivo HTML
    mapa.save('mapa_focos_de_incendio.html')
    print('Mapa gerado e coordenadas dos focos de incêndio exibidas.')

# Intervalo de 10 minutos (em segundos)
intervalo = 600

# Loop principal
while True:
    baixar_arquivo_csv(url_pagina)
    analisar_e_exibir_mapa()
    time.sleep(intervalo)
