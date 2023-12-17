import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt

# 1. Ler os dados do arquivo CSV
df = pd.read_csv('base-focos-20231010.csv')

# 2. Transformar o DataFrame em um GeoDataFrame
geometry = [Point(lon, lat) for lon, lat in zip(df['lon'], df['lat'])]
gdf = gpd.GeoDataFrame(df, geometry=geometry)

# 3. Ler o shapefile da região de interesse
regiao = gpd.read_file('protecao-integral/ucsfi.shp')

# 4. Filtrar os dados na região
dados_na_regiao = gdf[gdf.intersects(regiao.unary_union)]

# 5. Verificar se há dados após a filtragem
print("Número de registros após a filtragem:", len(dados_na_regiao))

# 6. Agrupar os dados por data
dados_agrupados = dados_na_regiao.groupby('data').size().reset_index(name='focos_diarios')

# 7. Verificar os dados agrupados
print(dados_agrupados)

# 8. Criar o gráfico
plt.plot(dados_agrupados['data'], dados_agrupados['focos_diarios'])
plt.xlabel('Data')
plt.ylabel('Quantidade de Focos Diários')
plt.title('Focos de Incêndio na Região de Interesse')

# 9. Salvar o gráfico como uma imagem (por exemplo, PNG)
plt.savefig('grafico_focos_incendio.png')

# 10. Mostrar o gráfico
plt.show()
