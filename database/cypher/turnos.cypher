LOAD CSV WITH HEADERS FROM 'file:///turnos.csv' AS row
MERGE (x:Turno {id: row.id})
ON CREATE SET
    x.nome = row.nome
RETURN x;
