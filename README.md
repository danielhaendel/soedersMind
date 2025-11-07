# Söders Mind

Ein kleines Flask-Projekt, bei dem registrierte Benutzer eine geheime Zahl erraten und sich im Highscore vergleichen können.

## Voraussetzungen

- Python 3.10 oder neuer
- SQLite (liefert Python auf macOS und Windows bereits mit)
- (optional) Git, falls du das Repository klonen möchtest

## Installation

### 1. Quellcode beziehen

```bash
git clone https://github.com/danielhaendel/soedersMind
cd soedersMind
```

### 2. Virtuelle Umgebung anlegen

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Abhängigkeiten installieren

macOS / Linux:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Windows:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Anwendung starten

1. Flask starten:

   macOS / Linux:
   ```bash
   export FLASK_APP=app
   python -m flask run
   ```

   Windows (PowerShell):
   ```powershell
   $env:FLASK_APP="app"
   python -m flask run
   ```

3. Browser öffnen und `http://127.0.0.1:5000` aufrufen.

Beim ersten Start wird automatisch die SQLite-Datenbank `soeder.db` im Projektverzeichnis angelegt.

## Tests ausführen

macOS / Linux:

```bash
python -m pytest
```

Windows:

```powershell
python -m pytest
```

Die Tests verwenden eine temporäre SQLite-Datei, beeinflussen also nicht die produktive Datenbank.

Viel Spaß beim Raten! Änderungen und Erweiterungen sind willkommen.***
