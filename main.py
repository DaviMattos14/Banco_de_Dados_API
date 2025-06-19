from connect_bd import connect_mysql, text
from tratando_arquivos import  df_consorcio, df_escala, df_pontos_BUS, df_viagem, df_tarifa, df_tarifa1, df_linha, df_Ponto_Parada, df_tarifa_consorcio
import pandas as pd

connect = connect_mysql()

tabelas_para_limpar = [
    "pontos_de_parada",
    "viagem",
    "linha",
    "tarifa_consorcio",
    "tarifa",
    "consorcio",
    "escala",
    "pontos_de_onibus"
]

with connect.begin() as conn:  # begin() garante commit automático
    for tabela in tabelas_para_limpar:
        conn.execute(text(f'DROP TABLE {tabela};'))

print("\nIniciando inserção de novos dados...")

df_consorcio.to_sql(
    name="consorcio",
    con=connect,
    if_exists="append",
    index=False
)
print("OK 1/8")
df_escala.to_sql(
    name="escala",
    con=connect,
    if_exists="append",
    index=False
)
print("OK 2/8")

df_pontos_BUS.to_sql(
    name="pontos_de_onibus",
    con=connect,
    if_exists="append",
    index=False
)
print("OK 3/8")

df_tarifa1.to_sql(
    name="tarifa",
    con=connect,
    if_exists="append",
    index=False
)
print("OK 4/8 ")

df_linha.to_sql(
    name="linha",
    con=connect,
    if_exists="append",
    index=False
)
print("OK 5/8")

df_viagem.to_sql(
    name="viagem",
    con=connect,
    if_exists="append",
    index=False
)
print("OK 6/8 ")

df_Ponto_Parada = df_Ponto_Parada.drop_duplicates(subset=["fk_id_viagem", "fk_id_ponto"])
df_Ponto_Parada.to_sql(
    name="pontos_de_parada",
    con=connect,
    if_exists="append",
    index=False
)

print("OK 7/8")


df_tarifa_consorcio.to_sql(
    name="tarifa_consorcio",
    con=connect,
    if_exists="append",
    index=False
)
print("OK 8/8")

connect.dispose()