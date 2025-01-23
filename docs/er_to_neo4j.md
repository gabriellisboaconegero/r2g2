# Migração das tabelas do adega para o neo4j
Existem 3 arquivos auxiliares para fazer a migração.
1. `export_csv.py`: Exporta as tabelas csv do adega.
    1. Para poder exporatar copia o arquivo `development.sqlite3` do adega
    para o diretório.
    2. Faz a query `SELECT * from {table}`.

2. `gen_cypher.py`: Gera o código cypher que importa do csv para o neo4j.
3. `run_migrations.py`: Roda os scripts cypher criados pela etapa anterior.
