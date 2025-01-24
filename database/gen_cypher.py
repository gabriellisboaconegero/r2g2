#! /usr/bin/python3
import sqlite3
import csv
import os
import sys
from jinja2 import Environment, FileSystemLoader

# Configuração do jinja2
file_loader = FileSystemLoader('.')
env = Environment(loader=file_loader, trim_blocks=True, lstrip_blocks=True)

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
output_dir = os.path.join(root_dir, "cypher")
nodes_dir = os.path.join(output_dir, "nodes")
relations_dir = os.path.join(output_dir, "relations")

# Certifique-se de que o diretório de saída existe
os.makedirs(output_dir, exist_ok=True)
os.makedirs(nodes_dir, exist_ok=True)
os.makedirs(relations_dir, exist_ok=True)
print(f"Gerando diretório: {output_dir}")

# Informações de quais tabelas importar e quais colunas importar.
#   "<table>": {
#       "attrs": ['nome', 'peiodo'],
#       "label": "<Lable>"
#   }
mapping_info = {
    # ---------- Tabelas Fixas ----------
    "turnos": {
        "attrs": ['nome'],
        "label": "Turno",
    },
    "graus": {
        "attrs": ['nome'],
        "label": "Grau",
    },
    "resultado_disciplinas": {
        "attrs": ['nome'],
        "label": "ResultadoDisciplina",
    },
    "situacao_disciplinas": {
        "attrs": ['nome'],
        "label": "SituacaoDisciplina",
    },
    "natureza_disciplinas": {
        "attrs": ['nome'],
        "label": "NaturezaDisciplina",
    },
    "forma_evasaos": {
        "attrs": ['nome'],
        "label": "FormaEvasao",
    },
    "forma_ingressos": {
        "attrs": ['nome'],
        "label": "FormaIngresso",
    },
    # ---------- Tabelas Fixas ----------
    # ---------- Tabelas ----------
    "periodo_letivos": {
        "attrs": ['ano', 'periodo'],
        "label": "PeriodoLetivo",
    },
    "cursos": {
        "attrs": ['nome', 'habilitacao'],
        "label": "Curso",
    },
    "turmas": {
        "attrs": ['codigo'],
        "label": "Turma",
    },
    "disciplinas": {
        "attrs": ['nome', 'carga_horaria', 'codigo', 'numero', 'tcc', 'estagio' ],
        "label": "Disciplina",
    },
    "historicos": {
        "attrs": ['nota', 'frequencia'],
        "label": "Historico",
    },
    "alunos": {
        "attrs": ['registro_academico', 'nome', 'data_matricula', 'data_conclusao', 'data_colacao', 'ira', 'data_colacao'],
        "label": "Aluno",
    },
    "curriculos": {
        "attrs": ['nome', 'codigo_externo', 'versao'],
        "label": "Curriculo",
    },
    "grades": {
        "attrs": ['linha', 'coluna', 'texto'],
        "label": "Grade",
    },
    "elencos": {
        "attrs": ['codigo', 'nome'],
        "label": "Elenco",
    },
}

def get_tables_name(cursor):
    cursor.execute("select name from pragma_table_list where schema='main'")
    return [row[0] for row in cursor.fetchall()]

# 'PRAGMA table_info({table})' schema:
#  0     1      2        3            4          5
# cid | name | type | notnull | default_value | pk
# Retirado de https://www.sqlite.org/pragma.html#pragma_table_info
# """
# This pragma returns one row for each normal column in the named table. Columns in the result set include:
# "name" (its name);
# "type" (data type if given, else '');
# "notnull" (whether or not the column can be NULL);
# "dflt_value" (the default value for the column); and
# "pk" (either zero for columns that are not part of the primary key, or the 1-based index of the column within the primary key).

# The "cid" column should not be taken to mean more than "rank within the current result set".
# """
def get_table_columns(cursor, table):
    cursor.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cursor.fetchall()]

def get_table_pk(cursor, table):
    cursor.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cursor.fetchall() if row[5] == 1]

def get_table_foreign_info(cursor, table_name):
    cursor.execute(f"PRAGMA foreign_key_list({table_name});")
    return [{
        "from_column": key[3],
        "to_table": key[2],
        "to_column": key[4]
    } for key in cursor.fetchall() if key[2] in mapping_info.keys()]

def gen_nodes():
    # Conectar ao banco de dados
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Obter todos os nomes de tabelas
    tables = get_tables_name(cursor)

    for table_name in tables:
        if table_name not in mapping_info.keys():
            print(f'! NODE: Tabela {table_name} não tem informações para gerar cypher')
            continue
        table_info = mapping_info[table_name]

        table_columns = get_table_columns(cursor, table_name)
        table_pks = set(get_table_pk(cursor, table_name))

        # Obter os nomes das colunas que estão em mapping_info da tabela da itração
        # e retira as que são chaves primarias
        column_names = set({})
        for col in table_columns:
            if col in table_info['attrs']:
                column_names.add(col)
        column_names = column_names.difference(table_pks)

        # Escrever os dados no arquivo cypher
        template = env.get_template('node_template.j2')

        data = {
            "table_name": table_name,
            "label": table_info["label"],
            "column_names": list(column_names),
            "table_pks": list(table_pks),
        }

        output_file = os.path.join(nodes_dir, f"{table_name}.cypher")
        with open(output_file, mode="w", newline="", encoding="utf-8") as cypher_file:
            print(template.render(data), file=cypher_file)
        print(f"# NODE: Arquivo de importação '{table_name}' gerado em '{output_file}'.")

    # Fechar a conexão
    conn.close()

def gen_relations():
    # Conectar ao banco de dados
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Obter todos os nomes de tabelas
    tables = get_tables_name(cursor)

    foreign_keys = {}

    # Pega informações sobre as relações, apenas de tabela que estão nas tabelas selecionadas
    for table_name in tables:
        # Verificaa se é uma das tabelas escolhidas
        if table_name not in mapping_info.keys():
            print(f'! RELATION: Tabela {table_name} não tem informações para gerar cypher')
            continue

        foreign_keys = get_table_foreign_info(cursor, table_name)
        # Escrever os dados no arquivo cypher
        template = env.get_template('relation_template.j2')
        label1 = mapping_info[table_name]["label"]

        for fk in foreign_keys:
            to_table = fk["to_table"]

            label2 = mapping_info[to_table]["label"]
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

    conn.close()

print("# NODE: Gerando arquivos de importação de nodes")
gen_nodes()
print("# RELATION: Gerando arquivos de importação de relations")
gen_relations()
print("Exportação concluída!")

