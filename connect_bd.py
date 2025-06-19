from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd

def connect_mysql():
    """
    Função para conectar ao banco de dados MySQL usando SQLAlchemy.
    """
    engine = None
    try:
        usuario = 'Admin' # Usar os dados do seu banco
        senha = '1310223a8'
        host = 'localhost'
        porta = '3306'
        banco = 'gtfs_rj'

        # Criação da engine de conexão
        engine = create_engine(f'mysql+pymysql://{usuario}:{senha}@{host}:{porta}/{banco}')
        
        # Testar a conexão abrindo uma conexão real
        with engine.connect() as conn:
            print("Conexão com o MySQL via SQLAlchemy bem-sucedida!")

    except SQLAlchemyError as e:
        print(f"Erro ao conectar com o MySQL via SQLAlchemy: {e}")
    
    return engine

def execute_query(engine, query: str):
    """
    Executa uma query de escrita (INSERT, UPDATE, DELETE, DDL) usando SQLAlchemy.
    """
    try:
        with engine.begin() as conn:  # begin() faz commit automático
            conn.execute(text(query))
            print("Query executada com sucesso!")
    except SQLAlchemyError as e:
        print(f"Erro ao executar a query: {e}")

def read_query(engine, query):
    """
    Função para executar uma query SELECT usando SQLAlchemy e retornar um DataFrame.
    """
    try:
        # Lê a query diretamente como DataFrame
        df = pd.read_sql(query, con=engine)
        return df
    except SQLAlchemyError as err:
        print(f"Erro ao executar a query: {err}")
        return None