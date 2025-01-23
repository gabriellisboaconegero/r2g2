# Como foi migrado o banco de dados do ADEGA para o neo4j
A decisão foi ir tabela a tabela do banco e inserindo no neo4j, acompanhandoo artigo
[A Rule-based Conversion of an EER Schema to Neo4j Schema
Constraints](https://sol.sbc.org.br/index.php/sbbd/article/view/17876/17710)
e depois de inserido o banco verificar se bate com a proposta de tranformação.

## Passo a Passo
1. Peguei o esquema ER do ADEGA [ADEGA](https://gitlab.c3sl.ufpr.br/bmuller/adegaweb/-/blob/main/Dados/adega-02-2024.pdf)
2. Peguei as tabelas do banco ja subido do ADEGA (sqlite3)
3. Fiz o dump do esquema no [chrtdb.io](https://chartdb.io/) para sqlite3
```shell
# depois de subir o dokcer do adega
cd adegaweb
docker compose cp <chatdb script>.sql rails:adegadb
docker compose exec -it rails bash -c 'sqlite3 adegadb/development.sqlite3 < adegadb/<chartdb script>.sql' > <shema-dump>
```
4. Observando o schema no chartdb.io
5. Testar query no adega antes de exportar.
```shell
cd adegaweb
docker compose exec -it rails sqlite3 adegadb/development.sqlite3
```
5. Exportando tabela para csv
```shell
cd adegaweb
SQL="<query sql>"
docker compose exec -it rails sqlite3 -header -csv adegadb/development.sqlite3 "$SQL" > ../containers/adega/import/<file>.csv
```

