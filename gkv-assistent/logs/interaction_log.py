"""Einfaches Logging der Chat-Interaktionen in eine lokale CSV-Datei."""

import csv
import os
from datetime import datetime

LOG_PFAD = os.path.join(os.path.dirname(__file__), "interaktionen.csv")


def log_interaktion(frage: str, antwort: str, dauer_sekunden: float) -> None:
    """Hängt eine Interaktion (Zeitstempel, Frage, Antwort, Dauer) an logs/interaktionen.csv an.

    Legt die Datei inkl. Kopfzeile an, falls sie noch nicht existiert. Schreibfehler
    (z. B. kein Schreibrecht) werden bewusst nur ignoriert, damit das Logging den
    Chat nicht zum Absturz bringt.
    """
    datei_existiert_bereits = os.path.isfile(LOG_PFAD)
    try:
        with open(LOG_PFAD, "a", newline="", encoding="utf-8") as datei:
            writer = csv.writer(datei)
            if not datei_existiert_bereits:
                writer.writerow(["zeitstempel", "frage", "antwort", "dauer_sekunden"])
            writer.writerow(
                [datetime.now().isoformat(timespec="seconds"), frage, antwort, f"{dauer_sekunden:.2f}"]
            )
    except OSError:
        pass
