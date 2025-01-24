import sqlite3
import os
from neo4j import GraphDatabase

# Conexão com o banco
uri = "bolt://localhost:7687"
username = "neo4j"
password = "teste123"

driver = GraphDatabase.driver(uri, auth=(username, password))

root_dir = os.path.dirname(os.path.realpath(__file__))
cypher_dir = os.path.join(root_dir, "cypher")
nodes_dir = os.path.join(cypher_dir, "nodes")
relations_dir = os.path.join(cypher_dir, "relations")
indexes_dir = os.path.join(cypher_dir, "indexes")

def run_cypher_file(file_path):
    print(f"Rodando {file_path}")
    with driver.session() as session:
        with open(file_path, "r") as file:
            cypher_query = file.read()
            session.run(cypher_query)

def run_migration(migration_dir):
    for file in os.listdir(migration_dir):
        if file.endswith('.cypher'):
            run_cypher_file(os.path.join(migration_dir, file))

run_migration(indexes_dir)
run_migration(nodes_dir)
run_migration(relations_dir)

driver.close()
