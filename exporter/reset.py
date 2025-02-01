import os
import argparse
from neo4j import GraphDatabase
import time

parser = argparse.ArgumentParser(
    description="Script para resetar o banco de dados"
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
print(f"URI de conexão: {args.uri}")
print(f"Usuário de conexão: {args.user}")

with GraphDatabase.driver(args.uri, auth=(args.user, args.password)) as driver:
    labels = [l['label'] for l in driver.execute_query("call db.labels").records]
    for l in labels:
        summary = driver.execute_query(f"match (n:{l}) detach delete n").summary.counters
        print(f"Deletando nodes de label {l}: {summary}")

    result = driver.execute_query("SHOW INDEXES YIELD name return collect('drop index ' + name + ';') as cmd").records[0]["cmd"]
    for index in result:
        if index.endswith("index;"):
            summary = driver.execute_query(index).summary.counters
            print(f"Rodando {index}: {summary}")
