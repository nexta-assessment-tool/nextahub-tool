import streamlit as st
import plotly.graph_objects as go
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="NextaHub Strategic Suite", layout="wide", initial_sidebar_state="expanded")

# --- DATASET BENCHMARK (Simulazione dati di settore/territorio) ---
# In un'evoluzione futura, questi dati potrebbero venire da un database reale.
BENCHMARK_DATI = {
    "Manifatturiero": {"Strategia & Controllo": 3.2, "Digitalizzazione": 2.8, "Gestione HR": 3.0, "Finanza & Investimenti": 3.5, "Sostenibilità (ESG)": 2.5, "Protezione Legale": 3.8, "Sicurezza sul Lavoro": 4.5, "Standard & Qualità": 4.0, "Sviluppo Competenze": 2.9},
    "IT & Digital": {"Strategia & Controllo": 3.8, "Digitalizzazione": 4.5, "Gestione HR": 4.0, "Finanza & Investimenti": 3.2, "Sostenibilità (ESG)": 3.0, "Protezione Legale": 3.5, "Sicurezza sul Lavoro": 3.0, "Standard & Qualità": 3.5, "Sviluppo Competenze": 4.2},
    "Servizi": {"Strategia & Controllo": 3.0, "Digitalizzazione": 3.5, "Gestione HR": 3.5, "Finanza & Investimenti": 3.0, "Sostenibilità (ESG)": 2.8, "Protezione Legale": 3.2, "Sicurezza sul Lavoro": 3.5, "Standard & Qualità": 3.0, "Sviluppo Competenze": 3.5},
    "Edilizia": {"Strategia & Controllo": 2.5, "Digitalizzazione": 2.2, "Gestione HR": 2.8, "Finanza & Investimenti": 2.8, "Sostenibilità (ESG)": 2.2, "Protezione Legale": 3.0, "Sicurezza sul Lavoro": 4.8, "Standard & Qualità": 3.2, "Sviluppo Competenze": 2.5}
}

# --- INIZIALIZZAZIONE STATI ---
if 'page' not in st.session_state: st.session_state.page = "Anagrafica"
if 'clienti' not in st.session_state: st.session_state.clienti = {}
if 'current_client_piva' not in st.session_state: st.session_state.current_client_piva = None

# --- DATABASE DOMANDE ARTICOLATE ---
DOMANDE_MATRICE = {
    'Strategia & Controllo': [
        ("Pianificazione Industriale: Esiste un Business Plan (documento che definisce obiettivi e risorse)?", {1: "Assente", 2: "Solo budget breve termine", 3: "Piano a 12 mesi", 4: "Piano triennale", 5: "Piano strutturato con revisione trimestrale"}),
        ("Monitoraggio KPI: L'azienda usa indicatori chiave (es. margini, costi acquisizione) per decidere?", {1: "No", 2: "Solo bilancio annuale", 3: "Report mensili Excel", 4: "Dashboard software", 5: "Business Intelligence in tempo reale"})
    ],
    'Protezione Legale': [
        ("Modello 231: L'azienda ha il protocollo per prevenire reati penali d'impresa e sollevare la responsabilità dell'ente?", {1: "Mai sentito", 2: "In fase di valutazione", 3: "Adottato ma non aggiornato", 4: "Aggiornato", 5: "Modello vivo con Organismo di Vigilanza esterno"}),
        ("Compliance GDPR: Come gestite la privacy e il trattamento dei dati di clienti e dipendenti?", {1: "Nessun protocollo", 2: "Informative base", 3: "Registro trattamenti attivo", 4: "Audit periodici", 5: "DPO nominato e processi blindati"})
    ],
    'Standard & Qualità': [
        ("Certificazione ISO 9001: Esiste un sistema di gestione qualità certificato per ottimizzare i processi?", {1: "No", 2: "Documentazione parziale", 3: "Certificazione ottenuta per scopi commerciali", 4: "Processi standardizzati e monitorati", 5: "Cultura del miglioramento continuo (Kaizen)"})
    ],
    'Sicurezza sul Lavoro': [
        ("DVR (Documento Valutazione Rischi): È aggiornato e riflette i rischi reali delle mansioni attuali?", {1: "Assente/Scaduto", 2: "Base/Standard", 3: "Aggiornato negli ultimi 2 anni", 4: "Analisi dettagliata rischi specifici", 5: "Software gestione sicurezza integrato"})
    ]
    # Nota: Aggiungere qui le altre aree seguendo lo stesso stile esplicativo
}

def go_to(page): st.session_state.page = page

# --- SIDEBAR CON LOGO ---
with st.sidebar:
    # URL del logo Nexta (sostituire con file locale se necessario)
    st.image("https://www.nextahub.it/wp-content/uploads/2023/05/logo-nextahub.png", width=200)
    st.markdown("---")
    st.button("🏠 1. Anagrafica", on_click=go_to, args=("Anagrafica",), use_container_width=True)
    st.button("📝 2. Questionario", on_click=go_to, args=("Questionario",), use_container_width=True)
    st.button("📊 3. Radar & Benchmark", on_click=go_to, args=("Valutazione",), use_container_width=True)
    st.button("💼 4. Urgenze e Servizi", on_click=go_to, args=("Servizi",), use_container_width=True)
    st.button("📁 5. Archivio", on_click=go_to, args=("Lista",), use_container_width=True)

