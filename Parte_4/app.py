# 1. Adicione render_template à importação
from flask import Flask, jsonify, Response, render_template
from sqlalchemy import create_engine, text
import pandas as pd

# --- (O resto das suas configurações continua igual) ---
app = Flask(__name__)
db_connection_str = 'mysql+pymysql://Admin:1310223a8@localhost/gtfs_rj'
db_engine = create_engine(db_connection_str)
# ----------------------------------------------------

# 2. Modifique a rota principal (index)
@app.route('/')
def index():
    # Esta função agora procura por 'index.html' na pasta 'templates' e o envia para o navegador.
    return render_template('index.html')

# --- (Suas outras rotas, como /api/linhas_por_consorcio e /favicon.ico, continuam aqui) ---

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

# ------------------------------------------------------------------------------------------
# Adicione esta nova rota no seu app.py

@app.route('/api/linhas_por_tarifa')
def get_linhas_por_tarifa():
    """
    Este endpoint retorna a contagem de linhas de ônibus agrupadas pelo valor da tarifa.
    """
    # Renomeei a coluna de contagem para 'total_linhas' para facilitar o uso no front-end
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
        # O PANDAS pode retornar o valor como um Decimal. Convertemos para float para ser compatível com JSON.
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
        SELECT l.numero_linha, l.nome_linha
        FROM linha l 
        LEFT JOIN (
            SELECT * FROM viagem JOIN escala
            ON viagem.fk_id_escala = escala.id_escala
            WHERE escala.sab_dom = 1
        ) AS v
        ON l.id_linha = v.fk_id_linha
        WHERE v.id_escala IS NULL
        ORDER BY l.numero_linha ASC;
    """)
    
    try:
        df = pd.read_sql(query, db_engine)
        result = df.to_dict(orient='records')
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# NOVA Rota para o gráfico de status dos pontos
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
    (Versão para a tabela, não precisa de coordenadas).
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
        
if __name__ == '__main__':
    app.run(debug=True)