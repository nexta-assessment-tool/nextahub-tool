import streamlit as st
import plotly.graph_objects as go
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="NextaHub Business Platform", layout="wide", initial_sidebar_state="expanded")

# --- INIZIALIZZAZIONE STATI ---
if 'page' not in st.session_state:
    st.session_state.page = "Anagrafica"
if 'clienti' not in st.session_state:
    st.session_state.clienti = {}
if 'current_client_piva' not in st.session_state:
    st.session_state.current_client_piva = None

# --- DATABASE INTEGRALE DELLE 9 AREE (54 DOMANDE) ---
DOMANDE_MATRICE = {
    'Strategia & Controllo': [
        ("Esiste un business plan o piano industriale?", {1: "No, navighiamo a vista", 2: "Visione a 2/3 mesi", 3: "Visione a 6 mesi", 4: "Piano a 1 anno", 5: "Piano strutturato a 2+ anni"}),
        ("Monitoraggio KPI e cruscotti aziendali", {1: "Nessun dato", 2: "Controllo costi a fine anno", 3: "Monitoraggio fatturato mensile", 4: "KPI operativi monitorati", 5: "Dashboard real-time integrata"}),
        ("Definizione dell'organigramma e ruoli", {1: "Tutti fanno tutto", 2: "Ruoli accennati", 3: "Organigramma base", 4: "Mansionari definiti", 5: "Struttura manageriale autonoma"}),
        ("Analisi della concorrenza e del mercato", {1: "Mai fatta", 2: "Reattiva", 3: "Analisi sporadica", 4: "Monitoraggio annuale", 5: "Strategia basata su dati"}),
        ("Sistemi di delega e processi decisionali", {1: "Accentramento totale", 2: "Delega minima", 3: "Prime deleghe operative", 4: "Processi condivisi", 5: "Delega manageriale completa"}),
        ("Passaggio generazionale/continuità", {1: "Problema ignorato", 2: "Discussioni vaghe", 3: "Consapevolezza rischio", 4: "Piano abbozzato", 5: "Piano formalizzato"})
    ],
    'Digitalizzazione': [
        ("Grado di adozione ERP/Gestionale", {1: "Carta/Excel", 2: "Software base", 3: "Gestionale aree separate", 4: "ERP integrato", 5: "ERP cloud con AI"}),
        ("Digitalizzazione dei processi (Paperless)", {1: "Tutto cartaceo", 2: "Archivio PDF semplice", 3: "Parziale firma elettronica", 4: "Processi digitali", 5: "100% paperless"}),
        ("Presenza di un CRM", {1: "Nessuno", 2: "Agenda contatti", 3: "Tracciamento offerte", 4: "CRM integrato", 5: "CRM predittivo"}),
        ("Cybersecurity e protezione dati", {1: "Nessuna", 2: "Antivirus base", 3: "Backup regolari", 4: "Firewall/Disaster Recovery", 5: "SOC e test periodici"}),
        ("Presenza online e strategia digital", {1: "Nessuna", 2: "Sito vetrina", 3: "Social attivi", 4: "Lead generation", 5: "E-commerce avanzato"}),
        ("Competenze digitali del team", {1: "Analfabetismo", 2: "Base (email)", 3: "Uso Office", 4: "Strumenti collab", 5: "Cultura digitale proattiva"})
    ],
    'Gestione HR': [
        ("Politiche di Welfare", {1: "Assenti", 2: "Rimborsi minimi", 3: "Convenzioni", 4: "Piano strutturato", 5: "Piattaforma welfare"}),
        ("Valutazione performance", {1: "Nessuna", 2: "Feedback sporadico", 3: "Incontri annuali", 4: "MBO strutturati", 5: "Feedback costante"}),
        ("Attrazione talenti (Employer Branding)", {1: "Turnover alto", 2: "Difficoltà reperimento", 3: "Brand noto locale", 4: "Strategie attive", 5: "Top Employer"}),
        ("Clima aziendale", {1: "Tensioni", 2: "Comunicazione verticale", 3: "Riunioni reparto", 4: "Sondaggi clima", 5: "Trasparenza e benessere"}),
        ("Piani di formazione/upskilling", {1: "Nessuno", 2: "Solo obbligatoria", 3: "Corsi sporadici", 4: "Piano annuale", 5: "Academy interna"}),
        ("Flessibilità e Smart Working", {1: "Solo presenza", 2: "Eccezioni", 3: "Flessibilità oraria", 4: "Policy attiva", 5: "Lavoro per obiettivi"})
    ],
    'Finanza & Investimenti': [
        ("Pianificazione Cash Flow", {1: "Nessuna", 2: "Estratto conto", 3: "Previsione 30gg", 4: "Budget 6 mesi", 5: "Software real-time"}),
        ("Utilizzo Finanza Agevolata", {1: "Mai usata", 2: "Informati", 3: "Occasionale", 4: "Monitoraggio attivo", 5: "Strategia sistematica"}),
        ("Rapporto con Istituti di Credito", {1: "Difficile", 2: "Solo affidamenti base", 3: "Trasparenza", 4: "Rating monitorato", 5: "Mix bilanciato"}),
        ("Controllo Gestione/Margini", {1: "Sconosciuti", 2: "Margine globale", 3: "Per commessa", 4: "Analisi mensile scostamenti", 5: "Analisi predittiva"}),
        ("Gestione Credito/Insoluti", {1: "Nessuno", 2: "Solleciti rari", 3: "Assicurazione credito", 4: "Procedura rigida", 5: "Scoring preventivo"}),
        ("Investimenti R&S", {1: "Nulli", 2: "Migliorie base", 3: "Progetti sporadici", 4: "Budget annuale", 5: "Innovazione core"})
    ],
    'Sostenibilità (ESG)': [
        ("Sensibilità ESG", {1: "Sconosciuta", 2: "Curiosità", 3: "Base", 4: "Obiettivi nel piano", 5: "DNA aziendale"}),
        ("Certificazioni Ambientali", {1: "Nessuna", 2: "Studio", 3: "Gestione rifiuti", 4: "ISO 14001", 5: "Carbon Neutral"}),
        ("Parità di Genere/Inclusion", {1: "Nessuna", 2: "Sensibilità", 3: "Equità base", 4: "Certificata", 5: "Leadership bilanciata"}),
        ("Sostenibilità Filiera", {1: "Solo prezzo", 2: "Audit base", 3: "Codice etico", 4: "Valutazione ESG fornitori", 5: "Filiera certificata"}),
        ("Efficienza Energetica", {1: "Sprechi", 2: "Monitoraggio bollette", 3: "Efficientamento base", 4: "Audit professionale", 5: "Renewables/Autoproduzione"}),
        ("Bilancio Sostenibilità", {1: "Nulla", 2: "News sito", 3: "Report base", 4: "Bilancio annuale", 5: "Report GRI integrato"})
    ],
    'Protezione Legale': [
        ("Modello 231", {1: "Assente", 2: "In valutazione", 3: "Vecchio", 4: "Aggiornato", 5: "ODV attivo"}),
        ("Compliance GDPR", {1: "Nulla", 2: "Informative", 3: "Registri", 4: "Audit", 5: "DPO presente"}),
        ("Contrattualistica", {1: "Verbali", 2: "Web standard", 3: "Revisioni rare", 4: "Contratti ad hoc", 5: "Risk Management legale"}),
        ("Tutela IP (Marchi/Brevetti)", {1: "Nessuna", 2: "Marchio", 3: "Know-how protetto", 4: "Brevetti", 5: "Strategia IP globale"}),
        ("Recupero Crediti Legale", {1: "Assente", 2: "Sporadico", 3: "Solleciti", 4: "Procedura strutturata", 5: "Legale integrato"}),
        ("Rischi Assicurativi", {1: "Nessuna", 2: "Obbligatorie", 3: "Base", 4: "Analisi Broker", 5: "Cyber/D&O Insurance"})
    ],
    'Sicurezza sul Lavoro': [
        ("Aggiornamento DVR", {1: "Inesistente", 2: "Obsoleto", 3: "Base", 4: "Analitico", 5: "Dinamico"}),
        ("Formazione Obbligatoria", {1: "Scaduta", 2: "Parziale", 3: "Monitorata", 4: "Conforme", 5: "Cultura sicurezza"}),
        ("Sorveglianza Sanitaria", {1: "Assente", 2: "Ritardi", 3: "Nomina presente", 4: "Regolare", 5: "Benessere totale"}),
        ("DPI e Manutenzioni", {1: "Nessuno", 2: "Casual", 3: "Registro base", 4: "Programmata", 5: "Digitale"}),
        ("Gestione Appalti (DUVRI)", {1: "Assente", 2: "Standard", 3: "Grandi lavori", 4: "Accurato", 5: "Real-time"}),
        ("Cultura Near Miss", {1: "Nessuna", 2: "Solo infortuni", 3: "Tracciamento base", 4: "Analisi cause", 5: "Zero infortuni"})
    ],
    'Standard & Qualità': [
        ("Certificazione ISO 9001", {1: "Assente", 2: "In corso", 3: "Formale", 4: "Sostanziale", 5: "Miglioramento continuo"}),
        ("Manuale Procedure", {1: "Assente", 2: "Verbali", 3: "Qualche documento", 4: "Procedure scritte", 5: "Processi ottimizzati"}),
        ("Gestione Non Conformità", {1: "Ignorate", 2: "Reattive", 3: "Registro", 4: "Analisi cause", 5: "Kaizen"}),
        ("Soddisfazione Cliente", {1: "Mai chiesta", 2: "Solo reclami", 3: "Sondaggio annuale", 4: "Analisi NPS", 5: "Customer Centricity"}),
        ("Audit Interni", {1: "Mai fatti", 2: "Rari", 3: "Pre-rinnovo", 4: "Semestrali", 5: "Auto-controllo"}),
        ("Qualità Fornitori", {1: "Solo prezzo", 2: "Scelta base", 3: "Albo fornitori", 4: "Valutazione annuale", 5: "Partnership certificate"})
    ],
    'Sviluppo Competenze': [
        ("Piano Formativo", {1: "Assente", 2: "Solo obbligatoria", 3: "Tecnica sporadica", 4: "Basato su gap", 5: "Crescita continua"}),
        ("Fondi Interprofessionali", {1: "Mai sentiti", 2: "Noti non usati", 3: "Iscrizione", 4: "Corsi singoli", 5: "Piani finanziati complessi"}),
        ("Mentoring/Coaching", {1: "Assente", 2: "Affiancamento", 3: "Tutor", 4: "Percorsi coaching", 5: "Cultura mentoring"}),
        ("Soft Skills/Digital Mindset", {1: "Nulle", 2: "Base", 3: "Discrete", 4: "Problem solving", 5: "Leadership diffusa"}),
        ("Tracciamento Competenze", {1: "Nessuno", 2: "CV", 3: "Excel", 4: "Matrice competenze", 5: "Software Talenti"}),
        ("Knowledge Sharing", {1: "Nulla", 2: "Appunti", 3: "Cartelle", 4: "Manuali", 5: "Wiki aziendale"})
    ]
}

