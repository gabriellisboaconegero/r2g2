#! /usr/bin/python3
import sqlite3
import csv
import os

# Caminho para o banco de dados SQLite
db_path = "development.sqlite3"
output_dir = "cypher"  # Diretório para salvar os arquivos CSV

# Certifique-se de que o diretório de saída existe
os.makedirs(output_dir, exist_ok=True)

# Conectar ao banco de dados
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Informações de quais tabelas importar e quais colunas importar.
#   "<table>": {
#       "attrs": ['nome', 'peiodo'],
#       "label": "<Lable>"
#   }
tables_info = {
    # ---------- Tabelas Fixas ----------
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
    "turnos": {
        "attrs": ['nome'],
        "label": "Turno",
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

# Obter todos os nomes de tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

for table_name in tables:
    table_name = table_name[0]
    if table_name not in tables_info.keys():
        print(f'! Tabela {table_name} não tem informações para gerar cypher')
        continue
    table_info = tables_info[table_name]

    output_file = os.path.join(output_dir, f"{table_name}.cypher")

    # Selecionar os dados da tabela
    cursor.execute(f"SELECT * FROM {table_name}")

    # Obter os nomes das colunas que estão em tables_info da tabela da itração
    column_names = []
    ok = False
    for description in cursor.description:
        if description[0] == 'id':
            ok = True
        if description[0] in table_info['attrs']:
            column_names.append(description[0])

    if not ok:
        print("! Tabela não tem coluna 'id', não vai ser gerado arquivo cypher")
        continue

    # Escrever os dados no arquivo cypher
    with open(output_file, mode="w", newline="", encoding="utf-8") as cypher_file:
        # print(f"// {table_name}", file=cypher_file)
        print(f"LOAD CSV WITH HEADERS FROM 'file:///{table_name}.csv' AS row", file=cypher_file)
        label = table_info["label"]
        print(f"MERGE (x:{label} {{id: row.id}})", file=cypher_file)
        if len(column_names) > 0:
            print(f"ON CREATE SET", file=cypher_file)
            for i in range(len(column_names)-1):
                print(f"    x.{column_names[i]} = row.{column_names[i]},", file=cypher_file)
            print(f"    x.{column_names[-1]} = row.{column_names[-1]}", file=cypher_file)
        print(f"RETURN x;", file=cypher_file)

    print(f"# Arquivo de importação '{table_name}' gerado em '{output_file}'.")

# Fechar a conexão
conn.close()

print("Exportação concluída!")

