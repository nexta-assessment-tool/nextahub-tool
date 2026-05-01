import streamlit as st
import plotly.graph_objects as go
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="NextaHub Strategic Suite", layout="wide", initial_sidebar_state="expanded")

# --- CSS PER LA STAMPA ---
st.markdown("""
    <style>
    @media print {
        header, [data-testid="stSidebar"], .stButton {
            display: none !important;
        }
        .main .block-container {
            padding-top: 1rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# --- BENCHMARK DI SETTORE AGGIORNATI (17 SETTORI) ---
BENCHMARK_DATI = {
    "Agroalimentare (Food & Beverage)": {"Strategia & Controllo": 3.4, "Digitalizzazione": 3.0, "Gestione HR": 3.1, "Finanza & Investimenti": 3.2, "Sostenibilità (ESG)": 3.8, "Protezione Legale": 3.5, "Sicurezza sul Lavoro": 4.2, "Standard & Qualità": 4.5, "Sviluppo Competenze": 3.0},
    "Moda e Tessile (Fashion & Luxury)": {"Strategia & Controllo": 3.6, "Digitalizzazione": 3.8, "Gestione HR": 3.5, "Finanza & Investimenti": 3.4, "Sostenibilità (ESG)": 4.0, "Protezione Legale": 4.2, "Sicurezza sul Lavoro": 3.5, "Standard & Qualità": 4.0, "Sviluppo Competenze": 3.7},
    "Arredo e Design (Furniture)": {"Strategia & Controllo": 3.2, "Digitalizzazione": 3.2, "Gestione HR": 3.3, "Finanza & Investimenti": 3.1, "Sostenibilità (ESG)": 3.5, "Protezione Legale": 3.4, "Sicurezza sul Lavoro": 3.8, "Standard & Qualità": 3.7, "Sviluppo Competenze": 3.2},
    "Meccanica e Automazione": {"Strategia & Controllo": 3.5, "Digitalizzazione": 3.8, "Gestione HR": 3.4, "Finanza & Investimenti": 3.6, "Sostenibilità (ESG)": 3.0, "Protezione Legale": 3.5, "Sicurezza sul Lavoro": 4.5, "Standard & Qualità": 4.2, "Sviluppo Competenze": 3.8},
    "Metallurgia e Siderurgia": {"Strategia & Controllo": 3.2, "Digitalizzazione": 2.8, "Gestione HR": 3.0, "Finanza & Investimenti": 3.8, "Sostenibilità (ESG)": 2.8, "Protezione Legale": 3.2, "Sicurezza sul Lavoro": 4.8, "Standard & Qualità": 3.8, "Sviluppo Competenze": 3.0},
    "Automotive (Automobilistico)": {"Strategia & Controllo": 3.8, "Digitalizzazione": 4.2, "Gestione HR": 3.7, "Finanza & Investimenti": 3.5, "Sostenibilità (ESG)": 3.8, "Protezione Legale": 3.8, "Sicurezza sul Lavoro": 4.6, "Standard & Qualità": 4.7, "Sviluppo Competenze": 4.0},
    "Chimico e Farmaceutico": {"Strategia & Controllo": 3.7, "Digitalizzazione": 3.9, "Gestione HR": 3.8, "Finanza & Investimenti": 3.6, "Sostenibilità (ESG)": 4.2, "Protezione Legale": 4.5, "Sicurezza sul Lavoro": 4.9, "Standard & Qualità": 4.8, "Sviluppo Competenze": 3.9},
    "Energia e Utilities (Gas, Luce, Acqua)": {"Strategia & Controllo": 3.9, "Digitalizzazione": 4.0, "Gestione HR": 3.8, "Finanza & Investimenti": 4.0, "Sostenibilità (ESG)": 4.5, "Protezione Legale": 4.0, "Sicurezza sul Lavoro": 4.6, "Standard & Qualità": 4.3, "Sviluppo Competenze": 3.7},
    "Costruzioni ed Edilizia": {"Strategia & Controllo": 2.8, "Digitalizzazione": 2.5, "Gestione HR": 2.9, "Finanza & Investimenti": 3.0, "Sostenibilità (ESG)": 2.7, "Protezione Legale": 3.4, "Sicurezza sul Lavoro": 4.7, "Standard & Qualità": 3.4, "Sviluppo Competenze": 2.8},
    "Elettronica ed Elettrotecnica": {"Strategia & Controllo": 3.5, "Digitalizzazione": 4.0, "Gestione HR": 3.5, "Finanza & Investimenti": 3.4, "Sostenibilità (ESG)": 3.2, "Protezione Legale": 3.6, "Sicurezza sul Lavoro": 4.0, "Standard & Qualità": 4.3, "Sviluppo Competenze": 3.9},
    "Gomma e Materie Plastiche": {"Strategia & Controllo": 3.1, "Digitalizzazione": 3.0, "Gestione HR": 3.1, "Finanza & Investimenti": 3.3, "Sostenibilità (ESG)": 3.0, "Protezione Legale": 3.2, "Sicurezza sul Lavoro": 4.4, "Standard & Qualità": 3.9, "Sviluppo Competenze": 3.0},
    "Carta e Stampa (Packaging ed Editoria)": {"Strategia & Controllo": 3.3, "Digitalizzazione": 3.4, "Gestione HR": 3.2, "Finanza & Investimenti": 3.2, "Sostenibilità (ESG)": 3.7, "Protezione Legale": 3.3, "Sicurezza sul Lavoro": 4.1, "Standard & Qualità": 4.0, "Sviluppo Competenze": 3.1},
    "ICT e Digitale (Software e Tecnologie)": {"Strategia & Controllo": 4.0, "Digitalizzazione": 4.8, "Gestione HR": 4.2, "Finanza & Investimenti": 3.6, "Sostenibilità (ESG)": 3.5, "Protezione Legale": 4.0, "Sicurezza sul Lavoro": 3.0, "Standard & Qualità": 3.8, "Sviluppo Competenze": 4.5},
    "Logistica e Trasporti": {"Strategia & Controllo": 3.4, "Digitalizzazione": 3.8, "Gestione HR": 3.3, "Finanza & Investimenti": 3.2, "Sostenibilità (ESG)": 3.2, "Protezione Legale": 3.5, "Sicurezza sul Lavoro": 4.3, "Standard & Qualità": 3.7, "Sviluppo Competenze": 3.2},
    "Turismo e Ristorazione (Horeca)": {"Strategia & Controllo": 2.9, "Digitalizzazione": 3.2, "Gestione HR": 3.5, "Finanza & Investimenti": 2.8, "Sostenibilità (ESG)": 3.3, "Protezione Legale": 3.1, "Sicurezza sul Lavoro": 3.8, "Standard & Qualità": 3.5, "Sviluppo Competenze": 3.4},
    "Bancario e Assicurativo": {"Strategia & Controllo": 4.5, "Digitalizzazione": 4.3, "Gestione HR": 4.0, "Finanza & Investimenti": 4.5, "Sostenibilità (ESG)": 4.2, "Protezione Legale": 4.8, "Sicurezza sul Lavoro": 3.5, "Standard & Qualità": 4.6, "Sviluppo Competenze": 4.2},
    "Sanità e Servizi Sociali": {"Strategia & Controllo": 3.8, "Digitalizzazione": 3.5, "Gestione HR": 4.0, "Finanza & Investimenti": 3.2, "Sostenibilità (ESG)": 3.7, "Protezione Legale": 4.2, "Sicurezza sul Lavoro": 4.6, "Standard & Qualità": 4.5, "Sviluppo Competenze": 3.9}
}

# --- INIZIALIZZAZIONE STATI ---
if 'page' not in st.session_state: st.session_state.page = "Anagrafica"
if 'clienti' not in st.session_state: st.session_state.clienti = {}
if 'current_client_piva' not in st.session_state: st.session_state.current_client_piva = None
if 'rev_index' not in st.session_state: st.session_state.rev_index = -1 

# --- DATABASE INTEGRALE 54 DOMANDE (Testi sintetizzati per brevità nello script) ---
DOMANDE_MATRICE = {
    'Strategia & Controllo': [
        ("Business Plan triennale?", {1: "No", 2: "Budget", 3: "12m", 4: "3y", 5: "Rev trim"}),
        ("Monitoraggio KPI?", {1: "No", 2: "Bilancio", 3: "Excel", 4: "Dashboard", 5: "BI"}),
        ("Ruoli definiti?", {1: "No", 2: "Verbali", 3: "Base", 4: "Mansionari", 5: "Manager"}),
        ("Analisi Competitor?", {1: "No", 2: "Raro", 3: "Annuale", 4: "Sempre", 5: "Data-driven"}),
        ("Delega operativa?", {1: "No", 2: "Minima", 3: "Prime deleghe", 4: "Autonomia", 5: "Manageriale"}),
        ("Passaggio generazionale?", {1: "No", 2: "Discusso", 3: "Idea", 4: "Bozza", 5: "Formalizzato"})
    ],
    'Digitalizzazione': [
        ("Sistema ERP?", {1: "No", 2: "Base", 3: "Settore", 4: "Integrato", 5: "Evoluto"}),
        ("Processi Paperless?", {1: "Carta", 2: "Misto", 3: "Digitale", 4: "Avanzato", 5: "Auto"}),
        ("CRM attivo?", {1: "No", 2: "Contatti", 3: "Offerte", 4: "Integrato", 5: "Automation"}),
        ("Cybersecurity?", {1: "No", 2: "Minima", 3: "Backup", 4: "Audit", 5: "Certificato"}),
        ("Marketing Digital?", {1: "No", 2: "Sito", 3: "Social", 4: "Ads", 5: "Lead Gen"}),
        ("Uso AI?", {1: "No", 2: "Studio", 3: "Test", 4: "Operativa", 5: "Driven"})
    ],
    'Gestione HR': [
        ("Piano Welfare?", {1: "No", 2: "Minimo", 3: "Base", 4: "Strutturato", 5: "Evoluto"}),
        ("Performance Mgt?", {1: "No", 2: "Informale", 3: "Annuo", 4: "MBO", 5: "Continuo"}),
        ("Talent Retention?", {1: "No", 2: "Passiva", 3: "Base", 4: "Branding", 5: "Leader"}),
        ("Clima aziendale?", {1: "No", 2: "Raro", 3: "Sì", 4: "Sistemico", 5: "Top"}),
        ("Upskilling?", {1: "No", 2: "Obbligo", 3: "Sporadico", 4: "Annuale", 5: "Academy"}),
        ("Smart Working?", {1: "No", 2: "Raro", 3: "Flessibile", 4: "Policy", 5: "Obiettivi"})
    ],
    'Finanza & Investimenti': [
        ("Cash Flow?", {1: "No", 2: "Breve", 3: "Mese", 4: "Trim", 5: "Real-time"}),
        ("Finanza Agevolata?", {1: "No", 2: "Raro", 3: "Base", 4: "Pianificato", 5: "Strategico"}),
        ("Rating Bancario?", {1: "No", 2: "Vago", 3: "Annuale", 4: "Costante", 5: "Ottimo"}),
        ("Marginalità?", {1: "No", 2: "Global", 3: "Stima", 4: "Analitica", 5: "Predittiva"}),
        ("Recupero Crediti?", {1: "No", 2: "Reattiva", 3: "Sì", 4: "Interno", 5: "Sistemico"}),
        ("Budget R&D?", {1: "0%", 2: "1%", 3: "2%", 4: "5%", 5: ">5%"})
    ],
    'Sostenibilità (ESG)': [
        ("Criteri ESG?", {1: "No", 2: "Pochi", 3: "Base", 4: "Integrazione", 5: "Bilancio"}),
        ("Impatto Ambientale?", {1: "No", 2: "Rifiuti", 3: "Energia", 4: "ISO14001", 5: "Zero"}),
        ("Parità Genere?", {1: "No", 2: "Sensibile", 3: "Sì", 4: "Policy", 5: "Certificato"}),
        ("Governance?", {1: "No", 2: "Minima", 3: "Etica", 4: "Piena", 5: "Trasparente"}),
        ("Supply Chain ESG?", {1: "No", 2: "Raro", 3: "Sì", 4: "Audit", 5: "Partner"}),
        ("Certificazioni?", {1: "No", 2: "1", 3: "Base", 4: "Multi", 5: "B-Corp"})
    ],
    'Protezione Legale': [
        ("Modello 231?", {1: "No", 2: "Bozza", 3: "Adottato", 4: "Aggiornato", 5: "ODV"}),
        ("GDPR Compliance?", {1: "No", 2: "Base", 3: "Sì", 4: "Audit", 5: "DPO"}),
        ("Contrattualistica?", {1: "Standard", 2: "Base", 3: "Revisionata", 4: "Ad hoc", 5: "Legal Mgt"}),
        ("IP/Brevetti?", {1: "No", 2: "Marchio", 3: "Sì", 4: "Attivo", 5: "Asset"}),
        ("Recupero Legale?", {1: "No", 2: "Raro", 3: "Sì", 4: "Interno", 5: "Efficienza"}),
        ("D&O Insurance?", {1: "No", 2: "RC", 3: "Base", 4: "D&O", 5: "Cyber/D&O"})
    ],
    'Sicurezza sul Lavoro': [
        ("DVR?", {1: "No", 2: "Vecchio", 3: "Aggiornato", 4: "Digitale", 5: "Proattivo"}),
        ("Formazione?", {1: "No", 2: "Base", 3: "Sì", 4: "Tracciata", 5: "Zero scadenze"}),
        ("Sorveglianza?", {1: "No", 2: "Base", 3: "Sì", 4: "Piena", 5: "Eclatante"}),
        ("DPI Tracciati?", {1: "No", 2: "Verbale", 3: "Cartaceo", 4: "Digitale", 5: "Auto"}),
        ("Manutenzioni?", {1: "No", 2: "Guasto", 3: "Base", 4: "Programmata", 5: "Predittiva"}),
        ("Near Miss?", {1: "No", 2: "Raro", 3: "Gravi", 4: "Sempre", 5: "Target Zero"})
    ],
    'Standard & Qualità': [
        ("ISO 9001?", {1: "No", 2: "Formale", 3: "Attiva", 4: "Sì", 5: "Eccellenza"}),
        ("Procedure mappate?", {1: "No", 2: "Minimo", 3: "Core", 4: "Tutte", 5: "Kaizen"}),
        ("Audit interni?", {1: "No", 2: "Raro", 3: "Annuo", 4: "Sempre", 5: "Culture"}),
        ("NPS Cliente?", {1: "No", 2: "Reclami", 3: "Sondaggio", 4: "NPS", 5: "Centric"}),
        ("Qualifica Fornitori?", {1: "No", 2: "Base", 3: "Sì", 4: "Rating", 5: "Partner"}),
        ("Gestione NC?", {1: "No", 2: "Base", 3: "Sì", 4: "Cause", 5: "Root Solve"})
    ],
    'Sviluppo Competenze': [
        ("Gap Analysis?", {1: "No", 2: "Vaga", 3: "Sì", 4: "Analitica", 5: "Strategica"}),
        ("Fondi Formazione?", {1: "No", 2: "Raro", 3: "Sì", 4: "Sempre", 5: "Massimo"}),
        ("Academy Interna?", {1: "No", 2: "Tutor", 3: "Sì", 4: "Manuali", 5: "Academy"}),
        ("Leadership Training?", {1: "No", 2: "Minimo", 3: "Soft", 4: "Coaching", 5: "Diffusa"}),
        ("Piani Carriera?", {1: "No", 2: "Vaghi", 3: "Sì", 4: "Certi", 5: "Merito"}),
        ("Mindset Digital?", {1: "No", 2: "Resistenza", 3: "Aperti", 4: "Pronti", 5: "Innovatori"})
    ]
}

def go_to(page): st.session_state.page = page

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://www.nextahub.it/wp-content/uploads/2023/05/logo-nextahub.png", width=200)
    st.markdown("---")
    if st.button("🏠 1. Anagrafica", use_container_width=True): go_to("Anagrafica")
    if st.button("📝 2. Nuovo Assessment", use_container_width=True): go_to("Questionario")
    if st.button("📊 3. Radar & Analisi AI", use_container_width=True): go_to("Valutazione")
    if st.button("💼 4. Servizi & Urgenze", use_container_width=True): go_to("Servizi")
    if st.button("📁 5. Archivio Revisioni", use_container_width=True): go_to("Lista")

# --- PAGINA 1: ANAGRAFICA ---
if st.session_state.page == "Anagrafica":
    st.header("🏢 Anagrafica Cliente")
    with st.form("anag_form"):
        col1, col2 = st.columns(2)
        with col1:
            azienda = st.text_input("Ragione Sociale")
            piva = st.text_input("Partita IVA")
            indirizzo = st.text_input("Indirizzo Aziendale")
        with col2:
            settore = st.selectbox("Settore", list(BENCHMARK_DATI.keys()))
            regione = st.selectbox("Regione", ["Lombardia", "Veneto", "Emilia-Romagna", "Piemonte", "Lazio", "Campania", "Altro"])
        
        if st.form_submit_button("Salva Cliente"):
            if azienda and piva:
                st.session_state.current_client_piva = piva
                if piva not in st.session_state.clienti:
                    st.session_state.clienti[piva] = {"anagrafica": {"azienda": azienda, "piva": piva, "indirizzo": indirizzo, "settore": settore, "regione": regione}, "revisioni": []}
                else:
                    st.session_state.clienti[piva]["anagrafica"].update({"azienda": azienda, "indirizzo": indirizzo, "settore": settore, "regione": regione})
                st.success("Anagrafica salvata!")
                go_to("Questionario")
                st.rerun()

# --- PAGINA 2: QUESTIONARIO ---
elif st.session_state.page == "Questionario":
    piva = st.session_state.current_client_piva
    if not piva: st.warning("Seleziona un cliente in Anagrafica.")
    else:
        st.header(f"📝 Assessment: {st.session_state.clienti[piva]['anagrafica']['azienda']}")
        scores = {}
        tabs = st.tabs(list(DOMANDE_MATRICE.keys()))
        for i, area in enumerate(DOMANDE_MATRICE.keys()):
            with tabs[i]:
                p_area = []
                for j, (q, opts) in enumerate(DOMANDE_MATRICE[area]):
                    val = st.radio(q, options=[1,2,3,4,5], format_func=lambda x: f"{x}: {opts[x]}", key=f"q_{piva}_{area}_{j}_{len(st.session_state.clienti[piva]['revisioni'])}")
                    p_area.append(val)
                scores[area] = sum(p_area)/len(p_area)
        
        if st.button("Salva Revisione"):
            st.session_state.clienti[piva]['revisioni'].append({"data": datetime.now().strftime("%d/%m/%Y %H:%M"), "punteggi": scores, "analisi_ai": ""})
            st.session_state.rev_index = len(st.session_state.clienti[piva]['revisioni']) - 1
            go_to("Valutazione")
            st.rerun()

# --- PAGINA 3: RADAR & AI (CON FUNZIONE DI STAMPA) ---
elif st.session_state.page == "Valutazione":
    piva = st.session_state.current_client_piva
    if not piva or not st.session_state.clienti[piva]['revisioni']: st.warning("Dati mancanti.")
    else:
        cliente = st.session_state.clienti[piva]
        rev = cliente['revisioni'][st.session_state.rev_index]
        
        # Intestazione professionale
        col_logo, col_info = st.columns([1, 2])
        with col_logo: st.image("https://www.nextahub.it/wp-content/uploads/2023/05/logo-nextahub.png", width=250)
        with col_info: st.markdown(f"### REPORT STRATEGICO NEXTAHUB\n**Azienda:** {cliente['anagrafica']['azienda']} | **P.IVA:** {piva}\n**Indirizzo:** {cliente['anagrafica']['indirizzo']}\n**Settore:** {cliente['anagrafica']['settore']} | **Data:** {rev['data']}")

        if st.button("🖨️ Stampa Report / Salva PDF"):
            st.markdown('<script>window.print();</script>', unsafe_allow_html=True)
        
        st.markdown("---")

        # Radar
        settore = cliente['anagrafica']['settore']
        categorie = list(rev['punteggi'].keys())
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=list(rev['punteggi'].values()), theta=categorie, fill='toself', name='Cliente', line_color='#e63946'))
        fig.add_trace(go.Scatterpolar(r=[BENCHMARK_DATI[settore].get(c, 3.0) for c in categorie], theta=categorie, name='Benchmark Settore', line_color='gray', line_dash='dash'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), height=600)
        st.plotly_chart(fig, use_container_width=True)

        if not rev['analisi_ai']:
            if st.button("🤖 Genera Analisi AI"):
                try:
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    model_id = next((m for m in models if "flash" in m), models[0])
                    model = genai.GenerativeModel(model_id)
                    prompt = f"Consulente NextaHub. Azienda: {cliente['anagrafica']['azienda']}. Settore {settore}. Punteggi: {rev['punteggi']}. Benchmark: {BENCHMARK_DATI[settore]}. Gap analysis e 3 mosse strategiche."
                    with st.spinner("Analisi in corso..."):
                        res = model.generate_content(prompt)
                        rev['analisi_ai'] = res.text
                        st.rerun()
                except Exception as e: st.error(f"AI Error: {e}")
        else:
            st.markdown("### 🤖 ANALISI STRATEGICA AI")
            st.markdown(rev['analisi_ai'])

# --- PAGINE 4 E 5 ---
elif st.session_state.page == "Servizi":
    piva = st.session_state.current_client_piva
    if piva and st.session_state.clienti[piva]['revisioni']:
        rev = st.session_state.clienti[piva]['revisioni'][st.session_state.rev_index]
        settore = st.session_state.clienti[piva]['anagrafica']['settore']
        st.header("💼 Piano d'Urgenza")
        c1, c2, c3 = st.columns(3)
        for area, s in rev['punteggi'].items():
            b = BENCHMARK_DATI[settore].get(area, 3.0)
            if s < 2.5: c1.error(f"🚨 **{area}**")
            elif s < b: c2.warning(f"⚠️ **{area}**")
            else: c3.success(f"✅ **{area}**")

elif st.session_state.page == "Lista":
    st.header("📁 Archivio Revisioni")
    for p, d in st.session_state.clienti.items():
        with st.expander(f"🏢 {d['anagrafica']['azienda']} ({p})"):
            st.write(f"📍 {d['anagrafica']['indirizzo']} | {d['anagrafica']['settore']}")
            for idx, r in enumerate(d['revisioni']):
                if st.button(f"Carica {r['data']}", key=f"v_{p}_{idx}"):
                    st.session_state.current_client_piva = p
                    st.session_state.rev_index = idx
                    go_to("Valutazione")
                    st.rerun()
