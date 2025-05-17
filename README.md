# EstraiCatasto ![alt text](https://github.com/ludovico85/estraicatasto/blob/main/estrai_catasto/icon.png?raw=true)

[![Plugin QGIS](https://img.shields.io/badge/QGIS-3.22%2B-green.svg)](https://qgis.org)
[![License: GPL v2](https://img.shields.io/badge/license-GPL--2.0-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html)
[![Build Status](https://img.shields.io/badge/build-manual-blue.svg)]()
[![Last update](https://img.shields.io/github/last-commit/ludovico85/estraicatasto)](https://github.com/ludovico85/estraicatasto/commits/main)
[![Issues](https://img.shields.io/github/issues/ludovico85/estraicatasto)](https://github.com/ludovico85/estraicatasto/issues)
[![GitHub Release](https://img.shields.io/github/v/release/ludovico85/estraicatasto)](https://github.com/ludovico85/estraicatasto/releases/tag/v1.0.0)

---

## 🗂️ Descrizione

**EstraiCatasto** è un plugin per QGIS che consente di:

- Caricare e analizzare file GeoJSON contenenti dati catastali
- Suddividere geometrie per tipo (punti, linee, poligoni)
- Classificare gli oggetti per attributo (FABBRICATI, PARTICELLE, ACQUE, STRADE, ECC.)
- Salvare i layer in un file GeoPackage
- Caricarli automaticamente nel progetto QGIS
- Caricare uno stile predefinito (ispirato allo stile CAD e allo stile WMS)

Utile per **geometri, pianificatori, tecnici GIS** che lavorano su dati catastali distributi tramite piattaforma SISTER dell'[Agenzia delle Entrate](https://iampe.agenziaentrate.gov.it/sam/UI/Login?realm=/agenziaentrate).

---

## ✅ Requisiti

- QGIS **3.22** o superiore
- Testato su Windows

---

## 🚀 Installazione

### <img src="https://qgis.org/styleguide/visual/qgis-icon64.svg" alt="QGIS Logo" width="25"/> Installazione del plugin da QGIS

Per installare il plugin direttamente da QGIS, segui questi passaggi:

1. Apri QGIS e vai al menu: Plugins → Gestione e installazione plugin...
2. Nella finestra che si apre, clicca sull’icona dell’ingranaggio in alto a destra (⚙️) per accedere alle impostazioni.
3. Abilita i plugin sperimentali: Metti la spunta su "Mostra anche i plugin sperimentali".
4. Torna alla scheda Tutti o usa la barra di ricerca per cercare il plugin: EstraiCatasto
5. Seleziona il plugin dalla lista e clicca su "Installa plugin".
	ℹ️ Nota: il plugin è attualmente in fase sperimentale. Assicurati di aver attivato l’opzione nelle impostazioni per poterlo visualizzare e installare.

### 📦 Da ZIP (manuale)

1. Scarica l'ultima versione da [Releases](https://github.com/ludovico85/estraicatasto/releases)
2. In QGIS: `Plugins > Gestisci e installa plugin > Installa da file .zip`
3. Seleziona `estraicatasto_vX.Y.Z.zip`
4. Abilita il plugin

## Demo

![Demo](media/example.gif)
