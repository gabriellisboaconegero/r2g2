LOAD CSV WITH HEADERS FROM 'file:///disciplinas.csv' AS row
MERGE (x:Disciplina {id: row.id})
ON CREATE SET
    x.nome = row.nome,
    x.carga_horaria = row.carga_horaria,
    x.codigo = row.codigo,
    x.numero = row.numero,
    x.tcc = row.tcc,
    x.estagio = row.estagio
RETURN x;
