#! /usr/bin/python3
import sqlite3
import psycopg

import os
import sys
import csv
import json
from jinja2 import Environment, FileSystemLoader
import argparse
from urllib.parse import urlparse

root_dir = os.path.dirname(os.path.realpath(__file__))

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
    "--context",
    type=str,
    default="cypher",
    help="Caminho relativo que os scripts e arquivos csv vão usar (default: cypher)"
)
parser.add_argument(
    "--context-dir",
    type=str,
    default=root_dir,
    help=f"Diretório no qual vai ser criado o contexto (default: {root_dir})"
)
parser.add_argument(
    "--uri",
    type=str,
    default="file:development.sqlite3?mode=ro",
    help="URI de conexão com o banco de dados (default: file:development.sqlite3?mode=ro)"
)
parser.add_argument(
    "--dump",
    action="store_true",
    default=False,  # O valor padrão será False
    help="Indica de deve fazer o dump das tabelas para um arquivo csv"
)

args = parser.parse_args()
print(f"Banco de dados selecionado: {args.db}")
print(f"Diretório de saída: {args.context}")
print(f"URI de conexão: {args.uri}")

ROW_ID = "row_id"
MIGRATE_ALL_FILENAME = "migrate"

# Arquivos internos
templates_dir = os.path.join(root_dir, "templates")
sql_dir = os.path.join(root_dir, "sql")

# Saida do programs
output_dir = os.path.join(args.context_dir, args.context)
nodes_dir = os.path.join(output_dir, "nodes")
relations_dir = os.path.join(output_dir, "relations")
indexes_dir = os.path.join(output_dir, "indexes")
csv_dir = os.path.join(output_dir, "csv")


# Configuração do jinja2
file_loader = FileSystemLoader(templates_dir)
env = Environment(loader=file_loader, trim_blocks=True, lstrip_blocks=True)

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
    pks = [pk["column"].split(",") for pk in database_info["pk_info"] if pk["table"] == table_name]
    pks = sum(pks, [])
    # Adiciona campo de _row_id_ para tabelas sem Primary Keys
    if len(pks) <= 0:
        pks += [ROW_ID]
    return pks

def get_table_fk(database_info, table_name):
    return [pk["column"] for pk in database_info["fk_info"] if pk["table"] == table_name]

def get_table_foreign_info(database_info, table_name):
    return [{
        "from_column": fk["column"],
        "to_table": fk["reference_table"],
        "to_column": fk["reference_column"],
        "fk_name": fk["foreign_key_name"],
    } for fk in database_info["fk_info"] if fk["table"] == table_name]

def gen_nodes(database_info):
    # Obter todos os nomes de tabelas
    tables = get_tables_name(database_info)
    template = env.get_template('node_template.j2')

    for table_name in tables:
        table_pks = get_table_pk(database_info, table_name)
        table_fks = get_table_fk(database_info, table_name)
        table_columns = get_table_columns(database_info, table_name)

        # Retira as chaves privadas e foreigns
        column_names = list(set(table_columns).difference(set(table_pks)).difference(set(table_fks)))

        data = {
            "table_name": table_name,
            "label": LabelGenerator(table_name),
            "column_names": column_names,
            "table_pks": table_pks,
            "prefix": f"{args.context}/csv/",
        }

        # Escreve os dados no arquivo cypher
        output_file = os.path.join(nodes_dir, f"{table_name}.cypher")
        with open(output_file, mode="w", newline="", encoding="utf-8") as cypher_file:
            print(template.render(data), file=cypher_file)

        # Escreve dados no arquivo de migração geral
        print(template.render(data), file=MIGRATE_ALL_FILE)
        print(f"# NODE: Arquivo de importação '{table_name}' gerado em '{output_file}'.")

def gen_relations(database_info):
    # Obter todos os nomes de tabelas
    tables = get_tables_name(database_info)
    template = env.get_template('relation_template.j2')

    foreign_keys = {}

    # Pega informações sobre as relações, apenas de tabela que estão nas tabelas selecionadas
    for table_name in tables:
        foreign_keys = get_table_foreign_info(database_info, table_name)
        label1 = LabelGenerator(table_name)
        table_pks = get_table_pk(database_info, table_name)

        for fk in foreign_keys:
            to_table = fk["to_table"]
            fk_name = fk["fk_name"]
            label2 = LabelGenerator(to_table)

            data = {
                "table_name": table_name,
                "table1_label": label1,
                "table2_label": label2,
                "from_column": fk["from_column"],
                "to_column": fk["to_column"],
                "edge_label": LabelGenerator(fk_name),
                "table_pks": table_pks,
                "prefix": f"{args.context}/csv/",
            }

            # Escreve os dados no arquivo cypher
            output_file = os.path.join(relations_dir, f"{fk_name}.cypher")
            with open(output_file, mode="w", newline="", encoding="utf-8") as cypher_file:
                print(template.render(data), file=cypher_file)

            # Escreve dados no arquivo de migração geral
            print(template.render(data), file=MIGRATE_ALL_FILE)
            print(f"# RELATION: Arquivo de importação '{fk_name}' gerado em '{output_file}'.")

