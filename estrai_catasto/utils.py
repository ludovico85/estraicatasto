import json
import os
from osgeo import ogr

def estrai_epsg_da_geojson(path_geojson):
    with open(path_geojson, "r", encoding="utf-8") as f:
        data = json.load(f)

    crs_string = data.get("crs", {}).get("properties", {}).get("name", "")
    if "EPSG::" in crs_string:
        epsg_code = crs_string.split("EPSG::")[-1]
        return int(epsg_code)
    return None

def pulisci_nome_layer(nome):
    if nome.startswith("POLIGONI_"):
        return nome.replace("POLIGONI_", "")
    elif nome.startswith("PUNTI_"):
        return nome.replace("PUNTI_", "")
    return nome

def assicurati_cartella_esiste(path_output):
    folder = os.path.dirname(path_output)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)

def unisci_geopackage(lista_gpkg_temporanei, output_finale, elimina_tmp=False):
    """
    Unisce più GeoPackage (ognuno contenente uno o più layer) in un unico GeoPackage finale.
    """
    driver = ogr.GetDriverByName("GPKG")

    if os.path.exists(output_finale):
        driver.DeleteDataSource(output_finale)

    output_ds = driver.CreateDataSource(output_finale)
    if output_ds is None:
        print(f"❌ Errore: impossibile creare il file finale {output_finale}")
        return

    for tmp_path in lista_gpkg_temporanei:
        src_ds = driver.Open(tmp_path)
        if src_ds is None:
            print(f"⚠️ File non leggibile: {tmp_path}")
            continue

        for i in range(src_ds.GetLayerCount()):
            layer = src_ds.GetLayerByIndex(i)
            layer_name = layer.GetName()
            print(f"➕ Copio layer '{layer_name}' da {os.path.basename(tmp_path)}")
            output_ds.CopyLayer(layer, layer_name)

        src_ds = None  # chiudi prima di rimuovere
        if elimina_tmp:
            try:
                os.remove(tmp_path)
            except PermissionError as e:
                print(f"⚠️ Impossibile eliminare {tmp_path}: {e}")

    output_ds = None
    print(f"✅ Merge completato in: {output_finale}")