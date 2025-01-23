LOAD CSV WITH HEADERS FROM 'file:///graus.csv' AS row
MERGE (x:Grau {id: row.id})
ON CREATE SET
    x.nome = row.nome
RETURN x;
