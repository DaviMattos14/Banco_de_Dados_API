--- Sequencia de pontos de uma linha no sentido
SELECT DISTINCT nome_ponto, sequencia 
FROM pontos_de_parada JOIN pontos_de_onibus 
ON id_ponto = fk_id_ponto 
WHERE fk_id_viagem IN(
    SELECT id_viagem 
    FROM linha JOIN viagem 
    ON id_linha=fk_id_linha 
    WHERE numero_linha='46' AND sentido=0 
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
ORDER BY nome_linha

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

-- Pontos de ônibus que não passam nenhuma linha
SELECT p.id_ponto, p.nome_ponto, pp.fk_id_viagem
FROM Pontos_de_Onibus p
LEFT JOIN Pontos_de_parada pp ON p.id_ponto = pp.fk_id_ponto
WHERE pp.fk_id_viagem IS NULL;

-- Linhas Inativas
SELECT COUNT(*)
FROM linha l LEFT JOIN viagem v
ON l.id_linha = v.fk_id_linha
WHERE v.id_viagem IS NULL

SELECT COUNT(l.id_linha)
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

SELECT

-- todas as linha que não funcionam fim de semana
SELECT l.numero_linha, l.nome_linha
FROM linha l 
LEFT JOIN (
    SELECT * 
    FROM viagem JOIN escala
    ON viagem.fk_id_escala = escala.id_escala
    WHERE escala.sab_dom = 1
) AS v
ON l.id_linha = v.fk_id_linha
WHERE v.id_escala IS NULL

-- Tarifa do Ônibus
SELECT valor, l.nome_linha, l.numero_linha
FROM tarifa t JOIN linha l
ON t.id_tarifa = l.fk_id_tarifa
WHERE l.numero_linha = '2345'

-- Linhas de ônubus por valor
SELECT valor, l.nome_linha, l.numero_linha
FROM tarifa t JOIN linha l
ON t.id_tarifa = l.fk_id_tarifa
WHERE t.valor = 15

SELECT l.numero_linha, v.nome_destino, v.sentido, v.hora_inicio, v.hora_fim
FROM linha l JOIN viagem v
ON v.fk_id_linha = l.id_linha
WHERE l.numero_linha = '610'
ORDER BY v.sentido, v.hora_inicio, v.hora_fim

SELECT * 
FROM viagem
WHERE fk_id_linha = 'O0865AAA0A' and sentido = 0 AND fk_id_escala = 'U_REG'
ORDER BY hora_inicio, hora_fim DESC
LIMIT 100

-------------

SELECT 
  status_linha,
  COUNT(*) AS quantidade
FROM (
  SELECT 
    l.id_linha,
    CASE 
      WHEN COUNT(v.id_viagem) > 0 THEN 'Ativa'
      ELSE 'Inativa'
    END AS status_linha
  FROM Linha l
  LEFT JOIN Viagem v ON l.id_linha = v.fk_id_linha
  GROUP BY l.id_linha
) AS sub
GROUP BY status_linha;

-----------------------
SELECT 
  status_ponto,
  COUNT(*) AS quantidade
FROM (
  SELECT 
    p.id_ponto,
    CASE 
      WHEN COUNT(pp.fk_id_viagem) > 0 THEN 'Com viagem'
      ELSE 'Sem viagem'
    END AS status_ponto
  FROM Pontos_de_Onibus p
  LEFT JOIN Pontos_de_parada pp ON p.id_ponto = pp.fk_id_ponto
  GROUP BY p.id_ponto
) AS sub
GROUP BY status_ponto;




----------------- CONSULTAS UTILIZADAS NA API ------------------

SELECT DISTINCT
            CASE l.tipo
                WHEN 'regular' THEN 'Regular'
                WHEN 'brt' THEN 'BRT'
                WHEN '700' THEN 'Especial'
                WHEN 'frescao' THEN 'Frescão'
                ELSE l.tipo
            END AS tipo_formatado,
            t.valor
        FROM Linha l
        JOIN Tarifa t ON l.fk_id_tarifa = t.id_tarifa
        WHERE l.tipo IS NOT NULL AND l.tipo != ''
        ORDER BY t.valor;


SELECT AVG(valor) AS media_valor FROM Tarifa;

SELECT c.nome_consorcio, COUNT(v.id_viagem) AS total_viagens
        FROM Consorcio c
        JOIN Linha l ON c.id_consorcio = l.fk_id_consorcio
        JOIN Viagem v ON l.id_linha = v.fk_id_linha
        GROUP BY c.nome_consorcio
        ORDER BY total_viagens DESC;

SELECT DISTINCT l.numero_linha, l.nome_linha, v.nome_destino
        FROM linha l JOIN (
            SELECT DISTINCT fk_id_linha, nome_destino
            FROM viagem JOIN (
                SELECT fk_id_viagem FROM pontos_de_parada JOIN pontos_de_onibus
                ON fk_id_ponto = id_ponto
                WHERE nome_ponto = "CMS Jorge Saldanha Bandeira de Mello"
            ) AS pontos ON id_viagem = pontos.fk_id_viagem
        ) AS v ON l.id_linha = v.fk_id_linha
        ORDER BY l.nome_linha;

SELECT DISTINCT sentido, nome_destino
        FROM viagem
        WHERE fk_id_linha = (SELECT id_linha FROM linha WHERE numero_linha = "610" LIMIT 1)
        ORDER BY sentido;

SELECT DISTINCT p.nome_ponto, pp.sequencia 
        FROM pontos_de_parada pp JOIN pontos_de_onibus p
        ON p.id_ponto = pp.fk_id_ponto 
        WHERE pp.fk_id_viagem IN (
            SELECT id_viagem FROM linha JOIN viagem 
            ON id_linha=fk_id_linha 
            WHERE numero_linha = "610" AND sentido = 0
        ) 
        ORDER BY pp.sequencia ASC 
        LIMIT 5;

SELECT status_ponto, COUNT(*) AS quantidade
        FROM (
            SELECT 
                p.id_ponto,
                CASE WHEN COUNT(pp.fk_id_viagem) > 0 THEN 'Ativos' ELSE 'Desativados' END AS status_ponto
            FROM Pontos_de_Onibus p
            LEFT JOIN Pontos_de_parada pp ON p.id_ponto = pp.fk_id_ponto
            GROUP BY p.id_ponto
        ) AS sub
        GROUP BY status_ponto;

SELECT l.numero_linha, l.nome_linha, l.tipo
        FROM linha l 
        LEFT JOIN (
            SELECT * FROM viagem JOIN escala
            ON viagem.fk_id_escala = escala.id_escala
            WHERE escala.sab_dom = 1
        ) AS v
        ON l.id_linha = v.fk_id_linha
        WHERE v.id_escala IS NULL
        ORDER BY l.numero_linha, l.tipo DESC;

SELECT 
            status_linha,
            COUNT(*) AS quantidade
        FROM (
            SELECT 
                l.id_linha,
                CASE 
                    WHEN COUNT(v.id_viagem) > 0 THEN 'Ativa'
                    ELSE 'Inativa'
                END AS status_linha
            FROM Linha l
            LEFT JOIN Viagem v ON l.id_linha = v.fk_id_linha
            GROUP BY l.id_linha
        ) AS sub
        GROUP BY status_linha;

SELECT valor, COUNT(l.id_linha) AS total_linhas
        FROM tarifa JOIN (
            SELECT DISTINCT id_linha, fk_id_tarifa
            FROM linha
        ) AS l
        ON tarifa.id_tarifa = l.fk_id_tarifa
        GROUP BY valor
        ORDER BY valor ASC;

SELECT nome_consorcio, COUNT(numero_linha) AS total_linhas
        FROM linha JOIN consorcio ON fk_id_consorcio = id_consorcio
        GROUP BY nome_consorcio
        ORDER BY total_linhas DESC;

--- Linhas Experimentais de Coleta de Dados
SELECT l.numero_linha, l.nome_linha
FROM linha l
WHERE l.numero_linha LIKE "LECD%"

--- Linhas com serviço parcial
SELECT l.numero_linha, l.nome_linha
FROM linha l
WHERE l.numero_linha LIKE "SP%"
ORDER BY l.numero_linha, l.nome_linha

--- Linhas com serviço variante
SELECT l.numero_linha, l.nome_linha
FROM linha l
WHERE l.numero_linha LIKE "SV%"
ORDER BY l.numero_linha, l.nome_linha

