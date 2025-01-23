LOAD CSV WITH HEADERS FROM 'file:///resultado_disciplinas.csv' AS row
MERGE (x:ResultadoDisciplina {id: row.id})
ON CREATE SET
    x.nome = row.nome
RETURN x;
