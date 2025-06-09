from osgeo import ogr, osr
from qgis.core import QgsVectorLayer, QgsProject, QgsWkbTypes
import os

def scrivi_con_gdal(nome_layer, features, geometry_type, output_path, epsg, stile_dir=None, filtro_sql=None):
    if not features:
        print(f"⚠️ Nessuna feature per il layer '{nome_layer}', salto.")
        return

    # Applica filtro SQL se richiesto
    if filtro_sql:
        if filtro_sql == "line-color = '#FFFFFF'":
            features = [f for f in features if f['line-color'] == '#FFFFFF']
        elif filtro_sql == "INTERNOAFOGLIO = 'T'":
            features = [f for f in features if f['INTERNOAFOGLIO'] == 'T']



    # Crea sistema di riferimento da EPSG
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg)

    # Ottieni driver GPKG
    driver = ogr.GetDriverByName("GPKG")

    # Verifica se il file esiste: apri o crea
    if os.path.exists(output_path):
        gpkg_ds = driver.Open(output_path, 1)
    else:
        gpkg_ds = driver.CreateDataSource(output_path)

    if gpkg_ds is None:
        print(f"❌ Errore: impossibile aprire o creare il file {output_path}")
        return

    # Mappa tipo geometria da QGIS a OGR
    if geometry_type == QgsWkbTypes.PointGeometry:
        ogr_geom_type = ogr.wkbPoint
    elif geometry_type == QgsWkbTypes.LineGeometry:
        ogr_geom_type = ogr.wkbLineString
    elif geometry_type == QgsWkbTypes.PolygonGeometry:
        ogr_geom_type = ogr.wkbPolygon
    else:
        print(f"⚠️ Tipo geometria non supportato: {geometry_type}")
        return

    if gpkg_ds.GetLayerByName(nome_layer):
        gpkg_ds.DeleteLayer(nome_layer)

    out_layer = gpkg_ds.CreateLayer(nome_layer, srs, ogr_geom_type)
    if out_layer is None:
        print(f"❌ Errore: impossibile creare layer '{nome_layer}'")
        return

    fields = features[0].fields()
    for f in fields:
        field_def = ogr.FieldDefn(f.name(), ogr.OFTString)
        out_layer.CreateField(field_def)

    defn = out_layer.GetLayerDefn()

    for feat in features:
        ofeat = ogr.Feature(defn)
        available_fields = feat.fields().names()
        for i in range(defn.GetFieldCount()):
            fname = defn.GetFieldDefn(i).GetName()
            if fname in available_fields:
                ofeat.SetField(fname, str(feat[fname]) if feat[fname] is not None else "")
            else:
                ofeat.SetField(fname, "")  # oppure: pass, se vuoi ignorarlo
        ofeat.SetGeometry(ogr.CreateGeometryFromWkb(feat.geometry().asWkb()))
        out_layer.CreateFeature(ofeat)


    gpkg_ds = None  # Chiudi il file

    layer_path = f"{output_path}|layername={nome_layer}"
    loaded = QgsVectorLayer(layer_path, nome_layer, "ogr")
    #if loaded.isValid():
    #    QgsProject.instance().addMapLayer(loaded)
    #
    #    if stile_dir:
    #        qml_path = os.path.join(stile_dir, f"{nome_layer}.qml")
    #        if os.path.exists(qml_path):
    #            loaded.loadNamedStyle(qml_path)
    #            loaded.triggerRepaint()
    #            print(f"🎨 Stile applicato: {qml_path}")
    #        else:
    #            print(f"⚠️ Stile non trovato: {qml_path}")
    #else:
    #    print(f"⚠️ Layer '{nome_layer}' NON caricato (errore di validità).")
