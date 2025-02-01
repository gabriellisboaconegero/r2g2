import os
import argparse
from neo4j import GraphDatabase
import time

root_dir = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser(
    description="Script para importar dados de um banco de dados SQLite ou PostgreSQL para Neo4j"
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
    help=f"Diretório no qual o contexto está (default: {root_dir})"
)
parser.add_argument(
    "--uri",
    type=str,
    default="bolt://localhost:7687",
    help="URI de conexão com o neo4j (default: bolt://localhost:7687)"
)
parser.add_argument(
    "--user",
    type=str,
    default="neo4j",
    help="usuário de conexão com o neo4j (default: neo4j)"
)
parser.add_argument(
    "--password",
    type=str,
    default="teste123",
    help="Senha do usuário de conexão com o neo4j (default: teste123)"
)

args = parser.parse_args()
print(f"Diretório de scripts: {args.context}")
print(f"URI de conexão: {args.uri}")
print(f"Usuário de conexão: {args.user}")


# Arquivos internos
templates_dir = os.path.join(root_dir, "templates")
sql_dir = os.path.join(root_dir, "sql")

# Saida do programs
output_dir = os.path.join(args.context_dir, args.context)
nodes_dir = os.path.join(output_dir, "nodes")
relations_dir = os.path.join(output_dir, "relations")
indexes_dir = os.path.join(output_dir, "indexes")
csv_dir = os.path.join(output_dir, "csv")

driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))

total_time = 0
total_summary = {
    'nodes_created': 0,
    'relationships_created': 0,
}

def run_cypher_file(file_path):
    global total_time, total_nodes_created, total_relations_created
    with driver.session() as session:
        with open(file_path, "r") as file:
            cypher_query = file.read()
            inicio = time.time()
            summary = session.run(cypher_query).consume().counters
            fim = time.time()
            exec_time = fim - inicio

            total_time += exec_time
            total_summary['nodes_created'] += summary.nodes_created
            total_summary['relationships_created'] += summary.relationships_created

            return (summary, exec_time)

def run_migration(migration_dir):
    for file in os.listdir(migration_dir):
        if file.endswith('.cypher'):
            file_path = os.path.join(migration_dir, file)
            print(f"Rodando: {file_path}")
            summary, exec_time = run_cypher_file(file_path)
            print(f"Sumario: {summary}")
            print(f"Tempo: {exec_time:.4f} segundos")

run_migration(indexes_dir)
run_migration(nodes_dir)
run_migration(relations_dir)

print(f"Tempo de execução total: {total_time}")
print(f"Sumario final: {total_summary}")
driver.close()
