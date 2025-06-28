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

if __name__ == '__main__':
    app.run(debug=True)