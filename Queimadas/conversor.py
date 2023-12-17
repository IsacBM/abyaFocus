import geopandas as gpd

# Substitua 'seu_arquivo_shapefile.shp' pelo caminho do seu arquivo Shapefile
shapefile_path = 'shape-municipal/PI_Municipios_2022.shp'

# Carregue o Shapefile em um GeoDataFrame
gdf = gpd.read_file(shapefile_path)

# Substitua 'seu_arquivo_geojson.geojson' pelo caminho do arquivo GeoJSON de saída
geojson_path = 'PI-Municipios.geojson'

# Salve o GeoDataFrame como um arquivo GeoJSON
gdf.to_file(geojson_path, driver='GeoJSON')

print(f'Arquivo GeoJSON salvo em: {geojson_path}')
