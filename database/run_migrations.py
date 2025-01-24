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


cypher_dir = "cypher"
for file in os.listdir(cypher_dir):
    if file.endswith('.cypher'):
        run_cypher_file(os.path.join(cypher_dir, file))

driver.close()
