import os
import requests
import pandas as pd
import geopandas as gpd
import folium
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# URL da página que contém os links para os arquivos CSV
url_pagina = 'https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/10min/'

# URL da imagem personalizada
# url_imagem_fogo = 'https://cdn-icons-png.flaticon.com/512/8989/8989449.png'
url_imagem_fogo = 'img/fogo-icon.svg'

# Caminho para o arquivo GeoJSON do Piauí
piaui_geojson = 'limite-piaui/br_pi.json'

# Caminho para o arquivo shapefile do Brasil
brasil_shapefile = 'limite-do-brasil/BR_Pais_2022.shp'

# Caminho para o arquivo CSV padrão
arquivo_csv_padrao = 'focos-base-10-10.csv'

# Caminho para o arquivo shapefile dos Parques Nacionais
parques_nacionais_shapefile = 'protecao-integral/ucsfi.shp'

#terras_indigenas_shapefile = 'areas-indigenas/tis_poligonais.shp'

url_imagem_piaui = 'img/marca.png'
url_imagem_verde = 'img/verde.png'
url_imagem_rosa = 'img/rosa.png'
url_imagem_parques = 'img/parque.png'

# Função para baixar o arquivo CSV mais recente ou usar o padrão
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
            if response_csv.status_code == 200 and len(response_csv.content) > 22:  # Verifique o tamanho do arquivo
                with open('focos_de_incendio.csv', 'wb') as arquivo:
                    arquivo.write(response_csv.content)
                print('Arquivo CSV baixado com sucesso:', url_csv_mais_recente)
                df = pd.read_csv('focos_de_incendio.csv')
                if not verificar_coordenadas_validas(df) or df.empty:
                    print('O arquivo focos_de_incendio.csv contém coordenadas inválidas ou está vazio.')
                    print('Carregando o arquivo CSV padrão...')
                    df = carregar_arquivo_csv_padrao()
                else:
                    print('O arquivo CSV contém coordenadas.')
                filtrar_por_regiao(df)
            else:
                print('Falha ao baixar o arquivo CSV:', response_csv.status_code)
        else:
            print('Nenhum arquivo CSV encontrado na página.')
    else:
        print('Falha ao acessar a página:', response.status_code)

# Função para carregar o arquivo CSV padrão
def carregar_arquivo_csv_padrao():
    if os.path.isfile(arquivo_csv_padrao):
        df_padrao = pd.read_csv(arquivo_csv_padrao)
        return df_padrao
    else:
        print('O arquivo CSV padrão não foi encontrado.')
        return pd.DataFrame()  # Retorna um DataFrame vazio

# Função para verificar se os dados contêm coordenadas válidas
def verificar_coordenadas_validas(df):
    return 'lat' in df.columns and 'lon' in df.columns

# Função para filtrar os focos de incêndio somente no Brasil
def filtrar_por_regiao(df):
    # Carregar o shapefile do Brasil usando geopandas
    gdf_brasil = gpd.read_file(brasil_shapefile)

    # Converter as coordenadas em um GeoDataFrame
    gdf_focos = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat))

    # Definir um CRS para gdf_focos (por exemplo, EPSG:4326 para lat/lon)
    gdf_focos.set_crs(epsg=4326, inplace=True)

    # Realizar a interseção espacial para encontrar os focos de incêndio no Brasil
    focos_brasil = gpd.sjoin(gdf_focos, gdf_brasil, op='intersects')

    # Salvar os focos de incêndio no Brasil em um arquivo CSV
    focos_brasil.to_csv('focos_brasil.csv', index=False)
    print('Focos de incêndio no Brasil filtrados e salvos no arquivo "focos_brasil.csv."')

# Função para adicionar os Parques Nacionais ao mapa
def adicionar_parques_nacionais(mapa):
    # Carregar o shapefile dos Parques Nacionais
    gdf_parques_nacionais = gpd.read_file(parques_nacionais_shapefile)

    # Define a projeção (CRS) para o gdf_parques_nacionais
    gdf_parques_nacionais.crs = 'EPSG:4326'

    # Adicionar os Parques Nacionais ao mapa
    folium.GeoJson(gdf_parques_nacionais, name='Parques Nacionais', style_function=lambda x: {'color': 'green'}).add_to(mapa)

# Função para adicionar os Parques Nacionais ao mapa
#def adicionar_terras_indigenas(mapa):
    # Carregar o shapefile dos Parques Nacionais
    #gdf_parques_nacionais = gpd.read_file(terras_indigenas_shapefile)

    # Define a projeção (CRS) para o gdf_parques_nacionais
    #gdf_parques_nacionais.crs = 'EPSG:4326'

    # Adicionar os Parques Nacionais ao mapa
    #folium.GeoJson(gdf_parques_nacionais, name='Terras Indígenas', style_function=lambda x: {'color': 'yellow'}).add_to(mapa)

