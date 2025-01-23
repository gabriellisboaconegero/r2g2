LOAD CSV WITH HEADERS FROM 'file:///cursos.csv' AS row
MERGE (x:Curso {id: row.id})
ON CREATE SET
    x.nome = row.nome,
    x.habilitacao = row.habilitacao
RETURN x;
