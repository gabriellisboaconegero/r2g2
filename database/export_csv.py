#! /usr/bin/python3
import sqlite3
import csv
import os
import sys

# Caminho para o banco de dados SQLite
db_path = "/var/lib/docker/volumes/adegadb-sqlite/_data/development.sqlite3"

if len(sys.argv) == 1:
    pass
elif len(sys.argv) == 2:
    db_path = sys.argv[1]
else:
    print(f"Usage: {sys.argv[0]} [file.sqlite3]")
    exit(1)

print(f"Usando banco: {db_path}")
root_dir = os.path.dirname(os.path.realpath(__file__))
output_dir = os.path.join(root_dir, "csv")

if not os.path.exists(db_path):
    print(f"Banco de dados [{db_path}] não existente")
    exit(1)

# Certifique-se de que o diretório de saída existe
os.makedirs(output_dir, exist_ok=True)
print(f"Gerando diretório: {output_dir}")

# Conectar ao banco de dados
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Obter todos os nomes de tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

for table_name in tables:
    table_name = table_name[0]
    output_file = os.path.join(output_dir, f"{table_name}.csv")

    # Selecionar os dados da tabela
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    # Obter os nomes das colunas
    column_names = [description[0] for description in cursor.description]

    # Escrever os dados no arquivo CSV
    with open(output_file, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(column_names)  # Escreve os nomes das colunas
        writer.writerows(rows)        # Escreve os dados das tabelas

    print(f"Tabela '{table_name}' exportada para '{output_file}'.")

# Fechar a conexão
conn.close()

print("Exportação concluída!")

