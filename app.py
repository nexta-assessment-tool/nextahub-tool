import streamlit as st
import plotly.graph_objects as go
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="NextaHub Strategic Suite", layout="wide", initial_sidebar_state="expanded")

# --- CSS PER LA STAMPA (Nasconde gli elementi web quando salvi in PDF) ---
st.markdown("""
    <style>
    @media print {
        [data-testid="stSidebar"], 
        header, 
        footer, 
        .stButton, 
        [data-testid="stToolbar"],
        .stTabs [data-baseweb="tab-list"] {
            display: none !important;
        }
        .main .block-container {
            padding: 1rem !important;
            margin: 0 !important;
            max-width: 100% !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE BENCHMARK (Tutti i 17 settori) ---
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

# --- DOMANDE (MATRICE INTEGRALE) ---
DOMANDE_MATRICE = {
    'Strategia & Controllo': [
        ("Esiste un Business Plan triennale formalizzato?", {1: "No", 2: "Solo budget annuale", 3: "Sì, ma orizzonte 12 mesi", 4: "Sì, triennale completo", 5: "Sì, con revisione trimestrale"}),
        ("Monitoraggio KPI aziendali?", {1: "Assente", 2: "Solo bilancio annuale", 3: "Excel saltuario", 4: "Dashboard mensile", 5: "BI in tempo reale"}),
        ("Ruoli e organigramma definiti?", {1: "Tutto fa capo al titolare", 2: "Verbalizzati ma confusi", 3: "Organigramma base", 4: "Mansionari completi", 5: "Manager responsabili di BU"}),
        ("Analisi della concorrenza e posizionamento?", {1: "Mai fatta", 2: "Raramente", 3: "Annuale", 4: "Sempre monitorati", 5: "Data-driven costante"}),
        ("Delega operativa effettiva?", {1: "Nessuna", 2: "Minima", 3: "Prime deleghe a capi area", 4: "Autonomia decisionale", 5: "Delega piena ai manager"}),
        ("Pianificazione passaggio generazionale?", {1: "Nessuna", 2: "Solo discussioni", 3: "Idea di base", 4: "Bozza di piano", 5: "Formalizzato e attivo"})
    ],
    'Digitalizzazione': [
        ("Presenza di un ERP/Gestionale?", {1: "No", 2: "Base (solo fatture)", 3: "Settoriale", 4: "Integrato con magazzino", 5: "Cloud ed evoluto"}),
        ("Processi Paperless?", {1: "Tutto cartaceo", 2: "Misto", 3: "Prevalenza digitale", 4: "Avanzato", 5: "Automazione completa"}),
        ("CRM per gestione clienti?", {1: "Assente", 2: "Lista contatti", 3: "Gestione offerte", 4: "Integrato marketing", 5: "Marketing Automation"}),
        ("Cybersecurity e protezione dati?", {1: "Solo antivirus", 2: "Backup saltuario", 3: "Backup cloud e policy", 4: "Audit periodici", 5: "Certificato/Zero Trust"}),
        ("Presenza Digital Marketing?", {1: "Assente", 2: "Solo sito vetrina", 3: "Social attivi", 4: "Campagne ADS", 5: "Lead Generation evoluta"}),
        ("Utilizzo AI nei processi?", {1: "Nullo", 2: "Sperimentale individuale", 3: "Test in alcuni uffici", 4: "Operativa in un'area", 5: "AI-Driven company"})
    ],
    'Gestione HR': [
        ("Piano di Welfare aziendale?", {1: "Assente", 2: "Solo rimborsi minimi", 3: "Base", 4: "Strutturato", 5: "Evoluto/Personalizzato"}),
        ("Performance Management?", {1: "Nessuna", 2: "Informale", 3: "Annuale base", 4: "MBO legati a KPI", 5: "Feedback continuo"}),
        ("Politiche di Talent Retention?", {1: "Assenti", 2: "Solo bonus saltuari", 3: "Base", 4: "Employer Branding", 5: "Leader di mercato"}),
        ("Monitoraggio clima aziendale?", {1: "Mai", 2: "Solo in crisi", 3: "Saltuario", 4: "Indagine annuale", 5: "Monitoraggio costante"}),
        ("Investimento in Upskilling?", {1: "Solo obbligatoria", 2: "Minimo", 3: "Sporadico", 4: "Piano formativo annuo", 5: "Academy interna"}),
        ("Smart Working e flessibilità?", {1: "No", 2: "Casi eccezionali", 3: "Flessibilità oraria", 4: "Policy strutturata", 5: "Work from anywhere"})
    ],
    'Finanza & Investimenti': [
        ("Controllo Cash Flow?", {1: "Assente", 2: "Solo a breve termine", 3: "Mensile", 4: "Trimestrale previsionale", 5: "Dashboard real-time"}),
        ("Accesso a Finanza Agevolata?", {1: "Mai", 2: "Raramente", 3: "Base", 4: "Pianificato", 5: "Strategico costante"}),
        ("Monitoraggio Rating Bancario?", {1: "No", 2: "Vago", 3: "Annuale", 4: "Costante", 5: "Ottimizzazione attiva"}),
        ("Analisi marginalità per prodotto?", {1: "Solo globale", 2: "Stime", 3: "Sì su core business", 4: "Analitica completa", 5: "Predittiva"}),
        ("Gestione recupero crediti?", {1: "Reattiva", 2: "Base", 3: "Procedure scritte", 4: "Ufficio interno", 5: "Sistemica e veloce"}),
        ("Budget R&D / Fatturato?", {1: "0%", 2: "1%", 3: "2-3%", 4: "5%", 5: ">5%"})
    ],
    'Sostenibilità (ESG)': [
        ("Integrazione criteri ESG?", {1: "Nessuna", 2: "Iniziale", 3: "Base", 4: "Integrazione strategia", 5: "Bilancio Sostenibilità"}),
        ("Monitoraggio impatto ambientale?", {1: "No", 2: "Solo rifiuti", 3: "Energia/Acqua", 4: "Carbon Footprint", 5: "Net Zero Plan"}),
        ("Politiche parità di genere?", {1: "Assenti", 2: "Sensibilità", 3: "Sì", 4: "Policy attive", 5: "Certificazione parità"}),
        ("Governance etica?", {1: "No", 2: "Minima", 3: "Codice etico", 4: "Piena trasparenza", 5: "Rating legalità +++"}),
        ("Valutazione fornitori (ESG)?", {1: "Solo prezzo", 2: "Rara", 3: "Questionari base", 4: "Audit ESG", 5: "Partnership sostenibili"}),
        ("Certificazioni Green?", {1: "Nessuna", 2: "1 base", 3: "Standard settore", 4: "Multiple", 5: "B-Corp / Benefit"})
    ],
    'Protezione Legale': [
        ("Modello 231?", {1: "No", 2: "In fase di studio", 3: "Adottato", 4: "Aggiornato e diffuso", 5: "ODV esterno attivo"}),
        ("Conformità GDPR?", {1: "Minima", 2: "Base", 3: "Sì", 4: "Audit periodici", 5: "DPO nominato"}),
        ("Gestione Contrattualistica?", {1: "Modelli web", 2: "Standard vecchi", 3: "Revisionata", 4: "Ad hoc per cliente", 5: "Legal Management System"}),
        ("Tutela IP e Marchi?", {1: "No", 2: "Marchio registrato", 3: "Monitoraggio base", 4: "Strategia IP attiva", 5: "Asset brevettuale"}),
        ("Gestione contenzioso?", {1: "Solo emergenza", 2: "Reattiva", 3: "Sì", 4: "Interno/Esterno fisso", 5: "Analisi preventiva"}),
        ("Coperture D&O Insurance?", {1: "No", 2: "Solo RC base", 3: "Valutazione", 4: "Sì, D&O attiva", 5: "Polizze Cyber+D&O"})
    ],
    'Sicurezza sul Lavoro': [
        ("Stato del DVR?", {1: "Assente/Scaduto", 2: "Obsoleto", 3: "Aggiornato", 4: "Digitale dinamico", 5: "Modello eccellenza"}),
        ("Formazione sicurezza?", {1: "Scaduta", 2: "Solo base", 3: "In regola", 4: "Tracciata digitalmente", 5: "Cultura sicurezza diffusa"}),
        ("Sorveglianza Sanitaria?", {1: "Assente", 2: "Minima", 3: "Sì, costante", 4: "Piena conformità", 5: "Programmi benessere"}),
        ("Gestione DPI?", {1: "Informale", 2: "Consegna semplice", 3: "Registri cartacei", 4: "Tracciati digitalmente", 5: "Automatici"}),
        ("Manutenzioni macchinari?", {1: "A guasto", 2: "Base", 3: "Programmata", 4: "Software dedicato", 5: "Predittiva"}),
        ("Segnalazione Near Miss?", {1: "Mai", 2: "Raramente", 3: "Solo gravi", 4: "Procedura attiva", 5: "Target Zero infortuni"})
    ],
    'Standard & Qualità': [
        ("Certificazione ISO 9001?", {1: "No", 2: "Solo formale", 3: "Attiva", 4: "Sì", 5: "Sistema eccellenza"}),
        ("Mappatura processi?", {1: "No", 2: "Minima", 3: "Core business", 4: "Tutti i processi", 5: "Miglioramento continuo"}),
        ("Audit interni periodici?", {1: "No", 2: "Rari", 3: "Annui", 4: "Sempre eseguiti", 5: "Cultura della qualità"}),
        ("Soddisfazione cliente (NPS)?", {1: "No", 2: "Solo reclami", 3: "Sondaggio annuo", 4: "NPS strutturato", 5: "Customer Centricity"}),
        ("Qualifica fornitori?", {1: "Nessuna", 2: "Base", 3: "Albo fornitori", 4: "Rating fornitori", 5: "Partnership di qualità"}),
        ("Gestione Non Conformità?", {1: "Reattiva", 2: "Base", 3: "Registrata", 4: "Analisi cause", 5: "Risoluzione preventiva"})
    ],
    'Sviluppo Competenze': [
        ("Analisi dei Gap formativi?", {1: "No", 2: "Vaga", 3: "Sì", 4: "Analitica", 5: "Strategica"}),
        ("Utilizzo fondi interprofessionali?", {1: "Mai", 2: "Raro", 3: "Sì", 4: "Sempre", 5: "Ottimizzazione massima"}),
        ("Academy o formazione interna?", {1: "No", 2: "Tutoraggio base", 3: "Sì", 4: "Manuali tecnici", 5: "Academy aziendale"}),
        ("Training Leadership?", {1: "Assente", 2: "Minimo", 3: "Solo figure chiave", 4: "Percorsi coaching", 5: "Leadership diffusa"}),
        ("Piani di carriera definiti?", {1: "No", 2: "Informali", 3: "Sì", 4: "Certi e trasparenti", 5: "Basati sul merito"}),
        ("Digital Mindset?", {1: "Resistenza", 2: "Basso", 3: "In crescita", 4: "Pronto al cambiamento", 5: "Innovatori nati"})
    ]
}

# --- INIZIALIZZAZIONE STATI ---
if 'page' not in st.session_state: st.session_state.page = "Anagrafica"
if 'clienti' not in st.session_state: st.session_state.clienti = {}
if 'current_client_piva' not in st.session_state: st.session_state.current_client_piva = None
if 'rev_index' not in st.session_state: st.session_state.rev_index = -1

LOGO_URL = "https://www.nextahub.it/wp-content/uploads/2023/05/logo-nextahub.png"

# --- LOGICA NAVIGAZIONE ---
def go_to(page):
    st.session_state.page = page
    st.rerun()

# --- SIDEBAR ---
with st.sidebar:
    st.image(LOGO_URL, width=180)
    st.markdown("---")
    if st.button("🏠 1. Anagrafica", use_container_width=True): go_to("Anagrafica")
    if st.button("📝 2. Nuovo Assessment", use_container_width=True): go_to("Questionario")
    if st.button("📊 3. Radar & Analisi AI", use_container_width=True): go_to("Valutazione")
    if st.button("📁 4. Archivio", use_container_width=True): go_to("Lista")

# --- PAGINA 1: ANAGRAFICA ---
if st.session_state.page == "Anagrafica":
    st.header("🏢 Anagrafica Cliente")
    with st.form("anag_form"):
        col1, col2 = st.columns(2)
        with col1:
            azienda = st.text_input("Ragione Sociale")
            piva = st.text_input("Partita IVA")
            indirizzo = st.text_input("Indirizzo Sede Operativa")
        with col2:
            settore = st.selectbox("Settore Benchmark", list(BENCHMARK_DATI.keys()))
            regione = st.selectbox("Regione", ["Lombardia", "Veneto", "Emilia-Romagna", "Piemonte", "Lazio", "Toscana", "Campania", "Puglia", "Sicilia", "Altro"])
        
        if st.form_submit_button("Salva e Prosegui"):
            if azienda and piva:
                st.session_state.current_client_piva = piva
                if piva not in st.session_state.clienti:
                    st.session_state.clienti[piva] = {
                        "anagrafica": {"azienda": azienda, "piva": piva, "indirizzo": indirizzo, "settore": settore, "regione": regione},
                        "revisioni": []
                    }
                else:
                    st.session_state.clienti[piva]["anagrafica"].update({"azienda": azienda, "indirizzo": indirizzo, "settore": settore})
                go_to("Questionario")
            else:
                st.error("Inserire Ragione Sociale e P.Iva")

# --- PAGINA 2: QUESTIONARIO (54 DOMANDE) ---
elif st.session_state.page == "Questionario":
    piva = st.session_state.current_client_piva
    if not piva:
        st.warning("Seleziona un cliente in Anagrafica.")
    else:
        st.header(f"📝 Assessment: {st.session_state.clienti[piva]['anagrafica']['azienda']}")
        st.info("Rispondi a tutte le domande per generare il grafico radar.")
        
        scores = {}
        tabs = st.tabs(list(DOMANDE_MATRICE.keys()))
        
        for i, area in enumerate(DOMANDE_MATRICE.keys()):
            with tabs[i]:
                st.subheader(f"Area {area}")
                p_area = []
                for j, (q, opts) in enumerate(DOMANDE_MATRICE[area]):
                    val = st.select_slider(
                        q,
                        options=[1, 2, 3, 4, 5],
                        format_func=lambda x: f"{x} - {opts[x]}",
                        key=f"q_{piva}_{area}_{j}"
                    )
                    p_area.append(val)
                scores[area] = sum(p_area) / len(p_area)
        
        if st.button("Finalizza e Genera Report", use_container_width=True):
            st.session_state.clienti[piva]['revisioni'].append({
                "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "punteggi": scores,
                "analisi_ai": ""
            })
            st.session_state.rev_index = len(st.session_state.clienti[piva]['revisioni']) - 1
            go_to("Valutazione")

# --- PAGINA 3: VALUTAZIONE & RADAR ---
elif st.session_state.page == "Valutazione":
    piva = st.session_state.current_client_piva
    if not piva or not st.session_state.clienti[piva]['revisioni']:
        st.warning("Dati non disponibili.")
    else:
        cliente = st.session_state.clienti[piva]
        rev = cliente['revisioni'][st.session_state.rev_index]
        
        # --- HEADER PER STAMPA ---
        col_logo, col_info = st.columns([1, 2])
        with col_logo:
            st.image(LOGO_URL, width=220)
        with col_info:
            st.markdown(f"""
            ### REPORT STRATEGICO NEXTAHUB
            **Azienda:** {cliente['anagrafica']['azienda']}  
            **Sede:** {cliente['anagrafica']['indirizzo']}  
            **Settore:** {cliente['anagrafica']['settore']} | **Data:** {rev['data']}
            """)
        
        st.markdown("---")

        # --- RADAR CHART ---
        settore = cliente['anagrafica']['settore']
        categorie = list(rev['punteggi'].keys())
        
        fig = go.Figure()
        # Dati Cliente
        fig.add_trace(go.Scatterpolar(
            r=list(rev['punteggi'].values()),
            theta=categorie,
            fill='toself',
            name='Situazione Aziendale',
            line_color='#e63946'
        ))
        # Benchmark
        fig.add_trace(go.Scatterpolar(
            r=[BENCHMARK_DATI[settore].get(c, 3.0) for c in categorie],
            theta=categorie,
            name=f'Benchmark {settore}',
            line_color='gray',
            line_dash='dash'
        ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            height=600,
            legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- ANALISI AI ---
        if not rev['analisi_ai']:
            if st.button("🤖 Genera Analisi con Intelligenza Artificiale"):
                try:
                    # Se hai una API Key configurata in .streamlit/secrets.toml
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"""
                    Agisci come Senior Consultant NextaHub. Analizza i punteggi di questa azienda: {rev['punteggi']}.
                    Settore: {settore}. Confrontali con il benchmark: {BENCHMARK_DATI[settore]}.
                    Fornisci: 1. Analisi dei Gap principali. 2. Tre azioni prioritarie da compiere subito.
                    Mantieni un tono professionale, incisivo e orientato al business.
                    """
                    with st.spinner("Analisi in corso..."):
                        response = model.generate_content(prompt)
                        rev['analisi_ai'] = response.text
                        st.rerun()
                except:
                    st.info("Funzionalità AI: Inserire la chiave API per attivare l'analisi automatica.")
        else:
            st.markdown("### 🤖 Analisi Strategica AI")
            st.markdown(rev['analisi_ai'])

# --- PAGINA 4: ARCHIVIO ---
elif st.session_state.page == "Lista":
    st.header("📁 Archivio Storico")
    if not st.session_state.clienti:
        st.write("Nessun cliente in archivio.")
    for p, dati in st.session_state.clienti.items():
        with st.expander(f"🏢 {dati['anagrafica']['azienda']} ({p})"):
            for idx, r in enumerate(dati['revisioni']):
                if st.button(f"Carica Report del {r['data']}", key=f"hist_{p}_{idx}"):
                    st.session_state.current_client_piva = p
                    st.session_state.rev_index = idx
                    go_to("Valutazione")
