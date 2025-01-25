# O importador para o neo4j (SQLite & PostgresSQL)
A ferramenta permite importar um banco de dados relacional dos bancos `SQLite` e `PostgresSQL`
para o `Neo4j`.

A importação é feita exatamente como está no banco e o mapeamento segue as seguintes regras
1. Uma linha é um **Node**.
2. Um nome de uma tabela é um **Label**.
3. Um par de chave primária e chave estrangeira é uma **Relation**.
4. As propriedades de um **Node** são os atributos que a tabela de nome **Label** tinha, menos as chaves estrangeiras.
5. Relations não tem atributos. Derivada de 3. e 1., pois como toda tabela vira **Nodes** e **Relations**
são a conexão entre as chaves então a **Relation** não vai ter atributos.
6. Todo **Node** tem um conjunto de atributos únicos.
7. Todo **Label** tem um index em cima do atributos que eram chave primária no modelo relacional.
8. Toda tabela sem chave primária tem adicionada um chave primária intermediária `row_id`.
9. O **Label** de uma **Relation** é a concatenação dos labels de seus **Nodes** com `To` no meio.

# Executando
Esse ambiente foi criado para utilizar docker e facilitar o desenvolvimento. No ambiente existem um projeto
docker compose que inicia o `Neo4j`, `ChartDB.io` e um banco `PostgresSQL`. O banco do ADEGA precisa ser levantado manualmente seguindo as instruções do próprio ADEGA.
Suba os containers com
```
docker compose up -d
```
Dentro do diretório `database` são encontradas as ferramentas que fazem a importação, elas vão gerar os scripts `Cypher` e os arquivos csv
para realizar a importação do banco.
São duas ferramentas principais
- `gen_import_context.py`
- `run_migrations.py`
A primeira é reponsável por criar os scripts `Cypher` e os arquivos csv das tabelas do banco.
```
# Ative o ambiente virtual
source database/.env/bin/activate

# Rode o script. --help para melhor explicação do funcionamento dele
python3 database/gen_import_context.py --help
```

Após os scripts e arquivos csv estarem criados é preciso dar acesso aos arquivos csv para o `Neo4j`. Para isso o arquivos dentro de `database/<context>/csv` devem ser copiados para `import/<context>`.
```
mkdir -p import/<context>
cp database/<context>/csv/* import/<context>
```

Agora que o `Neo4j` tem acesso à eles basta executar os scripts
```
# --help, leia nates de executar
python3 database/run_migrations.py --help
```

# Usando o `ChatDB.io`
Siga o passo a passo para visualizar um novo banco e depois importe ele para o `Neo4j` seguindo os
passos anteriores e confira se os esquema batem.
PS: O script para obter informações dos bancos do `ChatDB.io` é o mesmo utilizado pelas ferramentas. Peguei emprestado :)
