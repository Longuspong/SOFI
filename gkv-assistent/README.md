# GKV-Serviceassistent

Ein KI-gestützter Serviceassistent für Versicherte einer gesetzlichen
Krankenversicherung (GKV). Portfolio-Projekt für eine Bewerbung im Bereich
IT/Digitalisierung bei einer Krankenkasse.

Der Assistent hilft Versicherten, schneller an ihr Anliegen zu kommen - per
Wissensauskunft (Chat mit Wissensbasis), per fertig formuliertem Anschreiben
(z. B. Anfrage einer Mitgliedschaftsbescheinigung) oder per automatisch
befülltem amtlichen Antrag (Familienversicherung, Kinderkrankengeld,
Pflegeversicherung).

Alle Beispieldaten basieren auf dem fiktiven Testfall "Max Mustermann"
(Geburtsdatum 15.03.1985, Versichertennummer M123456789, wohnhaft
Musterstraße 1, 12345 Musterstadt) - es werden zu keinem Zeitpunkt echte
Personendaten verwendet.

## Technische Grundentscheidungen

- Sprache: Python 3.11+
- UI-Framework: Streamlit
- LLM-Zugang: OpenRouter API (OpenAI-kompatibel), Modell konfigurierbar
  über `.env` (Standard: `openrouter/free`)
- Kein Cloud-Hosting - alles läuft lokal

## Projektstruktur

```
gkv-assistent/
  app.py                  <- Streamlit-Einstiegspunkt
  config/
    settings.py           <- lädt .env, stellt Konfigurationswerte bereit
  chat_logic/
    llm_client.py         <- Funktionen für LLM-Aufrufe
    conversation.py       <- Gesprächsablauf-Steuerung
  knowledge_base/
    documents/            <- abgelegte Wissens-Textdateien
    retriever.py          <- Embedding + Suche
  letters/
    mgb_request.py        <- Anfrage-Generator Mitgliedschaftsbescheinigung
  forms/
    familienversicherung.py
    kinderkrankengeld.py
    pflegeversicherung.py
    pdf_fill_utils.py      <- gemeinsame PDF-Fülllogik
  data/
    test_cases.py          <- Musterfall "Max Mustermann"
  logs/
    interaction_log.py     <- einfaches Logging
  requirements.txt
  .env.example
  README.md
```

## Status

**Phase 0 abgeschlossen:** Ordnerstruktur, `.gitignore` und `.env.example`
sind angelegt. Die einzelnen Module enthalten noch keine Logik - diese
entsteht schrittweise in den folgenden Phasen (siehe Docstrings in den
jeweiligen Dateien).

## Lokales Setup

1. Python 3.11+ installieren (prüfen mit `python --version`).
2. In diesen Ordner wechseln: `cd gkv-assistent`
3. Virtuelle Umgebung anlegen und aktivieren:
   - Windows: `python -m venv venv` dann `venv\Scripts\activate`
   - macOS/Linux: `python3 -m venv venv` dann `source venv/bin/activate`
4. `.env.example` zu `.env` kopieren und deinen OpenRouter-API-Key eintragen
   (siehe Kommentare in `.env.example`, wie du kostenlos einen Key erstellst).
5. Sobald Phase 1 abgeschlossen ist: Abhängigkeiten installieren
   (`pip install -r requirements.txt`) und die App starten
   (`streamlit run app.py`).
