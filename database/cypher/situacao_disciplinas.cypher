LOAD CSV WITH HEADERS FROM 'file:///situacao_disciplinas.csv' AS row
MERGE (x:SituacaoDisciplina {id: row.id})
ON CREATE SET
    x.nome = row.nome
RETURN x;
