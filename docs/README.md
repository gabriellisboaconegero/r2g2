# Usando neo4j localmente
É possível utilizar o banco de dados do neo4j e um browser localmente.
- Para criar o conatiner.
- Imports mapeados para `datasets`
```shell
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -v /$HOME/neo4j:/data neo4j -v /$HOME/neo4j/datasets:/var/lib/neo4j/import
```
- Para próximas execuções executar
```shell
docker start neo4j
```

- Para parar o neo4j
```shell
docker stop neo4j
```

## Carregando dados no neo4j
É possível carregar uma base de dados relacional no neo4j de diversas formas
- `LOAD` command. https://neo4j.com/docs/cypher-manual/current/clauses/load-csv/
- `neo4j-admin database import`. https://neo4j.com/docs/operations-manual/current/tools/neo4j-admin/neo4j-admin-import/#_overview
- https://neo4j.com/docs/getting-started/appendix/tutorials/guide-import-relational-and-etl/
- https://github.com/neo4j-contrib/neo4j-etl. (Ferramente de migração de relational database para neo4j)

# Links úteis
- https://neo4j.com/docs/graph-data-science/current/algorithms/
