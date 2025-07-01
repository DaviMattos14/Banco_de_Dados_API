from flask import Flask, jsonify, Response, render_template, request
from sqlalchemy import create_engine, text
import pandas as pd
import requests
app = Flask(__name__)
db_connection_str = 'mysql+pymysql://Admin:1310223a8@localhost/gtfs_rj'
db_engine = create_engine(db_connection_str)
# ----------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/linhas_por_consorcio')
def get_linhas_por_consorcio():
    query = text("""
        SELECT nome_consorcio, COUNT(numero_linha) AS total_linhas
        FROM linha JOIN consorcio ON fk_id_consorcio = id_consorcio
        GROUP BY nome_consorcio
        ORDER BY total_linhas DESC;
    """)

    df = pd.read_sql(query, db_engine)
    result = df.to_dict(orient='records')
    return jsonify(result)


@app.route('/favicon.ico')
def favicon():
    return Response(status=204)


@app.route('/api/linhas_por_tarifa')
def get_linhas_por_tarifa():
    """
    Este endpoint retorna a contagem de linhas de ônibus agrupadas pelo valor da tarifa.
    """
    query = text("""
        SELECT valor, COUNT(l.id_linha) AS total_linhas
        FROM tarifa JOIN (
            SELECT DISTINCT id_linha, fk_id_tarifa
            FROM linha
        ) AS l
        ON tarifa.id_tarifa = l.fk_id_tarifa
        GROUP BY valor
        ORDER BY valor ASC;
    """)
    
    try:
        df = pd.read_sql(query, db_engine)
        df['valor'] = df['valor'].astype(float)
        result = df.to_dict(orient='records')
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/status_linhas')
def get_status_linhas():
    """
    Este endpoint retorna a contagem de linhas Ativas e Inativas.
    """
    query = text("""
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
    """)
    
    try:
        df = pd.read_sql(query, db_engine)
        result = df.to_dict(orient='records')
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Rota para a tabela de linhas que não operam no fim de semana
@app.route('/api/linhas_sem_fds')
def get_linhas_sem_fds():
    """
    Este endpoint retorna uma lista de linhas que não operam aos fins de semana.
    """
    query = text("""
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
    """)
    
    try:
        df = pd.read_sql(query, db_engine)
        result = df.to_dict(orient='records')
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Rota para o gráfico de status dos pontos
@app.route('/api/status_pontos')
def get_status_pontos():
    query = text("""
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
    """)
    try:
        df = pd.read_sql(query, db_engine)
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/trajeto/<linha>/<int:sentido>')
def get_trajeto(linha, sentido):
    """
    Retorna a sequência de nomes de pontos para uma dada linha e sentido.
    """
    query = text("""
        SELECT DISTINCT p.nome_ponto, pp.sequencia 
        FROM pontos_de_parada pp JOIN pontos_de_onibus p
        ON p.id_ponto = pp.fk_id_ponto 
        WHERE pp.fk_id_viagem IN (
            SELECT id_viagem FROM linha JOIN viagem 
            ON id_linha=fk_id_linha 
            WHERE numero_linha = :linha AND sentido = :sentido
        ) 
        ORDER BY pp.sequencia ASC;
    """)
    
    try:
        params = {"linha": linha, "sentido": sentido}
        df = pd.read_sql(query, db_engine, params=params)
        result = df.to_dict(orient='records')
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/destinos/<linha>')
def get_destinos(linha):
    """
    Para uma dada linha, retorna os sentidos (0 e 1) e seus
    respectivos nomes de destino.
    """
    # Esta consulta busca os nomes de destino distintos para uma linha
    query = text("""
        SELECT DISTINCT sentido, nome_destino
        FROM viagem
        WHERE fk_id_linha = (SELECT id_linha FROM linha WHERE numero_linha = :linha LIMIT 1)
        ORDER BY sentido;
    """)
    
    try:
        params = {"linha": linha}
        df = pd.read_sql(query, db_engine, params=params)
        result = df.to_dict(orient='records')
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Para buscar as linhas após selecionar um ponto
@app.route('/api/linhas_por_ponto')
def get_linhas_por_ponto():
    """
    Executa a consulta principal para encontrar todas as linhas que passam
    em um ponto de ônibus específico.
    """
    # Pegamos o nome do ponto dos parâmetros da URL (?nome=...)
    nome_ponto_selecionado = request.args.get('nome')

    if not nome_ponto_selecionado:
        return jsonify({"error": "Nome do ponto não fornecido"}), 400

    query = text("""
        SELECT DISTINCT l.numero_linha, l.nome_linha, v.nome_destino
        FROM linha l JOIN (
            SELECT DISTINCT fk_id_linha, nome_destino
            FROM viagem JOIN (
                SELECT fk_id_viagem FROM pontos_de_parada JOIN pontos_de_onibus
                ON fk_id_ponto = id_ponto
                WHERE nome_ponto = :nome_ponto
            ) AS pontos ON id_viagem = pontos.fk_id_viagem
        ) AS v ON l.id_linha = v.fk_id_linha
        ORDER BY l.nome_linha;
    """)
    try:
        params = {"nome_ponto": nome_ponto_selecionado}
        df = pd.read_sql(query, db_engine, params=params)
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Para o total de viagens por consórcio
@app.route('/api/viagens_por_consorcio')
def get_viagens_por_consorcio():
    """
    Retorna a contagem total de viagens agrupada por consórcio.
    """
    query = text("""
        SELECT c.nome_consorcio, COUNT(v.id_viagem) AS total_viagens
        FROM Consorcio c
        JOIN Linha l ON c.id_consorcio = l.fk_id_consorcio
        JOIN Viagem v ON l.id_linha = v.fk_id_linha
        GROUP BY c.nome_consorcio
        ORDER BY total_viagens DESC;
    """)
    try:
        df = pd.read_sql(query, db_engine)
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Para o valor médio da tarifa
@app.route('/api/tarifa_media')
def get_tarifa_media():
    """
    Calcula e retorna o valor médio de todas as tarifas.
    """
    query = text("SELECT AVG(valor) AS media_valor FROM Tarifa;")
    try:
        df = pd.read_sql(query, db_engine)
        # Pega o primeiro (e único) valor da coluna 'media_valor'
        media = df['media_valor'].iloc[0]
        # Retorna um JSON simples com a média
        return jsonify({"media_valor": float(media)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/tarifas_por_tipo')
def get_tarifas_por_tipo():
    """
    Retorna os pares distintos de tipo de linha (formatado) e valor de tarifa.
    """
    query = text("""
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
    """)
    try:
        df = pd.read_sql(query, db_engine)
        df['valor'] = df['valor'].astype(float)
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/linhas/experimentais')
def get_linhas_experimentais():
    """Retorna as linhas experimentais (LECD)."""
    query = text("SELECT l.numero_linha, l.nome_linha FROM linha l WHERE l.numero_linha LIKE 'LECD%';")
    try:
        df = pd.read_sql(query, db_engine)
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/linhas/parciais')
def get_linhas_parciais():
    """Retorna as linhas com serviço parcial (SP)."""
    query = text("SELECT l.numero_linha, l.nome_linha FROM linha l WHERE l.numero_linha LIKE 'SP%' ORDER BY l.numero_linha, l.nome_linha;")
    try:
        df = pd.read_sql(query, db_engine)
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/linhas/variantes')
def get_linhas_variantes():
    """Retorna as linhas com serviço variante (SV)."""
    query = text("SELECT l.numero_linha, l.nome_linha FROM linha l WHERE l.numero_linha LIKE 'SV%' ORDER BY l.numero_linha, l.nome_linha;")
    try:
        df = pd.read_sql(query, db_engine)
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
     
if __name__ == '__main__':
    app.run(debug=True)