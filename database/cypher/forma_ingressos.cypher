LOAD CSV WITH HEADERS FROM 'file:///forma_ingressos.csv' AS row
MERGE (x:FormaIngresso {id: row.id})
ON CREATE SET
    x.nome = row.nome
RETURN x;
