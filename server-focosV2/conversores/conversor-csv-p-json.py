import csv
import json

# Nome do arquivo CSV de entrada
input_csv = 'parques-nordeste.csv'

# Nome do arquivo JSON de saída
output_json = 'parques-nordeste.json'

# Lista para armazenar os dados
data = []

# Ler o arquivo CSV
with open(input_csv, mode='r', encoding='utf-8') as csvfile:
    csvreader = csv.DictReader(csvfile)
    for row in csvreader:
        data.append(row)

# Escrever os dados no arquivo JSON
with open(output_json, mode='w', encoding='utf-8') as jsonfile:
    json.dump(data, jsonfile, ensure_ascii=False, indent=4)

print(f'Arquivo {output_json} gerado com sucesso.')