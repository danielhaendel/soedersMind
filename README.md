# Söders Mind

Ein kleines Flask-Projekt, bei dem registrierte Benutzer eine geheime Zahl erraten und sich im Highscore vergleichen können.

## Voraussetzungen

- Python 3.10 oder neuer
- SQLite (liefert Python auf macOS und Windows bereits mit)
- (optional) Git, falls du das Repository klonen möchtest

## Installation

### 1. Quellcode beziehen

```bash
git clone <dein-repo-url>
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

> Tipp: Unter Windows kann `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` nötig sein, damit das Aktivieren der Umgebung funktioniert.

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

1. Optional einen eigenen Secret Key setzen (empfohlen für Produktion):

   - macOS / Linux: `export FLASK_SECRET_KEY="<dein-secret>"`
   - Windows (PowerShell): `$env:FLASK_SECRET_KEY="<dein-secret>"`

   Ohne diese Variable nutzt die App den Platzhalter `change-me`.

2. Flask starten:

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

## Nützliche Umgebungsvariablen

| Variable          | Bedeutung                                  | Standardwert   |
| ----------------- | ------------------------------------------- | -------------- |
| `FLASK_SECRET_KEY`| Secret-Key für Sessions                     | `change-me`    |
| `DATABASE_PATH`   | Pfad zur SQLite-Datenbank                   | `soeder.db`    |

Beispiel macOS / Linux:

```bash
export DATABASE_PATH=./data/soeder.db
```

Beispiel Windows:

```powershell
$env:DATABASE_PATH=".\data\soeder.db"
```

## Strukturüberblick

- `app.py` – Schlanker Einstiegspunkt, ruft `src.create_app()`.
- `src/` – Applogik (Factory, Routen, Services, Datenbank-Helfer).
- `templates/`, `static/` – HTML-Templates und Assets.
- `tests/` – Unit- und Integrationstests (Pytest).
- `requirements.txt` – Python-Abhängigkeiten.

Viel Spaß beim Raten! Änderungen und Erweiterungen sind willkommen.***
