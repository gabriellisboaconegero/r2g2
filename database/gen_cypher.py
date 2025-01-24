#! /usr/bin/python3
import sqlite3

import os
import sys
import json
from jinja2 import Environment, FileSystemLoader
import argparse
from urllib.parse import urlparse

# Configuração do jinja2
file_loader = FileSystemLoader('.')
env = Environment(loader=file_loader, trim_blocks=True, lstrip_blocks=True)

# Configuração da linha de comando
parser = argparse.ArgumentParser(
    description="Script para gerar código cypher para importar dados de um banco de dados SQLite ou PostgreSQL para Neo4j"
)
parser.add_argument(
    "--db",
    choices=["sqlite", "pg"],
    default="sqlite",
    help="Tipo de banco de dados (default: sqlite)"
)
parser.add_argument(
    "--out-dir",
    type=str,
    default="cypher",
    help="Diretório de saída para salvar os scripts cypher (default: cypher)"
)
parser.add_argument(
    "--uri",
    type=str,
    default="file:development.sqlite3?mode=ro",
    help="URI de conexão com o banco de dados (default: file:development.sqlite3?mode=ro)"
)

args = parser.parse_args()
print(f"Banco de dados selecionado: {args.db}")
print(f"Diretório de saída: {args.out_dir}")
print(f"URI de conexão: {args.uri}")

root_dir = os.path.dirname(os.path.realpath(__file__))
output_dir = os.path.join(root_dir, args.out_dir)
nodes_dir = os.path.join(output_dir, "nodes")
relations_dir = os.path.join(output_dir, "relations")
indexes_dir = os.path.join(output_dir, "indexes")

def LabelGenerator(label_seed):
    words = label_seed.title().split('_')
    if words[-1][-1] == 's':
        words[-1] = words[-1][:-1]
    return "".join(words)

def get_tables_name(database_info):
    return [table["table"] for table in database_info["tables"]]

def get_table_columns(database_info, table_name):
    return [col["name"] for col in database_info["columns"] if col["table"] == table_name]


def get_table_pk(database_info, table_name):
    return [pk["column"] for pk in database_info["pk_info"] if pk["table"] == table_name]

def get_table_foreign_info(database_info, table_name):
    return [{
        "from_column": fk["column"],
        "to_table": fk["reference_table"],
        "to_column": fk["reference_column"],
    } for fk in database_info["fk_info"] if fk["table"] == table_name]

def gen_nodes(database_info):
    # Obter todos os nomes de tabelas
    tables = get_tables_name(database_info)
    template = env.get_template('node_template.j2')

    for table_name in tables:
        # if table_name not in mapping_info.keys():
        #     print(f'! NODE: Tabela {table_name} não tem informações para gerar cypher')
        #     continue

        table_pks = get_table_pk(database_info, table_name)
        table_columns = get_table_columns(database_info, table_name)
        column_names = list(set(table_columns).difference(set(table_pks)))

        # Escrever os dados no arquivo cypher

        data = {
            "table_name": table_name,
            "label": LabelGenerator(table_name),
            "column_names": column_names,
            "table_pks": table_pks,
        }

        if len(table_pks) > 0:
            output_file = os.path.join(nodes_dir, f"{table_name}.cypher")
            with open(output_file, mode="w", newline="", encoding="utf-8") as cypher_file:
                print(template.render(data), file=cypher_file)
            print(f"# NODE: Arquivo de importação '{table_name}' gerado em '{output_file}'.")
        else:
            print(f"! NODE: Tabela {table_name} não tem chave primária.")

def gen_relations(database_info):
    # Obter todos os nomes de tabelas
    tables = get_tables_name(database_info)
    template = env.get_template('relation_template.j2')

    foreign_keys = {}

    # Pega informações sobre as relações, apenas de tabela que estão nas tabelas selecionadas
    for table_name in tables:
        # Verificaa se é uma das tabelas escolhidas
        # if table_name not in mapping_info.keys():
        #     print(f'! RELATION: Tabela {table_name} não tem informações para gerar cypher')
        #     continue

        foreign_keys = get_table_foreign_info(database_info, table_name)
        # Escrever os dados no arquivo cypher
        label1 = LabelGenerator(table_name)

        for fk in foreign_keys:
            to_table = fk["to_table"]
            label2 = LabelGenerator(to_table)
            data = {
                "table_name": table_name,
                "table1_label": label1,
                "table2_label": label2,
                "from_column": fk["from_column"],
                "to_column": fk["to_column"],
                "edge_label": f"{label1}To{label2}",
            }
            output_file = os.path.join(relations_dir, f"{table_name}-{to_table}.cypher")
            with open(output_file, mode="w", newline="", encoding="utf-8") as cypher_file:
                print(template.render(data), file=cypher_file)
            print(f"# RELATION: Arquivo de importação '{table_name}-{to_table}' gerado em '{output_file}'.")

def gen_indexes(database_info):
    # Obter todos os nomes de tabelas
    tables = get_tables_name(database_info)
    template = env.get_template('node_index_template.j2')

    # Pega informações sobre as relações, apenas de tabela que estão nas tabelas selecionadas
    for table_name in tables:
        # Verificaa se é uma das tabelas escolhidas
        # if table_name not in mapping_info.keys():
        #     print(f'! INDEX: Tabela {table_name} não tem informações para gerar cypher')
        #     continue

        table_pks = get_table_pk(database_info, table_name)
        # Escrever os dados no arquivo cypher
        data = {
            "table_name": table_name,
            "label": LabelGenerator(table_name),
            "table_pks": table_pks,
        }

        if len(table_pks) > 0:
            output_file = os.path.join(indexes_dir, f"{table_name}.cypher")
            with open(output_file, mode="w", newline="", encoding="utf-8") as cypher_file:
                print(template.render(data), file=cypher_file)
            print(f"# INDEX: Arquivo de importação '{table_name}' gerado em '{output_file}'.")
        else:
            print(f"! INDEX: Tabela {table_name} não tem chave primária.")


def get_sqlite_database_info():
    with open('get_sqlite_database_info.sql', 'r') as sql_file:
        sql_script = sql_file.read()

    database_info = {}
    result = urlparse(args.uri)
    if not os.path.exists(result.path):
        print(f"[ERRO]: URI [{args.uri}] incorreta, arquivo do banco {result.path} não existe")
        exit(1)
    conn = sqlite3.connect(args.uri, uri=True)
    cursor = conn.cursor()
    cursor.execute(sql_script)
    database_info = json.loads(cursor.fetchone()[0])
    conn.close()

    return database_info

def get_database_info():
    if args.db == "sqlite":
        return get_sqlite_database_info()
    else:
        print("[ERRO]: Não deveria chegar aqui")
        exit(1)

database_info = get_database_info()

# Certifique-se de que o diretório de saída existe
os.makedirs(output_dir, exist_ok=True)
os.makedirs(nodes_dir, exist_ok=True)
os.makedirs(relations_dir, exist_ok=True)
os.makedirs(indexes_dir, exist_ok=True)

print("# NODE: Gerando arquivos de importação de nodes")
gen_nodes(database_info)
print("# INDEX: Gerando arquivos de importação dos indexes")
gen_indexes(database_info)
print("# RELATION: Gerando arquivos de importação de relations")
gen_relations(database_info)
print("Exportação concluída!")

