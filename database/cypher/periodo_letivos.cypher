LOAD CSV WITH HEADERS FROM 'file:///periodo_letivos.csv' AS row
MERGE (x:PeriodoLetivo {id: row.id})
ON CREATE SET
    x.ano = row.ano,
    x.periodo = row.periodo
RETURN x;