# --- PAGINA 1: ANAGRAFICA ---
if st.session_state.page == "Anagrafica":
    st.header("🏢 Anagrafica Cliente")
    with st.form("anag_form"):
        col1, col2 = st.columns(2)
        with col1:
            azienda = st.text_input("Ragione Sociale")
            piva = st.text_input("Partita IVA")
        with col2:
            settore = st.selectbox("Settore", list(BENCHMARK_DATI.keys()))
            regione = st.selectbox("Regione", ["Lombardia", "Veneto", "Emilia-Romagna", "Piemonte", "Altro"])
        indirizzo = st.text_input("Indirizzo Sede")
        if st.form_submit_button("Avvia Analisi"):
            if azienda and piva:
                st.session_state.current_client_piva = piva
                st.session_state.clienti[piva] = {
                    "anagrafica": {"azienda": azienda, "piva": piva, "settore": settore, "regione": regione, "indirizzo": indirizzo},
                    "punteggi": {}, "analisi_ai": ""
                }
                go_to("Questionario")
                st.rerun()

# --- PAGINA 2: QUESTIONARIO ---
elif st.session_state.page == "Questionario":
    piva = st.session_state.current_client_piva
    cliente = st.session_state.clienti.get(piva)
    st.header(f"📝 Assessment: {cliente['anagrafica']['azienda']}")
    
    scores = {}
    for area, questions in DOMANDE_MATRICE.items():
        with st.expander(f"Area: {area}", expanded=True):
            p_area = []
            for j, (q, opts) in enumerate(questions):
                val = st.radio(q, options=[1,2,3,4,5], format_func=lambda x: opts[x], key=f"{piva}_{area}_{j}")
                p_area.append(val)
            scores[area] = sum(p_area)/len(p_area)
    
    if st.button("Salva e Confronta"):
        st.session_state.clienti[piva]['punteggi'] = scores
        go_to("Valutazione")
        st.rerun()

# --- PAGINA 3: RADAR & BENCHMARK ---
elif st.session_state.page == "Valutazione":
    piva = st.session_state.current_client_piva
    cliente = st.session_state.clienti.get(piva)
    st.header(f"📊 Radar Positioning: {cliente['anagrafica']['azienda']}")
    
    settore = cliente['anagrafica']['settore']
    categorie = list(cliente['punteggi'].keys())
    valori_cliente = list(cliente['punteggi'].values())
    
    # Recupero valori benchmark (default 3.0 se l'area non è nel benchmark semplificato)
    valori_benchmark = [BENCHMARK_DATI[settore].get(c, 3.0) for c in categorie]
    
    fig = go.Figure()
    # Traccia Cliente
    fig.add_trace(go.Scatterpolar(r=valori_cliente, theta=categorie, fill='toself', name='Cliente', line_color='#e63946'))
    # Traccia Benchmark
    fig.add_trace(go.Scatterpolar(r=valori_benchmark, theta=categorie, name=f'Media {settore}', line_color='gray', line_dash='dash'))
    
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), height=600)
    st.plotly_chart(fig, use_container_width=True)
    st.info(f"Il radar confronta l'azienda con la media del settore **{settore}** sul territorio nazionale.")

# --- PAGINA 4: URGENZE E SERVIZI ---
elif st.session_state.page == "Servizi":
    piva = st.session_state.current_client_piva
    cliente = st.session_state.clienti.get(piva)
    st.header("💼 Piano d'Azione e Urgenze")
    
    settore = cliente['anagrafica']['settore']
    scores = cliente['punteggi']
    
    col1, col2, col3 = st.columns(3)
    col1.subheader("🚨 URGENZA ALTA")
    col2.subheader("⚠️ URGENZA MEDIA")
    col3.subheader("✅ MONITORAGGIO")
    
    for area, s in scores.items():
        benchmark = BENCHMARK_DATI[settore].get(area, 3.0)
        gap = benchmark - s
        
        # Logica di urgenza: Se il gap è > 1 o il punteggio è < 2, l'urgenza è alta
        if s < 2 or gap > 1:
            col1.error(f"**{area}**")
            col1.write(f"Gap vs Settore: {gap:.1f}")
            col1.caption(f"Azione: Intervento specialistico entro 30gg.")
        elif s < benchmark:
            col2.warning(f"**{area}**")
            col2.write(f"Gap vs Settore: {gap:.1f}")
            col2.caption(f"Azione: Pianificazione a 6 mesi.")
        else:
            col3.success(f"**{area}**")
            col3.write("In linea con il settore")
            col3.caption("Azione: Mantenimento.")

# --- PAGINA 5: LISTA ---
elif st.session_state.page == "Lista":
    st.header("📁 Archivio Clienti")
    if not st.session_state.clienti: st.write("Archivio vuoto.")
    else:
        for p, d in st.session_state.clienti.items():
            st.button(f"{d['anagrafica']['azienda']} ({p}) - {d['anagrafica']['settore']}", 
                      on_click=lambda piva=p: (st.session_state.update({"current_client_piva": piva}), go_to("Valutazione")), 
                      key=f"arc_{p}")
