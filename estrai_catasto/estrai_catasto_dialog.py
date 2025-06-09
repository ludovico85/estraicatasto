import os
import tempfile
import time
from qgis.PyQt import uic, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import Qt
from qgis.core import QgsVectorLayer, QgsWkbTypes, QgsProject
from .utils import estrai_epsg_da_geojson, pulisci_nome_layer, assicurati_cartella_esiste, unisci_geopackage
from .gdal_utils import scrivi_con_gdal


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'estrai_catasto_dialog_base.ui'))


class EstraiCatastoDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.btn_add_input.clicked.connect(self.aggiungi_file_geojson)
        self.btn_remove_input.clicked.connect(self.rimuovi_file_selezionato)
        self.btn_browse_output.clicked.connect(self.scegli_output_gpkg)
        self.btn_run.clicked.connect(self.esegui_elaborazione)
        self.comboBox_stile.currentTextChanged.connect(self.aggiorna_interfaccia_stile)
        
        
        # Connetti il pulsante OK al reset manuale
        if hasattr(self, 'buttonBox'):
            self.buttonBox.accepted.connect(self.reset_dialog_fields)
        elif hasattr(self, 'button_box'):
            self.button_box.accepted.connect(self.reset_dialog_fields)


    def aggiorna_interfaccia_stile(self, testo):
        if testo.lower() == "stile wms":
            self.checkBox_mappa_continua.setChecked(False)
            self.checkBox_mappa_continua.setEnabled(False)
        else:
            self.checkBox_mappa_continua.setEnabled(True)

    def aggiungi_file_geojson(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Seleziona uno o più file GeoJSON", "", "GeoJSON (*.geojson)")
        for f in files:
            if not self.listWidget_inputs.findItems(f, Qt.MatchExactly):
                self.listWidget_inputs.addItem(f)

    def rimuovi_file_selezionato(self):
        for item in self.listWidget_inputs.selectedItems():
            self.listWidget_inputs.takeItem(self.listWidget_inputs.row(item))

    def scegli_output_gpkg(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Salva come GeoPackage", "", "GeoPackage (*.gpkg)")
        if file_path:
            if not file_path.endswith(".gpkg"):
                file_path += ".gpkg"
            self.lineEdit_output.setText(file_path)

    def esegui_elaborazione(self):
        input_files = [self.listWidget_inputs.item(i).text() for i in range(self.listWidget_inputs.count())]
        output_path = self.lineEdit_output.text()
        mappa_continua_attiva = self.checkBox_mappa_continua.isChecked()
        stile_sel = self.comboBox_stile.currentText().lower()
    
        livelli_attesi = {"PARTICELLE", "FABBRICATI", "CONFINI", "LINEEVARIE", "STRADE", "SIMBOLI", "TESTI", "ACQUE"}
        mappa_alias_livelli = {"DIRITTI_DI_SUPERFICIE": "TESTI"}
    
        self.textEdit_log.clear()
        start_time = time.time()
        self.textEdit_log.append("⏳ Elaborazione in corso...")
        QtWidgets.QApplication.processEvents()
    
        if not input_files:
            self.textEdit_log.append("⚠️ Nessun file GeoJSON selezionato.")
            return
    
        if not output_path or not output_path.lower().endswith(".gpkg"):
            self.textEdit_log.append("⚠️ Nessun file GeoPackage di output valido selezionato.")
            QtWidgets.QMessageBox.warning(
                self, "File di output mancante",
                "Seleziona un file di output valido con estensione .gpkg prima di procedere."
            )
            return
    
        assicurati_cartella_esiste(output_path)
    
        self.textEdit_log.append(f"📁 File in ingresso: {len(input_files)}")
        self.textEdit_log.append(f"💾 Output GPKG: {output_path}")
    
        epsg_codes = set()
        for f in input_files:
            epsg = estrai_epsg_da_geojson(f)
            if epsg:
                epsg_codes.add(epsg)
    
        if len(epsg_codes) > 1:
            self.textEdit_log.append("❌ Il sistema di riferimento dei layer caricati non è univoco:")
            for f in input_files:
                self.textEdit_log.append(f"  - {f} → EPSG:{estrai_epsg_da_geojson(f)}")
            self.textEdit_log.append("⚠️ Interrompo l'elaborazione.")
            return
        elif not epsg_codes:
            self.textEdit_log.append("⚠️ Nessun CRS rilevato nei file GeoJSON.")
            return
    
        epsg_corrente = list(epsg_codes)[0]
        self.textEdit_log.append(f"📌 CRS comune: EPSG:{epsg_corrente}")
        self.textEdit_log.append("📥 Analisi dei file GeoJSON...")
    
        layers_by_geom = {"LINEE": [], "POINT": {}, "POLYGON": {}}
        tmp_files = []
        temp_dir = tempfile.mkdtemp(prefix="catasto_")
    
        for path in input_files:
            layer = QgsVectorLayer(path, os.path.basename(path), "ogr")
            if not layer.isValid():
                self.textEdit_log.append(f"❌ Errore: file non valido → {path}")
                continue
    
            self.textEdit_log.append(f"✅ File valido: {path}")
            features_in_file = list(layer.getFeatures())
            codice_comune = os.path.basename(path).split("_")[0]
    
            for feature in features_in_file:
                geom = feature.geometry()
                gtype = geom.type()
                livello_raw = feature["LIVELLO"] if "LIVELLO" in feature.fields().names() else "SENZA_LIVELLO"
                livello = mappa_alias_livelli.get(livello_raw.upper(), livello_raw)
    
                #if livello != livello_raw:
                    #self.textEdit_log.append(f"ℹ️ Livello '{livello_raw}' mappato in '{livello}' nel file: {path}")
    
                if livello.upper() not in livelli_attesi:
                    self.textEdit_log.append(f"🧭 Livello non previsto: '{livello}' trovato nel file: {path}")
    
                if livello.upper() == "PARTICELLE":
                    if "COD_COMUNE" in feature.fields().names() and not feature["COD_COMUNE"]:
                        feature["COD_COMUNE"] = codice_comune
    
                if gtype == QgsWkbTypes.PolygonGeometry:
                    layers_by_geom["POLYGON"].setdefault(livello, []).append(feature)
                elif gtype == QgsWkbTypes.LineGeometry:
                    layers_by_geom["LINEE"].append(feature)
                elif gtype == QgsWkbTypes.PointGeometry:
                    layers_by_geom["POINT"].setdefault(livello, []).append(feature)
    
    
        # Stile directory
        stile_dir = None
        mapping = {"stile wms": "wms", "stile cad": "cad"}
        if stile_sel in mapping:
            stile_dir = os.path.join(os.path.dirname(__file__), "styles", mapping[stile_sel])
    
        # Inizializza progress bar
        self.progressBar.setValue(0)
        tot_operazioni = len(layers_by_geom["POLYGON"]) + len(layers_by_geom["POINT"])
        if layers_by_geom["LINEE"] and stile_sel != "stile wms":
            tot_operazioni += 1
        op_corrente = 0
    
        # POLIGONI
        for nome, features in layers_by_geom["POLYGON"].items():
            if features:
                nome_layer = pulisci_nome_layer(f"POLIGONI_{nome}")
                tmp_path = os.path.join(temp_dir, f"{nome_layer}.gpkg")
                scrivi_con_gdal(nome_layer, features, QgsWkbTypes.PolygonGeometry, tmp_path, epsg_corrente, stile_dir)
                if os.path.exists(tmp_path):
                    tmp_files.append(tmp_path)
    
                op_corrente += 1
                progresso = int((op_corrente / tot_operazioni) * 100)
                self.progressBar.setValue(progresso)
                QtWidgets.QApplication.processEvents()
    
        # LINEE (solo se non stile WMS)
        if layers_by_geom["LINEE"] and stile_sel != "stile wms":
            filtro_linee = "line-color = '#FFFFFF'" if mappa_continua_attiva else None
            nome_layer = "LINEE"
            tmp_path = os.path.join(temp_dir, f"{nome_layer}.gpkg")
            scrivi_con_gdal(nome_layer, layers_by_geom["LINEE"], QgsWkbTypes.LineGeometry, tmp_path, epsg_corrente, stile_dir, filtro_sql=filtro_linee)
            if os.path.exists(tmp_path):
                tmp_files.append(tmp_path)
    
            op_corrente += 1
            progresso = int((op_corrente / tot_operazioni) * 100)
            self.progressBar.setValue(progresso)
            QtWidgets.QApplication.processEvents()
    
        # PUNTI
        for nome, features in layers_by_geom["POINT"].items():
            if not features:
                continue
    
            # Salta TESTI se stile WMS
            if stile_sel == "stile wms" and nome.upper() == "TESTI":
                continue
    
            # Filtro SIMBOLI per tipo
            if nome.upper() == "SIMBOLI":
                features = [f for f in features if "TIPO" in f.fields().names() and str(f["TIPO"]) in ["9", "14"]]
    
            nome_layer = pulisci_nome_layer(f"PUNTI_{nome}")
            filtro = "INTERNOAFOGLIO = 'T'" if mappa_continua_attiva and nome.upper() in ["TESTI", "SIMBOLI"] else None
            tmp_path = os.path.join(temp_dir, f"{nome_layer}.gpkg")
            scrivi_con_gdal(nome_layer, features, QgsWkbTypes.PointGeometry, tmp_path, epsg_corrente, stile_dir, filtro_sql=filtro)
            if os.path.exists(tmp_path):
                tmp_files.append(tmp_path)
    
            op_corrente += 1
            progresso = int((op_corrente / tot_operazioni) * 100)
            self.progressBar.setValue(progresso)
            QtWidgets.QApplication.processEvents()
    
        # Merge finale
        unisci_geopackage(tmp_files, output_path, elimina_tmp=True)
    
        self.textEdit_log.append("✅ Esportazione completata.")
        # Carica i layer finali da output GPKG
        self.textEdit_log.append("📂 Caricamento layer dal file finale...")
        from osgeo import ogr  # Assicurati che sia già importato sopra

        driver = ogr.GetDriverByName("GPKG")
        ds = driver.Open(output_path, 0)
        if ds:
            # Determina directory dello stile selezionato
            stile_dir = None
            mapping = {"stile wms": "wms", "stile cad": "cad"}
            if stile_sel in mapping:
                stile_dir = os.path.join(os.path.dirname(__file__), "styles", mapping[stile_sel])

            for i in range(ds.GetLayerCount()):
                layer = ds.GetLayer(i)
                layer_name = layer.GetName()
                layer_path = f"{output_path}|layername={layer_name}"
                vlayer = QgsVectorLayer(layer_path, layer_name, "ogr")
                if vlayer.isValid():
                    QgsProject.instance().addMapLayer(vlayer)
                    self.textEdit_log.append(f"✅ Layer caricato: {layer_name}")

                    # ➕ Applica stile se disponibile
                    if stile_dir:
                        qml_path = os.path.join(stile_dir, f"{layer_name}.qml")
                        if os.path.exists(qml_path):
                            vlayer.loadNamedStyle(qml_path)
                            vlayer.triggerRepaint()
                            self.textEdit_log.append(f"🎨 Stile applicato")
                        else:
                            self.textEdit_log.append(f"⚠️ Stile non trovato per: {layer_name}")
                else:
                    self.textEdit_log.append(f"⚠️ Layer non valido: {layer_name}")
        else:
            self.textEdit_log.append("❌ Impossibile aprire il file GPKG finale per il caricamento.")
        self.progressBar.setValue(100)
        QtWidgets.QApplication.processEvents()
        time.sleep(2)  # pausa per mostrare il 100%
        self.progressBar.setValue(0)

        elapsed = time.time() - start_time
        self.textEdit_log.append(f"⏱ Tempo totale di elaborazione: {elapsed:.2f} secondi")
        
    def reset_dialog_fields(self):
        self.listWidget_inputs.clear()
        self.lineEdit_output.clear()
        self.textEdit_log.clear()
        self.comboBox_stile.setCurrentIndex(0)
        self.checkBox_mappa_continua.setChecked(False)
        self.progressBar.setValue(0)

    def closeEvent(self, event):
        self.reset_dialog_fields()
        event.accept()
