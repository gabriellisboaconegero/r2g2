LOAD CSV WITH HEADERS FROM 'file:///forma_evasaos.csv' AS row
MERGE (x:FormaEvasao {id: row.id})
ON CREATE SET
    x.nome = row.nome
RETURN x;
