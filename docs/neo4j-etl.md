# Usando neo4j-etl
Não consegui usar, muitos problemas com o sqlite3 e provavelmente por não ser a versão interprise.
Também nãao consegui usando outra base em um banco de dados postgres.

# Passo a passo
1. Para poder executar o `neo4j-etl export` ele precisa estar no mesmo container que o neo4j, então baixar ele
e colocar no container do neo4j. Minha solução, baixar na minha máquina e montar um volume no container.
[https://github.com/neo4j-contrib/neo4j-etl/releases](https://github.com/neo4j-contrib/neo4j-etl/releases).

2. Para poder usar com sqlite3 é preciso baixar o driver de conexão jdbc do sqlite3. [https://github.com/xerial/sqlite-jdbc/releases](https://github.com/xerial/sqlite-jdbc/releases). Coloque no diretório `neo4j-etl-cli-1.6.0`.

3. Para executar o neo4j-etl é preciso estar no mesmo diretório que o diretório `bin/`, então `cd neo4j-etl-cli-1.6.0`.

4. Para que o neo4j-etl tenha acesso ao banco do sqlite3, monte o banco do adega na raiz do container. Assim a ferramenta pode acessar o banco pela conexão jdbc `jdbc:sqlite:/adegadb/development.sqlite3`.

5. Dois arquivos de configuração estão prontos, um para cada banco (ATENÇÃO: Nenhum deles funciona).

```
unzip neo4j-etl-cli-<version>.zip
cp neo4j-etl-configs/etl.* neo4j-etl-cli-<version>
cp neo4j-etl-configs/sqlite-jdbc-3.48.0.0.jar neo4j-etl-cli-<version>/lib/

# Lembre de montar o volume do 'neo4j-etl-cli-<version>' no serviço 'neo4j' no docker-compose.yml
docker compose up -d
docker compose exec -it neo4j bash
cd neo4j-etl-cli-<version>
mkdir -p /tmp/etl

# Escolher o arquivo de configuração baseado no banco de dados
./bin/neo4j-elt <command> --config-file etl.config.<db>
```

# Problemas
Antes de executar o `neo4j-etl export` é preciso gerar o mapeamento.

Ao tentar executar o `./bin/neo4j-etl generate-metadata-mapping` com o banco sqlite ele da um erro dizendo que
a tabela não tem esquema, e como sqlite realmente não tem esquema então não sei como arrumar.
Mesmo problema no github: [https://github.com/neo4j-contrib/neo4j-etl/issues/78](https://github.com/neo4j-contrib/neo4j-etl/issues/78)

Executar o mapeamento no banco postgres funciona perfeitamente, porém na hora de fazer a exportação
segue o seguinte erro:
```
org.neo4j.driver.exceptions.ClientException: Invalid constraint syntax, ON and ASSERT should not be used. Replace ON with FOR and ASSERT with REQUIRE. (line 1, column 19 (offset: 18))
"CREATE CONSTRAINT ON (n:Genre) ASSERT n.genreId IS UNIQUE"
```
