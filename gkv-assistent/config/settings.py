"""Lädt die .env-Datei und stellt Konfigurationswerte für den Assistenten bereit."""

import os

from dotenv import load_dotenv

load_dotenv()

# API-Key für OpenRouter - niemals im Code hartkodieren, sondern aus der .env laden.
OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")

# Standardmäßig das kostenlose Router-Modell, per .env überschreibbar.
MODEL_NAME: str = os.getenv("MODEL_NAME", "openrouter/free")
