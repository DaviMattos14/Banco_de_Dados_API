import pandas as pd
import datetime as data

diretorio = "/gtfs_rj"

consorcio = f"{diretorio}/agency.txt"
escala = f"{diretorio}/calendar.txt"
linha = f"{diretorio}/routes.txt"
pontos_de_onibus = f"{diretorio}/stops.txt"
pontos_de_parada = f"{diretorio}/stop_times.txt"
tarifa = f"{diretorio}/fare_attributes.txt"
tarifa_linha = f"{diretorio}/fare_rules.txt"
viagem = f"{diretorio}/trips.txt"
pontos = f"{diretorio}/stops.txt"

"""
Consorcio
"""
r_consorcio = pd.read_csv(consorcio, sep=",")
df_consorcio = r_consorcio[["agency_id", "agency_name", "agency_url"]]
df_consorcio = df_consorcio.rename(columns={
    "agency_id":"id_consorcio", 
    "agency_name":"nome_consorcio", 
    "agency_url": "site"
})

"""
Escala
"""
r_escala= pd.read_csv(escala, sep=",")
df_escala =r_escala[["service_id","monday","sunday"]]
df_escala.loc[1, 'sunday'] = 1

df_escala = df_escala.rename(columns={
    "service_id" : "id_escala",
    "monday" : "seg_sex",
    "sunday" : "sab_dom"
})

"""
Linhas
"""
r_linha = pd.read_csv(linha, sep=",")
r_linha = r_linha[["route_id", "route_short_name", "route_long_name","route_desc", "route_type","agency_id","fare_id"]]
r_tarifa_linha = pd.read_csv(tarifa_linha, sep=",")
r_tarifa_linha = r_tarifa_linha[["fare_id","route_id"]]
df_linha = pd.merge(
    r_linha,
    r_tarifa_linha,
    on='route_id',
    how='left',
    suffixes=('_antiga', '_nova') # Adiciona sufixos para diferenciar as colunas 'tarifa'
)
df_linha = df_linha.drop('fare_id_antiga', axis=1)
df_linha = df_linha.rename(columns={'fare_id_nova': 'fare_id'})

df_itineraries = pd.read_csv(f'{diretorio}/itinerario.csv', sep=",")
df_itineraries['servico'] = df_itineraries['servico'].astype(str)
route_type_map = df_itineraries[['servico', 'tipo_rota']].drop_duplicates().set_index('servico')

df_linha['route_short_name'] = df_linha['route_short_name'].astype(str)
df_merged = pd.merge(
    df_linha,
    route_type_map,
    left_on='route_short_name',
    right_index=True,
    how='left'
)
df_merged['route_type'] = df_merged['tipo_rota'].fillna(df_merged['route_type'])
df_linha = df_merged.drop(columns=['tipo_rota'])
df_linha =df_linha.rename(columns={
    'route_id' :"id_linha", 
    'route_short_name':"numero_linha", 
    'route_long_name':"nome_linha",
    'route_desc':"descricao",
    'route_type':"tipo",
    'agency_id':"fk_id_consorcio", 
    'fare_id':"fk_id_tarifa"
})

"""
Pontos de Ônibus
"""
df_pontos_BUS = pd.read_csv(pontos_de_onibus, sep=",")
df_pontos_BUS = df_pontos_BUS[["stop_id","stop_name","parent_station","platform_code"]]
df_pontos_BUS = df_pontos_BUS.rename(columns={
    "stop_id":"id_ponto",
    "stop_name":"nome_ponto",
    "parent_station":"ponto_mais_proximo",
    "platform_code":"cod_plataforma"
})

"""
Pontos de Parada na Viagem
"""
df_Ponto_Parada = pd.read_csv(pontos_de_parada, sep=",")
df_Ponto_Parada = df_Ponto_Parada[["trip_id","stop_id","stop_sequence"]]
df_Ponto_Parada= df_Ponto_Parada.rename(columns={
    "trip_id":"fk_id_viagem",
    "stop_id":"fk_id_ponto",
    "stop_sequence":"sequencia"
})
"""
Tarifa
"""
df_tarifa = pd.read_csv(tarifa, sep=",")
df_tarifa1 = df_tarifa[["fare_id","price"]]
df_tarifa1 = df_tarifa1.rename(columns={
    "fare_id":"id_tarifa",
    "price":"valor"
})

"""
Tarifa Consorcio
"""
df_tarifa_consorcio = df_tarifa[["agency_id","fare_id"]]
df_tarifa_consorcio = df_tarifa_consorcio.rename(columns={
    "agency_id":"fk_id_consorcio",
    "fare_id":"fk_id_tarifa"
})

"""
Viagens
"""
df_viagem = pd.read_csv(viagem,sep=",")
df_viagem = df_viagem[["trip_id","trip_headsign","direction_id","route_id","service_id"]]
df_frequencia = pd.read_csv(f'{diretorio}/frequencies.txt',sep=",")
df_frequencia = df_frequencia[['trip_id', 'start_time', 'end_time']]

df_viagem = pd.merge(
    df_viagem,
    df_frequencia,
    on='trip_id',  # A coluna comum que serve como chave
    how='left'     # 'left' mantém todos os dados de df_trips
)

# Converte para timedelta
df_viagem['start_time'] = pd.to_timedelta(df_viagem['start_time'])
df_viagem['end_time'] = pd.to_timedelta(df_viagem['end_time'])

# Formata como HH:MM, aplicando % 24 nas horas

df_viagem['start_time'] = df_viagem['start_time'].apply(
    lambda x: f"{x.components.hours % 24:02d}:{x.components.minutes:02d}"
    if pd.notna(x) else "00:00"
)
df_viagem['end_time'] = df_viagem['end_time'].apply(
    lambda x: f"{x.components.hours % 24:02d}:{x.components.minutes:02d}"
    if pd.notna(x) else "00:00"
)

df_viagem = df_viagem.rename(columns={
    'trip_id':"id_viagem",
    'trip_headsign':"nome_destino",
    'direction_id':"sentido",
    'route_id':"fk_id_linha",
    'service_id':"fk_id_escala",
    'start_time':"hora_inicio", 
    'end_time':"hora_fim"
})


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