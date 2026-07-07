"""Embedding-basierte Suche über die abgelegten Wissens-Textdateien (RAG)."""

import glob
import os

import chromadb
from chromadb.utils import embedding_functions

DOKUMENTE_ORDNER = os.path.join(os.path.dirname(__file__), "documents")
CHROMA_ORDNER = os.path.join(os.path.dirname(__file__), "chroma_db")
COLLECTION_NAME = "gkv_wissen"

# Mehrsprachiges Embedding-Modell, gut geeignet für deutsche Texte.
EMBEDDING_MODELL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Wird erst beim ersten tatsächlichen Gebrauch geladen (nicht schon beim Import),
# damit die App auch ohne Internetverbindung startet und keinen Absturz verursacht.
_embedding_funktion = None


def _hole_embedding_funktion():
    """Lädt das Embedding-Modell beim ersten Aufruf und merkt es sich danach."""
    global _embedding_funktion
    if _embedding_funktion is None:
        try:
            _embedding_funktion = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=EMBEDDING_MODELL
            )
        except Exception as fehler:
            raise RuntimeError(
                "Das Embedding-Modell konnte nicht geladen werden (es wird beim ersten Mal aus "
                "dem Internet heruntergeladen). Bitte prüfe deine Internetverbindung und "
                "versuche es erneut."
            ) from fehler
    return _embedding_funktion


def _lade_client() -> chromadb.PersistentClient:
    """Erstellt bzw. öffnet den lokal gespeicherten ChromaDB-Client."""
    return chromadb.PersistentClient(path=CHROMA_ORDNER)


def _teile_in_abschnitte(text: str, woerter_pro_abschnitt: int = 400, ueberlappung: int = 50) -> list:
    """Teilt einen Text in Abschnitte von ca. 300-500 Wörtern mit etwas Überlappung."""
    woerter = text.split()
    abschnitte = []
    start = 0
    while start < len(woerter):
        ende = start + woerter_pro_abschnitt
        abschnitt = " ".join(woerter[start:ende])
        if abschnitt.strip():
            abschnitte.append(abschnitt)
        start = ende - ueberlappung
    return abschnitte


def index_existiert() -> bool:
    """Prüft, ob bereits ein ChromaDB-Index auf der Festplatte existiert."""
    return os.path.isdir(CHROMA_ORDNER) and len(os.listdir(CHROMA_ORDNER)) > 0


def baue_index() -> int:
    """Liest alle .txt-Dateien aus knowledge_base/documents/, teilt sie in Abschnitte,
    erzeugt Embeddings und speichert sie in einer lokalen ChromaDB-Collection.

    Gibt die Anzahl der gespeicherten Abschnitte zurück (0, falls keine .txt-Dateien
    abgelegt sind). Wirft eine RuntimeError mit verständlicher Meldung, falls das
    Embedding-Modell nicht geladen werden kann (z. B. fehlende Internetverbindung).
    """
    embedding_funktion = _hole_embedding_funktion()
    client = _lade_client()

    try:
        client.delete_collection(COLLECTION_NAME)
    except ValueError:
        pass  # Collection existierte noch nicht - kein Problem

    collection = client.create_collection(name=COLLECTION_NAME, embedding_function=embedding_funktion)

    dateipfade = sorted(glob.glob(os.path.join(DOKUMENTE_ORDNER, "*.txt")))

    ids = []
    texte = []
    metadaten = []

    for dateipfad in dateipfade:
        dateiname = os.path.basename(dateipfad)
        with open(dateipfad, "r", encoding="utf-8") as datei:
            inhalt = datei.read()

        for i, abschnitt in enumerate(_teile_in_abschnitte(inhalt)):
            ids.append(f"{dateiname}-{i}")
            texte.append(abschnitt)
            metadaten.append({"quelle": dateiname})

    if texte:
        collection.add(ids=ids, documents=texte, metadatas=metadaten)

    return len(texte)


def suche_kontext(frage: str, anzahl: int = 3) -> list:
    """Gibt die 'anzahl' relevantesten Textabschnitte zur Nutzerfrage zurück.

    Liefert eine leere Liste, falls noch kein Index existiert, keine Dokumente
    abgelegt wurden oder ein Fehler auftritt (z. B. fehlende Internetverbindung) -
    der Chat soll dann ohne Wissensbasis-Kontext weiterlaufen, statt abzustürzen.
    """
    if not index_existiert():
        return []

    try:
        embedding_funktion = _hole_embedding_funktion()
        client = _lade_client()
        collection = client.get_collection(name=COLLECTION_NAME, embedding_function=embedding_funktion)

        anzahl_vorhanden = collection.count()
        if anzahl_vorhanden == 0:
            return []

        ergebnis = collection.query(query_texts=[frage], n_results=min(anzahl, anzahl_vorhanden))
        return ergebnis.get("documents", [[]])[0]
    except Exception:
        return []
