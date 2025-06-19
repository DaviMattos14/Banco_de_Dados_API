import os
import requests
import zipfile
from io import BytesIO

os.makedirs("./gtfs_rj",exist_ok=True)

print("Baixando GTFS-RJ\n")
gtfs_url = "https://www.arcgis.com/sharing/rest/content/items/8ffe62ad3b2f42e49814bf941654ea6c/data"
filebytes = BytesIO(requests.get(gtfs_url).content)
myzip = zipfile.ZipFile(filebytes)
myzip.extractall("./gtfs_rj")

print(".CSV dos Itinerários\n")
itinerario_url = "https://hub.arcgis.com/api/v3/datasets/1bf2032a693746a68b70c2a3b2544859_1/downloads/data?format=csv&spatialRefId=31983&where=1%3D1"
file = requests.get(itinerario_url).content
filename= "itinerario.csv"
with open("./gtfs_rj/itinerario.csv", "wb") as f:
    f.write(file)


