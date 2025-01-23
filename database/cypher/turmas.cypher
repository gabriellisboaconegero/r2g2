LOAD CSV WITH HEADERS FROM 'file:///turmas.csv' AS row
MERGE (x:Turma {id: row.id})
ON CREATE SET
    x.codigo = row.codigo
RETURN x;
