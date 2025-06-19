--- Sequencia de pontos de uma linha no sentido
SELECT DISTINCT nome_ponto, sequencia 
FROM pontos_de_parada JOIN pontos_de_onibus 
ON id_ponto = fk_id_ponto 
WHERE fk_id_viagem IN(
    SELECT id_viagem 
    FROM linha JOIN viagem 
    ON id_linha=fk_id_linha 
    WHERE numero_linha='43' AND sentido=1 
) 
ORDER BY sequencia ASC;

-- Numero, Nome, Destinho de todas as linhas que passam no ponto 'CMS Jorge Saldanha Bandeira de Mello'
SELECT DISTINCT numero_linha, nome_linha, viagem.nome_destino
FROM linha JOIN (
    SELECT DISTINCT fk_id_linha, nome_destino, hora_inicio, hora_fim 
    FROM viagem JOIN (
        SELECT fk_id_viagem FROM pontos_de_parada JOIN pontos_de_onibus
        ON fk_id_ponto = id_ponto
        WHERE nome_ponto = 'CMS Jorge Saldanha Bandeira de Mello'
        ) AS pontos
        ON id_viagem = pontos.fk_id_viagem
) AS viagem
ON id_linha = viagem.fk_id_linha

-- Número de Linhas de Ônibus agrupadas por consórcio
SELECT nome_consorcio, COUNT(linhas.numero_linha)
FROM consorcio JOIN (
    SELECT DISTINCT numero_linha, fk_id_consorcio FROM linha
) AS linhas
ON id_consorcio = linhas.fk_id_consorcio
GROUP BY nome_consorcio

-- Número de Linhas de Ônibus agrupadas por consórcio
SELECT nome_consorcio, COUNT(numero_linha)
FROM linha JOIN consorcio
ON fk_id_consorcio = id_consorcio
GROUP BY nome_consorcio

-- Linhas que funcionam fim de semana
SELECT DISTINCT numero_linha, nome_linha
FROM linha JOIN (
    SELECT fk_id_linha, fk_id_escala
    FROM
    viagem JOIN escala
    ON id_escala = fk_id_escala
    WHERE sab_dom = 1 
) AS e
ON id_linha = e.fk_id_linha

-- Numero de Linhas agrupado pelo valor da passagem
SELECT valor, COUNT(l.id_linha)
FROM tarifa JOIN (
    SELECT DISTINCT id_linha, fk_id_tarifa
    FROM linha
) AS l
ON tarifa.id_tarifa = l.fk_id_tarifa
GROUP BY valor

-- Pontos de ônibuas que não passam nenhuma linha
SELECT p.id_ponto, p.nome_ponto, pp.fk_id_viagem
FROM Pontos_de_Onibus p
LEFT JOIN Pontos_de_parada pp ON p.id_ponto = pp.fk_id_ponto
WHERE pp.fk_id_viagem IS NULL;

-- Linhas Inativas
SELECT COUNT(*)
FROM linha l LEFT JOIN viagem v
ON l.id_linha = v.fk_id_linha
WHERE v.id_viagem IS NULL

SELECT DISTINCT l.id_linha, l.nome_linha
FROM Linha l
JOIN Viagem v ON l.id_linha = v.fk_id_linha
LEFT JOIN Escala e ON v.fk_id_escala = e.id_escala
WHERE v.fk_id_escala IS NULL;

SELECT l.id_linha, l.nome_linha
FROM Linha l
LEFT JOIN Tarifa t ON l.fk_id_tarifa = t.id_tarifa
WHERE t.id_tarifa IS NULL;
