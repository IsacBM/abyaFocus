import geopandas as gpd

# Carregue o GeoJSON
gdf = gpd.read_file('nordeste-indigena/indigena-nordeste.geojson')

# Simplifique as geometrias
gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.015)

# Salve o GeoJSON simplificado
gdf.to_file('nordeste-indigena/indigena-nordeste.geojson', driver='GeoJSON')
