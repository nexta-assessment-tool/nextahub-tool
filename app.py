import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="NextaHub Strategic Suite", layout="wide", initial_sidebar_state="expanded")

# --- CSS PER LA STAMPA ---
st.markdown("""
    <style>
    @media print {
        [data-testid="stSidebar"], header, footer, .stButton, [data-testid="stToolbar"], .stTabs [data-baseweb="tab-list"] {
            display: none !important;
        }
        .main .block-container { padding: 1rem !important; max-width: 100% !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE BENCHMARK ---
BENCHMARK_DATI = {
    "Agroalimentare (Food & Beverage)": {"Strategia & Controllo": 3.4, "Digitalizzazione": 3.0, "Gestione HR": 3.1, "Finanza & Investimenti": 3.2, "Sostenibilità (ESG)": 3.8, "Protezione Legale": 3.5, "Sicurezza sul Lavoro": 4.2, "Standard & Qualità": 4.5, "Sviluppo Competenze": 3.0},
    "Moda e Tessile (Fashion & Luxury)": {"Strategia & Controllo": 3.6, "Digitalizzazione": 3.8, "Gestione HR": 3.5, "Finanza & Investimenti": 3.4, "Sostenibilità (ESG)": 4.0, "Protezione Legale": 4.2, "Sicurezza sul Lavoro": 3.5, "Standard & Qualità": 4.0, "Sviluppo Competenze": 3.7},
    "Arredo e Design (Furniture)": {"Strategia & Controllo": 3.2, "Digitalizzazione": 3.2, "Gestione HR": 3.3, "Finanza & Investimenti": 3.1, "Sostenibilità (ESG)": 3.5, "Protezione Legale": 3.4, "Sicurezza sul Lavoro": 3.8, "Standard & Qualità": 3.7, "Sviluppo Competenze": 3.2},
    "Meccanica e Automazione": {"Strategia & Controllo": 3.5, "Digitalizzazione": 3.8, "Gestione HR": 3.4, "Finanza & Investimenti": 3.6, "Sostenibilità (ESG)": 3.0, "Protezione Legale": 3.5, "Sicurezza sul Lavoro": 4.5, "Standard & Qualità": 4.2, "Sviluppo Competenze": 3.8},
    "Metallurgia e Siderurgia": {"Strategia & Controllo": 3.2, "Digitalizzazione": 2.8, "Gestione HR": 3.0, "Finanza & Investimenti": 3.8, "Sostenibilità (ESG)": 2.8, "Protezione Legale": 3.2, "Sicurezza sul Lavoro": 4.8, "Standard & Qualità": 3.8, "Sviluppo Competenze": 3.0},
    "Automotive (Automobilistico)": {"Strategia & Controllo": 3.8, "Digitalizzazione": 4.2, "Gestione HR": 3.7, "Finanza & Investimenti": 3.5, "Sostenibilità (ESG)": 3.8, "Protezione Legale": 3.8, "Sicurezza sul Lavoro": 4.6, "Standard & Qualità": 4.7, "Sviluppo Competenze": 4.0},
    "Chimico e Farmaceutico": {"Strategia & Controllo": 3.7, "Digitalizzazione": 3.9, "Gestione HR": 3.8, "Finanza & Investimenti": 3.6, "Sostenibilità (ESG)": 4.2, "Protezione Legale": 4.5, "Sicurezza sul Lavoro": 4.9, "Standard & Qualità": 4.8, "Sviluppo Competenze": 3.9},
    "Energia e Utilities": {"Strategia & Controllo": 3.9, "Digitalizzazione": 4.0, "Gestione HR": 3.8, "Finanza & Investimenti": 4.0, "Sostenibilità (ESG)": 4.5, "Protezione Legale": 4.0, "Sicurezza sul Lavoro": 4.6, "Standard & Qualità": 4.3, "Sviluppo Competenze": 3.7},
    "Costruzioni ed Edilizia": {"Strategia & Controllo": 2.8, "Digitalizzazione": 2.5, "Gestione HR": 2.9, "Finanza & Investimenti": 3.0, "Sostenibilità (ESG)": 2.7, "Protezione Legale": 3.4, "Sicurezza sul Lavoro": 4.7, "Standard & Qualità": 3.4, "Sviluppo Competenze": 2.8},
    "Elettronica ed Elettrotecnica": {"Strategia & Controllo": 3.5, "Digitalizzazione": 4.0, "Gestione HR": 3.5, "Finanza & Investimenti": 3.4, "Sostenibilità (ESG)": 3.2, "Protezione Legale": 3.6, "Sicurezza sul Lavoro": 4.0, "Standard & Qualità": 4.3, "Sviluppo Competenze": 3.9},
    "Gomma e Materie Plastiche": {"Strategia & Controllo": 3.1, "Digitalizzazione": 3.0, "Gestione HR": 3.1, "Finanza & Investimenti": 3.3, "Sostenibilità (ESG)": 3.0, "Protezione Legale": 3.2, "Sicurezza sul Lavoro": 4.4, "Standard & Qualità": 3.9, "Sviluppo Competenze": 3.0},
    "Carta e Stampa": {"Strategia & Controllo": 3.3, "Digitalizzazione": 3.4, "Gestione HR": 3.2, "Finanza & Investimenti": 3.2, "Sostenibilità (ESG)": 3.7, "Protezione Legale": 3.3, "Sicurezza sul Lavoro": 4.1, "Standard & Qualità": 4.0, "Sviluppo Competenze": 3.1},
    "ICT e Digitale": {"Strategia & Controllo": 4.0, "Digitalizzazione": 4.8, "Gestione HR": 4.2, "Finanza & Investimenti": 3.6, "Sostenibilità (ESG)": 3.5, "Protezione Legale": 4.0, "Sicurezza sul Lavoro": 3.0, "Standard & Qualità": 3.8, "Sviluppo Competenze": 4.5},
    "Logistica e Trasporti": {"Strategia & Controllo": 3.4, "Digitalizzazione": 3.8, "Gestione HR": 3.3, "Finanza & Investimenti": 3.2, "Sostenibilità (ESG)": 3.2, "Protezione Legale": 3.5, "Sicurezza sul Lavoro": 4.3, "Standard & Qualità": 3.7, "Sviluppo Competenze": 3.2},
    "Turismo e Ristorazione": {"Strategia & Controllo": 2.9, "Digitalizzazione": 3.2, "Gestione HR": 3.5, "Finanza & Investimenti": 2.8, "Sostenibilità (ESG)": 3.3, "Protezione Legale": 3.1, "Sicurezza sul Lavoro": 3.8, "Standard & Qualità": 3.5, "Sviluppo Competenze": 3.4},
    "Bancario e Assicurativo": {"Strategia & Controllo": 4.5, "Digitalizzazione": 4.3, "Gestione HR": 4.0, "Finanza & Investimenti": 4.5, "Sostenibilità (ESG)": 4.2, "Protezione Legale": 4.8, "Sicurezza sul Lavoro": 3.5, "Standard & Qualità": 4.6, "Sviluppo Competenze": 4.2},
    "Sanità e Servizi Sociali": {"Strategia & Controllo": 3.8, "Digitalizzazione": 3.5, "Gestione HR": 4.0, "Finanza & Investimenti": 3.2, "Sostenibilità (ESG)": 3.7, "Protezione Legale": 4.2, "Sicurezza sul Lavoro": 4.6, "Standard & Qualità": 4.5, "Sviluppo Competenze": 3.9}
}

# --- MATRICE INTEGRALE 54 DOMANDE ---
DOMANDE_MATRICE = {
    'Strategia & Controllo': [
        ("Piano Strategico", ["Nessun piano", "Obiettivi verbali", "Budget annuale", "Piano triennale", "Piano dinamico trimestrale"]),
        ("Monitoraggio KPI", ["Assente", "Solo bilancio", "Excel saltuario", "Dashboard mensile", "BI real-time"]),
        ("Organigramma", ["Solo titolare", "Confuso", "Schema base", "Definito", "Manager autonomi"]),
        ("Analisi Competitor", ["Mai", "Rara", "Annuale fatturato", "Monitoraggio costante", "Data-driven"]),
        ("Delega", ["Nessuna", "Compiti semplici", "Capi area", "Responsabilità budget", "Direzione generale"]),
        ("Passaggio Generazionale", ["Tabù", "Informale", "Successori scelti", "Piano attivo", "Formalizzato"])
    ],
    'Digitalizzazione': [
        ("ERP/Gestionale", ["Solo fatture", "Contabilità", "Settoriale", "Integrato", "Cloud avanzato"]),
        ("Processi Paperless", ["Cartaceo", "Pochi PDF", "Misto", "Quasi tutto digitale", "100% digitale"]),
        ("CRM", ["Nessuno", "Excel", "Anagrafica/Offerte", "Marketing integrato", "Automation"]),
        ("Cybersecurity", ["Antivirus free", "Backup saltuari", "Cloud backup/Policy", "Audit/Firewall", "Soc 24/7"]),
        ("Presenza Web", ["Assente", "Sito vetrina", "Sito aggiornato/Social", "ADS strutturate", "Lead generation"]),
        ("Intelligenza Artificiale", ["Nulla", "Uso sporadico", "Test processi", "Integrata in un'area", "AI-driven"])
    ],
    'Gestione HR': [
        ("Welfare", ["No", "Rimborsi minimi", "Convenzioni base", "Piattaforma welfare", "Benefit evoluti"]),
        ("Valutazione", ["No", "Sensazione titolare", "Annuale", "MBO/KPI", "Feedback continuo"]),
        ("Retention", ["Alta fuga", "Turnover medio", "Bonus sporadici", "Employer branding", "Leader attrazione"]),
        ("Clima Aziendale", ["Mai", "Solo in crisi", "Saltuario", "Indagine annuale", "Monitoraggio continuo"]),
        ("Formazione", ["Solo legge", "Corsi tecnici rari", "Budget annuo", "Piani ad hoc", "Academy interna"]),
        ("Flessibilità", ["Rigida", "Permessi rari", "Flessibilità oraria", "Smart working", "Work from anywhere"])
    ],
    'Finanza & Investimenti': [
        ("Cash Flow", ["Ignorato", "Saldo banca", "Pianificazione mensile", "Previsionale 3 mesi", "Real-time predittivo"]),
        ("Finanza Agevolata", ["Mai", "Rara", "Usata una volta", "Monitoraggio bandi", "Pianificazione strategica"]),
        ("Rating Bancario", ["Sconosciuto", "Vago", "Controllato annuale", "Trimestrale", "Ottimizzazione attiva"]),
        ("Analisi Margini", ["Solo utile finale", "Stime prodotto", "Calcolo core business", "Analitica per ordine", "Predittiva"]),
        ("Crediti", ["Reattiva", "Mail sporadiche", "Procedura scritta", "Ufficio dedicato", "Assicurazione/Automazione"]),
        ("R&S", ["0%", "Solo reattiva", "1-2% fatturato", "5% fatturato", ">5% innovazione"])
    ],
    'Sostenibilità (ESG)': [
        ("Approccio ESG", ["Nessuno", "Obblighi legge", "Prime azioni", "Integrazione strategia", "Bilancio Sostenibilità"]),
        ("Ambiente", ["Nessuna misura", "Rifiuti", "Monitoraggio consumi", "Carbon Footprint", "Net Zero"]),
        ("Inclusione", ["Nessuna", "Sensibilità", "Donne in ruoli chiave", "Policy scritte", "Certificazione Parità"]),
        ("Etica", ["Nessuna", "Leggi base", "Codice Etico", "Trasparenza/Legalità", "Governance certificata"]),
        ("Fornitori", ["Solo prezzo", "Vicinanza", "Autocertificazioni", "Audit ESG", "Solo partner ESG"]),
        ("Certificazioni", ["Nessuna", "Valutazione", "ISO 14001", "Multiple", "Benefit/B-Corp"])
    ],
    'Protezione Legale': [
        ("Modello 231", ["No", "In studio", "Adottato", "Aggiornato/Formazione", "ODV attivo"]),
        ("GDPR", ["No", "Base vecchio", "Sì", "Audit regolari", "DPO nominato"]),
        ("Contratti", ["Verbali", "Web download", "Standard revisionati", "Ad hoc specifici", "Legal management"]),
        ("IP/Marchi", ["No", "Registrato", "Monitoraggio", "Strategia attiva", "Asset brevettuale"]),
        ("Rischi", ["Emergenza", "Avvocato al bisogno", "Assicurazione base", "Consulenza fissa", "Analisi preventiva"]),
        ("D&O Polizza", ["No", "Valutazione", "Titolare", "Board", "Completa massimali alti"])
    ],
    'Sicurezza sul Lavoro': [
        ("DVR", ["Scaduto", "Obsoleto", "Aggiornato", "Dinamico", "Eccellenza"]),
        ("Formazione", ["Nessuna", "Base legge", "Tutti in regola", "Avanzata tracciata", "Cultura valore"]),
        ("Medicina", ["Assente", "Parziale", "Sì regolare", "Monitorata", "Benessere extra"]),
        ("DPI", ["Libero", "Consegna base", "Registro cartaceo", "Digitale", "Distributori auto"]),
        ("Manutenzione", ["A guasto", "Libretto", "Programmata", "Software", "Predittiva"]),
        ("Near Miss", ["No", "Rari", "Solo gravi", "Procedura attiva", "Target Zero"])
    ],
    'Standard & Qualità': [
        ("ISO 9001", ["No", "Valutazione", "Solo formale", "Applicata", "Motore eccellenza"]),
        ("Processi", ["Testa", "Verbali", "Procedure core", "Mappatura totale", "Ottimizzazione"]),
        ("Controlli", ["Fine", "Campione", "Sistemico", "Ogni fase", "Real-time dati"]),
        ("Customer Sat", ["No", "Reclami", "Sondaggio annuo", "NPS", "Focus group"]),
        ("Qualifica Fornitori", ["Prezzo", "Storici", "Albo", "Rating", "Partnership"]),
        ("Non Conformità", ["Risolte/Perse", "Fogli Excel", "Analisi cause", "Azioni correttive", "Prevenzione"])
    ],
    'Sviluppo Competenze': [
        ("Gap Analysis", ["No", "Titolare", "Su richiesta", "Annuale", "Strategica futuro"]),
        ("Fondi", ["Mai", "Nozioni base", "Rari", "Sempre", "Ottimizzazione"]),
        ("Learning", ["Lavoro", "Affiancamento", "Manuali", "E-learning", "Academy"]),
        ("Leadership", ["No", "Titolare", "Capi reparto", "Coaching manager", "Diffusa"]),
        ("Carriera", ["No", "Anzianità", "Sporadica", "Piani chiari", "Meritocrazia"]),
        ("Mindset", ["Sempre fatto così", "Paura", "Alcuni", "Aperta", "DNA innovatore"])
    ]
}

# --- STATO DELL'APPLICAZIONE ---
if 'page' not in st.session_state: st.session_state.page = "Anagrafica"
if 'clienti' not in st.session_state: st.session_state.clienti = {}
if 'current_piva' not in st.session_state: st.session_state.current_piva = None

LOGO_URL = "https://www.nextahub.it/wp-content/uploads/2023/05/logo-nextahub.png"

# --- SIDEBAR ---
with st.sidebar:
    st.image(LOGO_URL, width=180)
    st.markdown("---")
    if st.button("🏠 1. Anagrafica Cliente", use_container_width=True): st.session_state.page = "Anagrafica"
    if st.button("📝 2. Nuovo Assessment", use_container_width=True): st.session_state.page = "Questionario"
    if st.button("📊 3. Report & Analisi AI", use_container_width=True): st.session_state.page = "Valutazione"
    if st.button("📁 4. Archivio Storico", use_container_width=True): st.session_state.page = "Archivio"
    st.markdown("---")
    if st.session_state.current_piva:
        st.info(f"Cliente: {st.session_state.current_piva}")

# --- PAGINA 1: ANAGRAFICA ---
if st.session_state.page == "Anagrafica":
    st.title("🏢 Setup Anagrafica Cliente")
    with st.form("anag_full"):
        c1, c2 = st.columns(2)
        with c1:
            azienda = st.text_input("Ragione Sociale")
            piva = st.text_input("Partita IVA")
            indirizzo = st.text_input("Via e Civico")
            cap = st.text_input("CAP", max_chars=5)
        with c2:
            citta = st.text_input("Comune")
            provincia = st.text_input("Provincia (Sigla)", max_chars=2).upper()
            regione = st.selectbox("Regione", ["Abruzzo", "Basilicata", "Calabria", "Campania", "Emilia-Romagna", "Friuli-Venezia Giulia", "Lazio", "Liguria", "Lombardia", "Marche", "Molise", "Piemonte", "Puglia", "Sardegna", "Sicilia", "Toscana", "Trentino-Alto Adige", "Umbria", "Valle d'Aosta", "Veneto"])
            settore = st.selectbox("Settore", list(BENCHMARK_DATI.keys()))
        
        if st.form_submit_button("Salva e Inizia"):
            if azienda and piva:
                st.session_state.current_piva = piva
                st.session_state.clienti[piva] = {
                    "info": {"azienda": azienda, "piva": piva, "indirizzo": indirizzo, "cap": cap, "citta": citta, "provincia": provincia, "regione": regione, "settore": settore},
                    "assessments": []
                }
                st.session_state.page = "Questionario"
                st.rerun()
            else:
                st.error("Inserire Ragione Sociale e P.Iva.")

# --- PAGINA 2: QUESTIONARIO ---
elif st.session_state.page == "Questionario":
    piva = st.session_state.current_piva
    if not piva: st.warning("Configura l'anagrafica."); st.stop()
    
    st.title(f"📝 Assessment: {st.session_state.clienti[piva]['info']['azienda']}")
    tabs = st.tabs(list(DOMANDE_MATRICE.keys()))
    temp_scores = {}

    for i, area in enumerate(DOMANDE_MATRICE.keys()):
        with tabs[i]:
            st.subheader(area)
            area_vals = []
            for j, (domanda, opzioni) in enumerate(DOMANDE_MATRICE[area]):
                scelta = st.radio(f"**{j+1}. {domanda}**", options=[1, 2, 3, 4, 5], format_func=lambda x: f"{x} - {opzioni[x-1]}", key=f"{piva}_{area}_{j}")
                area_vals.append(scelta)
            temp_scores[area] = sum(area_vals) / 6

    if st.button("Finalizza Assessment", use_container_width=True):
        nuovo = {"data": datetime.now().strftime("%d/%m/%Y %H:%M"), "punteggi": temp_scores, "analisi_ai": ""}
        st.session_state.clienti[piva]['assessments'].append(nuovo)
        st.session_state.page = "Valutazione"
        st.rerun()

# --- PAGINA 3: VALUTAZIONE ---
elif st.session_state.page == "Valutazione":
    piva = st.session_state.current_piva
    if not piva or not st.session_state.clienti[piva]['assessments']: st.warning("Nessun dato."); st.stop()
    
    cl = st.session_state.clienti[piva]
    ass = cl['assessments'][-1]
    
    # Header Stampa
    c1, c2 = st.columns([1, 2])
    with c1: st.image(LOGO_URL, width=200)
    with c2:
        st.markdown(f"## REPORT STRATEGICO\n**{cl['info']['azienda']}** | {cl['info']['citta']} ({cl['info']['provincia']})")
        st.caption(f"Settore: {cl['info']['settore']} | Data: {ass['data']}")

    # Radar
    categorie = list(ass['punteggi'].keys())
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=list(ass['punteggi'].values()), theta=categorie, fill='toself', name='Azienda', line_color='#e63946'))
    fig.add_trace(go.Scatterpolar(r=[BENCHMARK_DATI[cl['info']['settore']][c] for c in categorie], theta=categorie, name='Benchmark Settore', line_color='gray', line_dash='dash'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), height=600)
    st.plotly_chart(fig, use_container_width=True)

    # Analisi AI
    st.markdown("---")
    st.subheader("🤖 Analisi Strategica Agente AI")
    if not ass['analisi_ai']:
        if st.button("Attiva Agente AI (Analisi Territoriale)"):
            # Simulazione prompt AI
            info = cl['info']
            analisi = f"L'azienda operante a {info['citta']} nel settore {info['settore']} mostra un forte scostamento in {min(ass['punteggi'], key=ass['punteggi'].get)}. Data la posizione in {info['regione']}, si consiglia di monitorare i competitor locali e investire in digitalizzazione."
            ass['analisi_ai'] = analisi
            st.rerun()
    else:
        st.info(ass['analisi_ai'])

# --- PAGINA 4: ARCHIVIO ---
elif st.session_state.page == "Archivio":
    st.title("📁 Archivio Storico")
    if not st.session_state.clienti:
        st.info("Nessun cliente in archivio.")
    else:
        for p, dati in st.session_state.clienti.items():
            with st.expander(f"🏢 {dati['info']['azienda']} (PI: {p})"):
                st.write(f"Sede: {dati['info']['regione']} | Settore: {dati['info']['settore']}")
                for i, revisione in enumerate(dati['assessments']):
                    col_x, col_y = st.columns([4, 1])
                    col_x.write(f"Analisi del {revisione['data']}")
                    if col_y.button("Apri", key=f"open_{p}_{i}"):
                        st.session_state.current_piva = p
                        st.session_state.page = "Valutazione"
                        st.rerun()
