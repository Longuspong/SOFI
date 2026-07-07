"""Streamlit-Einstiegspunkt des GKV-Serviceassistenten - Chat-Oberfläche."""

import time

import streamlit as st

from chat_logic.conversation import fuehre_gespraech
from knowledge_base.retriever import baue_index, index_existiert
from logs.interaction_log import log_interaktion

st.set_page_config(page_title="GKV-Serviceassistent", page_icon="💬")
st.title("💬 GKV-Serviceassistent")

# Chatverlauf als Liste von {"role": "user"/"assistant", "content": str}.
if "verlauf" not in st.session_state:
    st.session_state.verlauf = []

# Zuletzt gemessene Antwortzeit für die Sidebar-Anzeige.
if "letzte_antwortzeit" not in st.session_state:
    st.session_state.letzte_antwortzeit = None

# Fehlermeldung der letzten Anfrage (falls vorhanden) - getrennt vom Verlauf,
# damit Fehlertexte nicht als Kontext an das Modell zurückgeschickt werden.
if "letzter_fehler" not in st.session_state:
    st.session_state.letzter_fehler = None

# Wissens-Abschnitte, die für die letzte Antwort verwendet wurden (für den Expander).
if "letzte_quellen" not in st.session_state:
    st.session_state.letzte_quellen = []

# Beim ersten Start automatisch die Wissensbasis aufbauen, falls noch keine existiert.
if not index_existiert():
    with st.spinner("Wissensbasis wird erstmalig aufgebaut ..."):
        try:
            anzahl_abschnitte = baue_index()
        except Exception as fehler:  # z. B. fehlende Internetverbindung beim Modell-Download
            st.session_state.letzter_fehler = (
                f"Wissensbasis konnte nicht aufgebaut werden: {fehler}"
            )
        else:
            if anzahl_abschnitte == 0:
                st.info(
                    "Noch keine Wissensdokumente gefunden. Lege .txt-Dateien in "
                    "knowledge_base/documents/ ab und klicke in der Sidebar auf "
                    "'Wissensbasis neu aufbauen'."
                )

with st.sidebar:
    st.header("Info")
    if st.session_state.letzte_antwortzeit is not None:
        st.metric("Letzte Antwortzeit", f"{st.session_state.letzte_antwortzeit:.2f} s")
    else:
        st.write("Noch keine Anfrage gestellt.")

    st.header("Wissensbasis")
    if st.button("Wissensbasis neu aufbauen"):
        with st.spinner("Wissensbasis wird neu aufgebaut ..."):
            try:
                anzahl_abschnitte = baue_index()
            except Exception as fehler:
                st.error(f"Wissensbasis konnte nicht aufgebaut werden: {fehler}")
            else:
                st.success(f"Wissensbasis aufgebaut: {anzahl_abschnitte} Textabschnitte gespeichert.")

# Bisherigen Chatverlauf anzeigen.
for nachricht in st.session_state.verlauf:
    with st.chat_message(nachricht["role"]):
        st.write(nachricht["content"])

if st.session_state.letzter_fehler:
    st.error(st.session_state.letzter_fehler)

if st.session_state.letzte_quellen:
    with st.expander("Verwendete Wissens-Abschnitte anzeigen"):
        for i, abschnitt in enumerate(st.session_state.letzte_quellen, start=1):
            st.markdown(f"**Abschnitt {i}:**")
            st.write(abschnitt)

nutzereingabe = st.chat_input("Deine Frage an den GKV-Serviceassistenten ...")

if nutzereingabe:
    eingabe_bereinigt = nutzereingabe.strip()

    if not eingabe_bereinigt:
        st.session_state.letzter_fehler = "Bitte gib eine Frage ein, bevor du sie abschickst."
    else:
        st.session_state.letzter_fehler = None
        verlauf_bisher = list(st.session_state.verlauf)
        st.session_state.verlauf.append({"role": "user", "content": eingabe_bereinigt})

        start_zeit = time.time()
        try:
            antwort, quellen = fuehre_gespraech(eingabe_bereinigt, verlauf_bisher)
        except RuntimeError as fehler:
            st.session_state.letzter_fehler = str(fehler)
            st.session_state.letzte_quellen = []
        else:
            dauer_sekunden = time.time() - start_zeit
            st.session_state.letzte_antwortzeit = dauer_sekunden
            st.session_state.letzte_quellen = quellen
            st.session_state.verlauf.append({"role": "assistant", "content": antwort})
            log_interaktion(eingabe_bereinigt, antwort, dauer_sekunden)

    st.rerun()