# --- FUNZIONI NAVIGAZIONE ---
def go_to(page_name):
    st.session_state.page = page_name

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://www.nextahub.it/wp-content/uploads/2023/05/logo-nextahub.png", width=180)
    st.title("NextaHub CRM")
    st.button("🏠 1. Anagrafica", on_click=go_to, args=("Anagrafica",), use_container_width=True)
    st.button("📝 2. Questionario", on_click=go_to, args=("Questionario",), use_container_width=True)
    st.button("📊 3. Analisi AI", on_click=go_to, args=("Valutazione",), use_container_width=True)
    st.button("💼 4. Offerta", on_click=go_to, args=("Servizi",), use_container_width=True)
    st.button("📁 5. Archivio", on_click=go_to, args=("Lista",), use_container_width=True)

# --- PAGINA 1: ANAGRAFICA ---
if st.session_state.page == "Anagrafica":
    st.header("1️⃣ Anagrafica Potenziale Cliente")
    with st.form("anagrafica"):
        col1, col2 = st.columns(2)
        with col1:
            azienda = st.text_input("Ragione Sociale")
            piva = st.text_input("Partita IVA")
        with col2:
            indirizzo = st.text_input("Indirizzo Sede Completo")
            regione = st.selectbox("Regione", ["Lombardia", "Veneto", "Piemonte", "Emilia-Romagna", "Lazio", "Campania", "Altro"])
        settore = st.selectbox("Settore", ["Manifatturiero", "IT", "Servizi", "Edilizia", "Agri-Food"])
        if st.form_submit_button("Avvia Assessment"):
            if azienda and piva:
                st.session_state.current_client_piva = piva
                st.session_state.clienti[piva] = {
                    "anagrafica": {"azienda": azienda, "piva": piva, "indirizzo": indirizzo, "regione": regione, "settore": settore},
                    "punteggi": {}, "analisi_ai": ""
                }
                go_to("Questionario")
                st.rerun()

