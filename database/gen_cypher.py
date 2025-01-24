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

# Certifique-se de que o diretório de saída existe
os.makedirs(output_dir, exist_ok=True)
print(f"Gerando diretório: {output_dir}")

# Conectar ao banco de dados
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

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
    "periodos_letivos": {
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
        "attrs": ['registro_Academico', 'nome', 'data_matricula', 'data_conclusao', 'data_colacao'],
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

def gen_vertices():
    # Obter todos os nomes de tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table_name in tables:
        table_name = table_name[0]
        if table_name not in mapping_info.keys():
            print(f'! VERT: Tabela {table_name} não tem informações para gerar cypher')
            continue
        table_info = mapping_info[table_name]

        output_file = os.path.join(output_dir, f"{table_name}.cypher")

        # Selecionar os dados da tabela
        cursor.execute(f"SELECT * FROM {table_name}")

        # Obter os nomes das colunas que estão em mapping_info da tabela da itração
        column_names = []
        ok = False
        for description in cursor.description:
            if description[0] == 'id':
                ok = True
            if description[0] in table_info['attrs']:
                column_names.append(description[0])

        if not ok:
            print("! VERT: Tabela não tem coluna 'id', não vai ser gerado arquivo cypher")
            continue

        # Escrever os dados no arquivo cypher
        template = env.get_template('vertice_template.j2')

        data = {
            "table_name": table_name,
            "label": table_info["label"],
            "column_names": column_names,
        }

        with open(output_file, mode="w", newline="", encoding="utf-8") as cypher_file:
            print(template.render(data), file=cypher_file)
        print(f"# VERT: Arquivo de importação '{table_name}' gerado em '{output_file}'.")

    # Fechar a conexão
    conn.close()

def gen_edges():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Obtém a lista de tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    foreign_keys = {}

    # Pega informações sobre as relações, apenas de tabela que estão nas tabelas selecionadas
    for table_name in tables:
        # Verificaa se é uma das tabelas escolhidas
        if table_name not in mapping_info.keys():
            print(f'! EDGE: Tabela {table_name} não tem informações para gerar cypher')
            continue

        cursor.execute(f"PRAGMA foreign_key_list({table_name});")
        keys = cursor.fetchall()
        if keys:
            if len(list(filter(lambda keys: keys[2] in mapping_info.keys(), keys))) > 0:
                foreign_keys[table_name] = []
                for key in keys:
                    to_table = key[2]
                    foreign_keys[table_name].append({"from_column": key[3], "to_table": to_table, "to_column": key[4]})
                    print(f"# EDGE: Arquivo de importação '{table_name}_{to_table}' gerado em.")

    conn.close()
    for table, relations in foreign_keys.items():
        print(f"Tabela: {table}")
        for relation in relations:
            print(f"  Coluna: {relation['from_column']} -> Tabela: {relation['to_table']}, Coluna: {relation['to_column']}")


gen_edges()
print("Exportação concluída!")

