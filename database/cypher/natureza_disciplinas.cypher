LOAD CSV WITH HEADERS FROM 'file:///natureza_disciplinas.csv' AS row
MERGE (x:NaturezaDisciplina {id: row.id})
ON CREATE SET
    x.nome = row.nome
RETURN x;
