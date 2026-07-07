"""Steuert den Gesprächsablauf: sucht zuerst relevante Wissens-Abschnitte,
ergänzt sie im Prompt und ruft danach das LLM auf.
"""

from chat_logic.llm_client import frage_llm
from knowledge_base.retriever import suche_kontext


def fuehre_gespraech(nachricht: str, verlauf: list) -> tuple:
    """Beantwortet eine Nutzerfrage unter Einbeziehung der Wissensbasis.

    Gibt ein Tupel (antwort: str, verwendete_abschnitte: list) zurück. Die
    verwendeten Abschnitte werden in app.py zur Nachvollziehbarkeit angezeigt.
    """
    abschnitte = suche_kontext(nachricht)

    if abschnitte:
        kontext_text = "\n\n".join(f"- {abschnitt}" for abschnitt in abschnitte)
        erweiterte_nachricht = (
            f"Relevante Informationen:\n{kontext_text}\n\n"
            "Stütze dich bei deiner Antwort primär auf diese Informationen. "
            "Falls sie die Frage nicht abdecken, sag das offen, statt zu raten.\n\n"
            f"Frage: {nachricht}"
        )
    else:
        erweiterte_nachricht = nachricht

    antwort = frage_llm(erweiterte_nachricht, verlauf)
    return antwort, abschnitte
