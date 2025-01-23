LOAD CSV WITH HEADERS FROM 'file:///historicos.csv' AS row
MERGE (x:Historico {id: row.id})
ON CREATE SET
    x.nota = row.nota,
    x.frequencia = row.frequencia
RETURN x;
