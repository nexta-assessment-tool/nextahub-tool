import streamlit as st
import plotly.graph_objects as go
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="NextaHub Platform", layout="wide", initial_sidebar_state="expanded")

# --- INIZIALIZZAZIONE STATI (DB Temporaneo) ---
if 'page' not in st.session_state:
    st.session_state.page = "Anagrafica"
if 'clienti' not in st.session_state:
    st.session_state.clienti = {} # Dizionario: {piva: {dati}}
if 'current_client_piva' not in st.session_state:
    st.session_state.current_client_piva = None

# --- DATABASE DOMANDE ---
# (Assicurati che qui ci siano tutte le 54 domande come definito in precedenza)
DOMANDE_MATRICE = {
    'Strategia & Controllo': [
        ("Esiste un business plan o piano industriale?", {1: "No, navighiamo a vista", 2: "Visione a 2/3 mesi", 3: "Visione a 6 mesi", 4: "Piano a 1 anno", 5: "Piano strutturato a 2+ anni"}),
        ("Monitoraggio KPI e cruscotti aziendali", {1: "Nessun dato", 2: "Controllo costi a fine anno", 3: "Monitoraggio fatturato mensile", 4: "KPI operativi monitorati", 5: "Dashboard real-time integrata"}),
        ("Definizione dell'organigramma e ruoli", {1: "Tutti fanno tutto", 2: "Ruoli accennati", 3: "Organigramma base", 4: "Mansionari definiti", 5: "Struttura manageriale autonoma"}),
        ("Analisi della concorrenza e del mercato", {1: "Mai fatta", 2: "Reattiva (seguiamo gli altri)", 3: "Analisi sporadica", 4: "Monitoraggio annuale", 5: "Strategia basata su dati costanti"}),
        ("Sistemi di delega e processi decisionali", {1: "Accentramento totale", 2: "Delega minima", 3: "Prime deleghe operative", 4: "Processi condivisi", 5: "Delega manageriale completa"}),
        ("Passaggio generazionale/continuità", {1: "Problema ignorato", 2: "Discussioni vaghe", 3: "Consapevolezza rischio", 4: "Piano abbozzato", 5: "Piano formalizzato"})
    ],
    'Protezione Legale': [
        ("Presenza Modello 231", {1: "Assente", 2: "In valutazione", 3: "Presente ma vecchio", 4: "Aggiornato regolarmente", 5: "Efficace con ODV attivo"}),
        ("Conformità GDPR", {1: "Nulla", 2: "Solo informative", 3: "Registri trattamenti", 4: "Audit periodici", 5: "Compliance totale e DPO"}),
        ("Contrattualistica Clienti/Fornitori", {1: "Verbali", 2: "Standard web", 3: "Revisionati raramente", 4: "Contratti ad hoc legali", 5: "Sistema di Risk Management legale"}),
        ("Tutela Proprietà Intellettuale", {1: "Nessuna", 2: "Marchio registrato", 3: "Protezione know-how base", 4: "Portafoglio brevetti", 5: "Strategia IP globale"}),
        ("Recupero Crediti Legale", {1: "Assente", 2: "Sporadico", 3: "Solleciti legali", 4: "Procedura strutturata", 5: "Assicurazione e legale integrato"}),
        ("Analisi Rischi Assicurativi", {1: "Nessuna", 2: "Obbligatorie", 3: "Coperture base", 4: "Analisi con Broker", 5: "All-risk e Cyber Insurance"})
    ],
    'Sicurezza sul Lavoro': [
        ("Aggiornamento DVR", {1: "Inesistente", 2: "Obsoleto", 3: "Base", 4: "Analitico e aggiornato", 5: "Digitale e dinamico"}),
        ("Formazione Obbligatoria", {1: "Scaduta", 2: "In corso", 3: "Monitorata base", 4: "Pienamente conforme", 5: "Cultura sicurezza diffusa"}),
        ("Sorveglianza Sanitaria", {1: "Assente", 2: "Ritardi visite", 3: "Nomina presente", 4: "Scadenze regolari", 5: "Focus benessere lavoratore"}),
        ("DPI e Manutenzioni", {1: "Nessun registro", 2: "Casual", 3: "Registro cartaceo", 4: "Programmata", 5: "Software manutenzione"}),
        ("Gestione Appalti (DUVRI)", {1: "Assente", 2: "Standard", 3: "Per grandi lavori", 4: "Accurato", 5: "Monitoraggio fornitori real-time"}),
        ("Infortuni e Near Miss", {1: "Frequenti", 2: "Non tracciati", 3: "Solo denunce obblig.", 4: "Analisi cause infortuni", 5: "Near miss tracciati e risolti"})
    ],
    # ... (Aggiungi qui le altre 6 aree per completare le 54 domande come nei codici precedenti)
}

# --- FUNZIONI DI NAVIGAZIONE ---
def go_to(page_name):
    st.session_state.page = page_name

# --- SIDEBAR NAVIGAZIONE ---
with st.sidebar:
    st.image("https://www.nextahub.it/wp-content/uploads/2023/05/logo-nextahub.png", width=180)
    st.title("Menu Principale")
    if st.button("🏠 1. Anagrafica Cliente", use_container_width=True): go_to("Anagrafica")
    if st.button("📝 2. Questionario", use_container_width=True): go_to("Questionario")
    if st.button("📊 3. Radar & Analisi AI", use_container_width=True): go_to("Valutazione")
    if st.button("💼 4. Servizi NextaHub", use_container_width=True): go_to("Servizi")
    if st.button("📁 5. Lista Clienti", use_container_width=True): go_to("Lista")

