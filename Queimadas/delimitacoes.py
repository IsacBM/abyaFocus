import geopandas as gpd
import fiona

# Caminho para o arquivo Shapefile que delimita a área de interesse
area_shapefile = 'limite-do-brasil/nordeste-brasil/nordeste.shp'

# Caminho para o arquivo GeoJSON com as unidades de conservação
uc_geojson_file = 'area-indigena.geojson'

# Carregue o Shapefile da área de interesse
gdf_area = gpd.read_file(area_shapefile)

# Carregue o arquivo GeoJSON com as unidades de conservação
gdf_uc = gpd.read_file(uc_geojson_file)

# Faça a interseção entre o Shapefile da área de interesse e as unidades de conservação
uc_within_area = gpd.overlay(gdf_uc, gdf_area, how='intersection')

# Caminho para o novo arquivo Shapefile com as unidades de conservação dentro da área de interesse
output_shapefile = 'indigena-nordeste.shp'

# Salve o resultado da interseção em um novo arquivo Shapefile
uc_within_area.to_file(output_shapefile)
