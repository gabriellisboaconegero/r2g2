# Documentação da estrutura do docker
## Subindo neo4j puro
É possível utilizar o banco de dados do neo4j e um browser localmente.
```shell
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -v /$HOME/neo4j:/data neo4j -v /$HOME/neo4j/datasets:/var/lib/neo4j/import
```

Monta o volume `-v /$HOME/neo4j:/data` para manter persistência.
Monta o volume `-v /$HOME/neo4j/datasets:/var/lib/neo4j/import` para poder importar os arquivos do diretório local.

- Para próximas execuções executar
```shell
docker start neo4j
```

- Para parar o neo4j
```shell
docker stop neo4j
```

## Subindo neo4j com compose
Para poder ter um controle maior dos ambientes neo4j e de diferentes projtos. Versão gratuita não suporta varios bancos de dados.

Usando o `docker-compose.yml` e o `Dockerfile` execute apenas um dos serviços do compose. Para criar um novo ambiente adicione no `docker-compose.yml` no mesmo formato que o ambiente `adega`.

```shell
docker compose up -d adega
```