# --- PAGINA 2: QUESTIONARIO ---
elif st.session_state.page == "Questionario":
    piva = st.session_state.current_client_piva
    if not piva: st.warning("Inserisci prima l'anagrafica.")
    else:
        st.header(f"📝 Questionario Diagnostico: {st.session_state.clienti[piva]['anagrafica']['azienda']}")
        scores = {}
        tabs = st.tabs(list(DOMANDE_MATRICE.keys()))
        for i, area in enumerate(DOMANDE_MATRICE.keys()):
            with tabs[i]:
                p_area = []
                for j, (q, opts) in enumerate(DOMANDE_MATRICE[area]):
                    val = st.radio(q, [1,2,3,4,5], format_func=lambda x: f"{x}: {opts[x]}", key=f"{piva}_{area}_{j}")
                    p_area.append(val)
                scores[area] = sum(p_area)/len(p_area)
        if st.button("Salva e Analizza"):
            st.session_state.clienti[piva]['punteggi'] = scores
            go_to("Valutazione")
            st.rerun()

# --- PAGINA 3: ANALISI AI & RADAR ---
elif st.session_state.page == "Valutazione":
    piva = st.session_state.current_client_piva
    cliente = st.session_state.clienti.get(piva)
    if not cliente or not cliente['punteggi']: st.warning("Dati incompleti.")
    else:
        st.header(f"📊 Analisi Strategica AI: {cliente['anagrafica']['azienda']}")
        fig = go.Figure(data=go.Scatterpolar(r=list(cliente['punteggi'].values()), theta=list(cliente['punteggi'].keys()), fill='toself', line_color='#e63946'))
        st.plotly_chart(fig, use_container_width=True)
        
        if st.button("Genera Analisi Profonda (Dati Pubblici + Territorialità)"):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-1.5-flash')
                # PROMPT POTENZIATO CON DATI ANAGRAFICI
                prompt = f"""
                Analizza l'azienda {cliente['anagrafica']['azienda']}.
                Dati Anagrafici: P.IVA {cliente['anagrafica']['piva']}, Indirizzo: {cliente['anagrafica']['indirizzo']}, Regione: {cliente['anagrafica']['regione']}.
                Settore: {cliente['anagrafica']['settore']}.
                Risultati Assessment: {cliente['punteggi']}.
                
                Richiesta:
                1. VALUTAZIONE TERRITORIALE: Basandoti sulla regione ({cliente['anagrafica']['regione']}), identifica bandi regionali attivi o rischi specifici del distretto industriale di riferimento.
                2. ANALISI P.IVA: Simula un'analisi dei dati pubblici (es. solidità percepita, obblighi normativi per quella dimensione aziendale).
                3. ROADMAP: Definisci FASE 1 (Urgenze 0-3 mesi), FASE 2 (Sviluppo 6-12 mesi).
                """
                with st.spinner("L'AI sta incrociando i dati territoriali e normativi..."):
                    res = model.generate_content(prompt)
                    cliente['analisi_ai'] = res.text
                    st.markdown(res.text)
            except Exception as e: st.error(f"Errore: {e}")

# --- PAGINA 4: SERVIZI ---
elif st.session_state.page == "Servizi":
    piva = st.session_state.current_client_piva
    if piva:
        st.header("💼 Soluzioni NextaHub Personalizzate")
        st.write("In base alle criticità rilevate, ecco la proposta commerciale:")
        scores = st.session_state.clienti[piva]['punteggi']
        for area, s in scores.items():
            if s < 3: st.error(f"⚠️ {area}: Servizio consigliato -> {area} Specialist Nexta")
        avg = sum(scores.values())/len(scores)
        st.info(f"Modello suggerito: {'ELITE (Outsourcing totale)' if avg < 2.5 else 'FLEX (Supporto strategico)'}")

# --- PAGINA 5: ARCHIVIO ---
elif st.session_state.page == "Lista":
    st.header("📁 Archivio Analisi")
    for p, d in st.session_state.clienti.items():
        with st.expander(f"{d['anagrafica']['azienda']} - {p}"):
            st.write(f"Sede: {d['anagrafica']['indirizzo']}")
            if st.button("Carica Analisi", key=f"btn_{p}"):
                st.session_state.current_client_piva = p
                go_to("Valutazione")
                st.rerun()
