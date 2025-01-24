import sqlite3
import os
from neo4j import GraphDatabase

# Conexão com o banco
uri = "bolt://localhost:7687"
username = "neo4j"
password = "teste123"

driver = GraphDatabase.driver(uri, auth=(username, password))

def run_cypher_file(file_path):
    print(f"Rodando {file_path}")
    with driver.session() as session:
        with open(file_path, "r") as file:
            cypher_query = file.read()
            session.run(cypher_query)


root_dir = os.path.dirname(os.path.realpath(__file__))
cypher_dir = os.path.join(root_dir, "cypher")
nodes_dir = os.path.join(cypher_dir, "nodes")
relations_dir = os.path.join(cypher_dir, "relations")

# for file in os.listdir(nodes_dir):
#     if file.endswith('.cypher'):
#         run_cypher_file(os.path.join(nodes_dir, file))

for file in os.listdir(relations_dir):
    if file.endswith('.cypher'):
        run_cypher_file(os.path.join(relations_dir, file))

driver.close()