# Função para adicionar uma legenda personalizada ao mapa
def adicionar_rosa(mapa):
    rosa_html = '''
    <div style="position: fixed; top: 15px; right: 15px; width: 80px; height: 80px; z-index:9999; font-size:14px;">
    <p style="margin: 1.5px;"><img src="''' + url_imagem_rosa + '''" width="80" height="80"></p>
    </div>
    '''

    mapa.get_root().html.add_child(folium.Element(rosa_html))

# Função para adicionar uma legenda personalizada ao mapa
def adicionar_legenda(mapa):
    legend_html = '''
    <head>
        <link rel="shortcut icon" href="https://cdn-icons-png.flaticon.com/512/708/708290.png" type="image/x-icon">
    </head>
    <title>Abya Focos - Focos de Incêndio no Brasil</title>
    <div style="position: fixed; bottom: 15px; left: 15px; width: 210px; height: 180px; border:2px solid grey; z-index:9999; font-size:14px; background-color: rgba(255, 255, 255, 0.8); border-radius:10px;">
    <p style="text-align:center; padding: 2.5px;"><b>Legenda</b></p>
    <p style="padding: 0.5px;"><img src="''' + url_imagem_fogo + '''" width="20" height="20"> Focos de Incêndio</p>
    <p style="padding: 0.5px;"><img src="''' + url_imagem_parques + '''" width="20" height="20"> Parques Nacionais</p>
    <p style="padding: 0.5px;"><img src="''' + url_imagem_verde + '''" width="20" height="20"> Unidades de Conservação <br> (Federais - Integral)</p>
    <p style="padding: 0.5px;"><img src="''' + url_imagem_piaui + '''" width="20" height="20"> Marcação do Piauí</p>
    </div>
    '''

    mapa.get_root().html.add_child(folium.Element(legend_html))

# Função para analisar coordenadas e exibir em um mapa com legenda
def analisar_e_exibir_mapa():
    # Tentar ler o arquivo CSV baixado
    try:
        df = pd.read_csv('focos_brasil.csv')
        if not verificar_coordenadas_validas(df) or df[['lat', 'lon']].isnull().values.any():
            print('O arquivo focos_brasil.csv contém coordenadas inválidas ou está vazio.')
            print('Carregando o arquivo CSV padrão...')
            df = pd.read_csv(arquivo_csv_padrao)
    except FileNotFoundError:
        print('O arquivo focos_brasil.csv não foi encontrado.')
        print('Carregando o arquivo CSV padrão...')
        df = pd.read_csv(arquivo_csv_padrao)

    # Verificar se as coordenadas são válidas e não estão ausentes (NaN)
    if verificar_coordenadas_validas(df) and not df[['lat', 'lon']].isnull().values.any():
        # Extrair as coordenadas
        latitude = df['lat']
        longitude = df['lon']

        # Verificar se há pelo menos uma coordenada válida
        if not latitude.isnull().all() and not longitude.isnull().all():
            # Criar um mapa
            mapa = folium.Map(location=[latitude.mean(), longitude.mean()], zoom_start=5)
            
            # Adicionar os Parques Nacionais ao mapa
            adicionar_parques_nacionais(mapa)
            #adicionar_terras_indigenas(mapa)

            # Adicionar marcadores para cada foco de incêndio com ícone personalizado
            for lat, lon in zip(latitude, longitude):
                if not pd.isna(lat) and not pd.isna(lon):
                    folium.Marker([lat, lon], icon=folium.CustomIcon(icon_image='img/icone-de-fogo.svg', icon_size=(32, 32))).add_to(mapa)

            # Adicionar o Piauí ao mapa com opacidade
            folium.GeoJson(
                piaui_geojson, name='Piauí',
                style_function=lambda x: {'color': 'blue', 'opacity': 0.7}
            ).add_to(mapa)

            # Adicionar a legenda ao mapa
            adicionar_rosa(mapa)
            adicionar_legenda(mapa)

            df_coord = pd.read_csv('parques/parques-nacionais.csv')
            for index, row in df_coord.iterrows():
                latitude = row['lat']
                longitude = row['lon']
                if not pd.isna(latitude) and not pd.isna(longitude):
                    folium.Marker([latitude, longitude], icon=folium.CustomIcon(icon_image=url_imagem_parques, icon_size=(48, 52))).add_to(mapa)

            # Salvar o mapa em um arquivo HTML
            mapa.save('mapa_focos_de_incendio_com_legenda.html')
            print('Mapa gerado e coordenadas dos focos de incêndio no Brasil exibidas.')
        else:
            print('Não há coordenadas válidas para criar o mapa.')
    else:
        print('Não há coordenadas válidas para criar o mapa.')

# Intervalo de 10 minutos (em segundos)
intervalo = 600

# Loop principal
while True:
    baixar_arquivo_csv(url_pagina)
    analisar_e_exibir_mapa()
    time.sleep(intervalo)
