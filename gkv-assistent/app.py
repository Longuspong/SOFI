"""Streamlit-Einstiegspunkt des GKV-Serviceassistenten - Chat-Oberfläche."""

import time

import streamlit as st

from chat_logic.llm_client import frage_llm
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

with st.sidebar:
    st.header("Info")
    if st.session_state.letzte_antwortzeit is not None:
        st.metric("Letzte Antwortzeit", f"{st.session_state.letzte_antwortzeit:.2f} s")
    else:
        st.write("Noch keine Anfrage gestellt.")

# Bisherigen Chatverlauf anzeigen.
for nachricht in st.session_state.verlauf:
    with st.chat_message(nachricht["role"]):
        st.write(nachricht["content"])

if st.session_state.letzter_fehler:
    st.error(st.session_state.letzter_fehler)

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
            antwort = frage_llm(eingabe_bereinigt, verlauf_bisher)
        except RuntimeError as fehler:
            st.session_state.letzter_fehler = str(fehler)
        else:
            dauer_sekunden = time.time() - start_zeit
            st.session_state.letzte_antwortzeit = dauer_sekunden
            st.session_state.verlauf.append({"role": "assistant", "content": antwort})
            log_interaktion(eingabe_bereinigt, antwort, dauer_sekunden)

    st.rerun()