# --- PAGINA 1: ANAGRAFICA ---
if st.session_state.page == "Anagrafica":
    st.header("1️⃣ Anagrafica Potenziale Cliente")
    with st.form("anagrafica_form"):
        col1, col2 = st.columns(2)
        with col1:
            azienda = st.text_input("Ragione Sociale")
            piva = st.text_input("Partita IVA")
        with col2:
            indirizzo = st.text_input("Indirizzo e Civico")
            regione = st.selectbox("Regione", ["Lombardia", "Veneto", "Emilia-Romagna", "Piemonte", "Altro"])
        
        settore = st.selectbox("Settore", ["Manifatturiero", "Servizi", "Edilizia", "IT", "Agri-Food"])
        note = st.text_area("Note Commerciali")
        
        if st.form_submit_button("Salva e Vai al Questionario"):
            if azienda and piva:
                st.session_state.current_client_piva = piva
                st.session_state.clienti[piva] = {
                    "anagrafica": {"azienda": azienda, "piva": piva, "indirizzo": indirizzo, "regione" : regione, "settore": settore, "note": note},
                    "punteggi": {},
                    "analisi_ai": ""
                }
                go_to("Questionario")
                st.rerun()
            else:
                st.error("Inserisci Ragione Sociale e P.IVA")

# --- PAGINA 2: QUESTIONARIO ---
elif st.session_state.page == "Questionario":
    if not st.session_state.current_client_piva:
        st.warning("Torna in Anagrafica e inserisci un cliente.")
    else:
        piva = st.session_state.current_client_piva
        st.header(f"📝 Questionario: {st.session_state.clienti[piva]['anagrafica']['azienda']}")
        
        # Gestione risposte
        final_scores = {}
        tabs = st.tabs(list(DOMANDE_MATRICE.keys()))
        for i, area in enumerate(DOMANDE_MATRICE.keys()):
            with tabs[i]:
                punteggi_area = []
                for j, (testo, opzioni) in enumerate(DOMANDE_MATRICE[area]):
                    val = st.radio(testo, options=[1, 2, 3, 4, 5], format_func=lambda x: f"{x}: {opzioni[x]}", key=f"q_{piva}_{area}_{j}")
                    punteggi_area.append(val)
                final_scores[area] = sum(punteggi_area) / len(punteggi_area)
        
        if st.button("Salva Risposte e Genera Analisi"):
            st.session_state.clienti[piva]['punteggi'] = final_scores
            go_to("Valutazione")
            st.rerun()

# --- PAGINA 3: VALUTAZIONE (RADAR & AI) ---
elif st.session_state.page == "Valutazione":
    piva = st.session_state.current_client_piva
    if not piva or not st.session_state.clienti[piva]['punteggi']:
        st.warning("Completa prima il questionario.")
    else:
        cliente = st.session_state.clienti[piva]
        st.header(f"📊 Valutazione Strategica: {cliente['anagrafica']['azienda']}")
        
        # Radar Chart
        categories = list(cliente['punteggi'].keys())
        values = list(cliente['punteggi'].values())
        fig = go.Figure(data=go.Scatterpolar(r=values, theta=categories, fill='toself', line_color='#e63946'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        if st.button("Lancia Analisi AI"):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"Analizza l'azienda {cliente['anagrafica']['azienda']} con questi score: {cliente['punteggi']}. Crea roadmap 24 mesi."
                response = model.generate_content(prompt)
                st.session_state.clienti[piva]['analisi_ai'] = response.text
                st.success("Analisi Generata!")
            except: st.error("Errore API")
        
        if cliente['analisi_ai']:
            st.markdown(cliente['analisi_ai'])

# --- PAGINA 4: SERVIZI NEXTAHUB ---
elif st.session_state.page == "Servizi":
    piva = st.session_state.current_client_piva
    if not piva: st.warning("Seleziona un cliente.")
    else:
        st.header("💼 Soluzioni NextaHub Consigliate")
        scores = st.session_state.clienti[piva]['punteggi']
        
        col1, col2 = st.columns(2)
        with col1:
            if scores.get('Protezione Legale', 5) < 3:
                st.error("🆘 AREA CRITICA: PROTEZIONE LEGALE")
                st.write("- Implementazione Modello 231\n- Audit GDPR Completo\n- Revisione Contrattualistica")
            if scores.get('Strategia & Controllo', 5) < 3:
                st.error("🆘 AREA CRITICA: STRATEGIA")
                st.write("- Temporary Management\n- Business Plan Industriale")
        with col2:
            st.info("💎 PACCHETTO CONSIGLIATO")
            avg = sum(scores.values()) / len(scores)
            if avg < 2.5: st.subheader("MODELLO ELITE (Full Outsource)")
            elif avg < 4: st.subheader("MODELLO FLEX (Supporto Mirato)")
            else: st.subheader("MODELLO ENTRY (Certificazioni)")

# --- PAGINA 5: LISTA CLIENTI ---
elif st.session_state.page == "Lista":
    st.header("📁 Archivio Clienti Valutati")
    if not st.session_state.clienti:
        st.write("Nessun cliente in archivio.")
    else:
        for p, dati in st.session_state.clienti.items():
            col1, col2, col3 = st.columns([3, 2, 2])
            col1.write(f"**{dati['anagrafica']['azienda']}** ({p})")
            if col2.button("Recupera Analisi", key=f"rec_{p}"):
                st.session_state.current_client_piva = p
                go_to("Valutazione")
                st.rerun()
            if col3.button("Nuovo Test", key=f"new_{p}"):
                st.session_state.current_client_piva = p
                go_to("Questionario")
                st.rerun()
