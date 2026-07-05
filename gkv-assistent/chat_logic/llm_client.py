"""Funktionen für LLM-Aufrufe an die OpenRouter-API."""

from openai import APIConnectionError, APIError, APITimeoutError, OpenAI

from config.settings import MODEL_NAME, OPENROUTER_API_KEY

# Fest im Code hinterlegter System-Prompt, der dem Modell seine Rolle vorgibt.
SYSTEM_PROMPT = (
    "Du bist ein hilfsbereiter Assistent einer gesetzlichen Krankenversicherung "
    "für Versicherte. Antworte klar, freundlich und in einfacher Sprache. "
    "Wenn du eine Information nicht sicher weißt, sag das offen, statt zu raten."
)


def frage_llm(nachricht: str, verlauf: list) -> str:
    """Schickt eine Nutzerfrage inkl. bisherigem Verlauf an OpenRouter und gibt die Textantwort zurück.

    Wirft bei fehlendem API-Key, Timeout oder API-Fehlern eine RuntimeError mit
    einer für Nutzer:innen verständlichen deutschen Fehlermeldung - app.py fängt
    diese ab, statt dass die App abstürzt.
    """
    if not OPENROUTER_API_KEY:
        raise RuntimeError(
            "Kein OpenRouter-API-Key gefunden. Bitte trage OPENROUTER_API_KEY "
            "in der Datei .env ein (siehe .env.example)."
        )

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY, timeout=30.0)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(verlauf)
    messages.append({"role": "user", "content": nachricht})

    try:
        antwort = client.chat.completions.create(model=MODEL_NAME, messages=messages)
    except APITimeoutError as fehler:
        raise RuntimeError(
            "Die Anfrage an das Sprachmodell hat zu lange gedauert (Timeout). Bitte versuche es erneut."
        ) from fehler
    except APIConnectionError as fehler:
        raise RuntimeError(
            "Verbindung zur OpenRouter-API fehlgeschlagen. Bitte prüfe deine Internetverbindung."
        ) from fehler
    except APIError as fehler:
        raise RuntimeError(f"Die OpenRouter-API hat einen Fehler gemeldet: {fehler}") from fehler

    inhalt = antwort.choices[0].message.content
    if not inhalt:
        raise RuntimeError("Das Sprachmodell hat keine Antwort geliefert. Bitte versuche es erneut.")
    return inhalt
