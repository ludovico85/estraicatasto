# Changelog

## [1.1.0] - 2025-06-09
### Migliorato
- Disabilitato il caricamento automatico dei layer temporanei salvati nei file `.gpkg` intermedi, migliorando la pulizia del progetto QGIS e prevenendo salvataggi incoerenti.

## [1.0.1] - 2025-05-11
### Aggiunto
- Reset automatico della barra di progresso al termine dell'elaborazione.
- Reset completo dell’interfaccia (input, output, log, progress bar) alla chiusura della finestra del dialogo.
- Reset dell’interfaccia anche al clic sul pulsante OK, indipendentemente dalla modalità di chiusura.
### Migliorato
- Gestione dell’interfaccia utente per renderla più pulita tra un’esecuzione e l’altra

## [1.0.0] - 2025-05-06
### Aggiunto
- Classificazione automatica delle feature per tipo di geometria (punti, linee, poligoni)
- Esportazione dei layer in un unico file GeoPackage
- Caricamento automatico dei layer generati nel progetto QGIS
- Applicazione di simbologia categorizzata basata su attributi
- Supporto multi-file GeoJSON