def gen_indexes(database_info):
    # Obter todos os nomes de tabelas
    tables = get_tables_name(database_info)
    template = env.get_template('node_index_template.j2')

    # Pega informações sobre as relações, apenas de tabela que estão nas tabelas selecionadas
    for table_name in tables:
        table_pks = get_table_pk(database_info, table_name)

        data = {
            "table_name": table_name,
            "label": LabelGenerator(table_name),
            "table_pks": table_pks,
        }

        # Escreve os dados no arquivo cypher
        output_file = os.path.join(indexes_dir, f"{table_name}.cypher")
        with open(output_file, mode="w", newline="", encoding="utf-8") as cypher_file:
            print(template.render(data), file=cypher_file)

        # Escreve dados no arquivo de migração geral
        print(template.render(data), file=MIGRATE_ALL_FILE)

        print(f"# INDEX: Arquivo de importação '{table_name}' gerado em '{output_file}'.")

# Pega os metadados sobre o banco de dados e armazena em um json
# Os dados coletados são de acordo com os scripts retirados dos scripts
# do https://chartdb.io/
#
# São eles:
# fk_info, pk_info, columns, indexes, tables, views, database_name, version
def get_sqlite_database_info():
    with open(os.path.join(sql_dir, 'get_sqlite_database_info.sql'), 'r') as sql_file:
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

def get_pg_database_info():
    with open(os.path.join(sql_dir, 'get_pg_database_info.sql'), 'r') as sql_file:
        sql_script = sql_file.read()

    database_info = {}
    with psycopg.connect(args.uri) as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql_script)
            database_info = json.loads(cursor.fetchone()[0])
    return database_info

def get_database_info():
    if args.db == "sqlite":
        return get_sqlite_database_info()
    elif args.db == "pg":
        return get_pg_database_info()
    else:
        print("[ERRO]: Não deveria chegar aqui")
        exit(1)

def sqlite_dump(database_info):
    conn = sqlite3.connect(args.uri, uri=True)
    cursor = conn.cursor()

    for table in get_tables_name(database_info):
        output_file = os.path.join(csv_dir, f"{table}.csv")
        table_columns = get_table_columns(database_info, table)
        cursor.execute(f"SELECT {",".join(table_columns)} FROM {table}")
        rows = cursor.fetchall()

        # Adiciona campo de _row_id_ para tabelas sem Primary Keys
        # Vai servir de id para os nodos
        table_columns = [ROW_ID] + table_columns
        for i,row in enumerate(rows):
            rows[i] = (i,)+row

        with open(output_file, mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file, quotechar="'")
            writer.writerow(table_columns)
            writer.writerows(rows)
        print(f"# DUMP: Fazendo dump da tabela '{table}' em '{output_file}'")

    conn.close()

def pg_dump(database_info):
    conn = psycopg.connect(args.uri)
    cursor = conn.cursor()

    for table_info in database_info["tables"]:
        table_name = table_info["table"]
        table_schema = table_info["schema"]

        output_file = os.path.join(csv_dir, f"{table_name}.csv")
        table_columns = get_table_columns(database_info, table_name)
        cursor.execute(f"SELECT {",".join(table_columns)} FROM {table_schema}.{table_name}")
        rows = cursor.fetchall()

        # Adiciona campo de _row_id_ para tabelas sem Primary Keys
        # Vai servir de id para os nodos
        table_columns = [ROW_ID] + table_columns
        for i,row in enumerate(rows):
            rows[i] = (i,)+row

        with open(output_file, mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(table_columns)
            writer.writerows(rows)
        print(f"# DUMP: Fazendo dump da tabela '{table_schema}.{table_name}' em '{output_file}'")

    conn.close()

def dump_database_csv(database_info):
    if args.db == "sqlite":
        sqlite_dump(database_info)
    elif args.db == "pg":
        pg_dump(database_info)
    else:
        print("[ERRO]: Não deveria chegar aqui")
        exit(1)

# Certifique-se de que o diretório de saída existem
os.makedirs(output_dir, exist_ok=True)
os.makedirs(nodes_dir, exist_ok=True)
os.makedirs(relations_dir, exist_ok=True)
os.makedirs(indexes_dir, exist_ok=True)
os.makedirs(csv_dir, exist_ok=True)

database_info = get_database_info()

if args.dump:
    dump_database_csv(database_info)


MIGRATE_ALL_FILEPATH = os.path.join(output_dir, f"{MIGRATE_ALL_FILENAME}.cypher")
MIGRATE_ALL_FILE = open(MIGRATE_ALL_FILEPATH, mode="w", newline="", encoding="utf-8")

print("# INDEX: Gerando arquivos de importação dos indexes")
gen_indexes(database_info)

# Espera para que todos os indexes sejam criados, ja que são criados assincronos
print("CALL db.awaitIndexes();", file=MIGRATE_ALL_FILE)

print("# NODE: Gerando arquivos de importação de nodes")
gen_nodes(database_info)

print("# RELATION: Gerando arquivos de importação de relations")
gen_relations(database_info)

MIGRATE_ALL_FILE.close()

print(f"Arquivo de transferência completo gerado em '{MIGRATE_ALL_FILEPATH}'")
print("Exportação concluída!")

