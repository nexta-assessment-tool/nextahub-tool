import streamlit as st
import plotly.graph_objects as go
import google.generativeai as genai
from datetime import datetime
import json

# --- 1. CONFIGURAZIONE PAGINA E API ---
st.set_page_config(page_title="NextaHub Strategic Suite v3.0", layout="wide")

def setup_gemini():
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("⚠️ Configura 'GEMINI_API_KEY' nei Secrets di Streamlit.")
        st.stop()
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    try:
        # Rilevamento automatico modelli (Flash prioritario per velocità, Pro per analisi)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        return models
    except Exception as e:
        st.error(f"Errore API: {e}")
        return []

modelli_disponibili = setup_gemini()
LOGO_URL = "https://nextahub.it/wp-content/uploads/2026/02/Nexta_Logo_Def_PiccoloHUB.png"

# --- 2. COSTANTI E SETTORI ---
SETTORI = [
    "Agroalimentare", "Moda e Tessile", "Arredo e Design", "Meccanica e Automazione",
    "Metallurgia", "Automotive", "Chimico e Farmaceutico", "Energia e Utilities",
    "Costruzioni ed Edilizia", "Elettronica", "Gomma e Materie Plastiche",
    "Carta e Stampa", "ICT e Digitale", "Logistica e Trasporti",
    "Turismo e Ristorazione", "Bancario e Assicurativo", "Sanità"
]

REGIONI = [
    "Abruzzo", "Basilicata", "Calabria", "Campania", "Emilia-Romagna", "Friuli-Venezia Giulia",
    "Lazio", "Liguria", "Lombardia", "Marche", "Molise", "Piemonte", "Puglia",
    "Sardegna", "Sicilia", "Toscana", "Trentino-Alto Adige", "Umbria", "Valle d'Aosta", "Veneto"
]

# --- 3. MATRICE DOMANDE (Con Logica di Filtro Settoriale) ---
# Struttura: (Domanda, Opzioni, Solo_Per_Settori_Specifici o None)
DOMANDE_MATRICE = {
    'Strategia & Controllo': [
        ("Piano Strategico", ["Nessun piano", "Verbali", "Budget annuale", "Piano triennale", "Piano dinamico"], None),
        ("Passaggio Generazionale", ["Tabù", "Informale", "Successori scelti", "Affiancamento", "Patti famiglia"], None),
        ("Organigramma", ["Titolare", "Confuso", "Schema base", "Deleghe", "Manager autonomi"], None)
    ],
    'Digitalizzazione': [
        ("Infrastruttura IT", ["Obsolescente", "Base", "Server locale", "Cloud ibrido", "Full Cloud"], None),
        ("Innovazione AI", ["No", "Sporadico", "Test area", "Integrata", "AI-driven"], ["ICT e Digitale", "Elettronica", "Meccanica"]),
        ("Cybersecurity", ["Base", "Backup saltuari", "Firewall", "Audit", "SOC 24/7"], None)
    ],
    'Gestione HR': [
        ("Welfare", ["No", "Rimborsi", "Convenzioni", "Piattaforma", "Benefit evoluti"], None),
        ("Academy Interna", ["No", "Occasionale", "Piani crescita", "Academy strutturata", "Learning Org"], ["Meccanica", "ICT e Digitale", "Bancario"])
    ],
    'Finanza & Investimenti': [
        ("Cash Flow", ["No", "Saldo banca", "Mensile", "Previsionale 6m", "Tesoreria AI"], None),
        ("Rating Bancario", ["No", "Vago", "Annuo", "Trimestrale", "Ottimizzazione"], None)
    ],
    'Sostenibilità (ESG)': [
        ("Bilancio Sostenibilità", ["No", "Obblighi legge", "Iniziativa volontaria", "Certificato", "Rating ESG"], None)
    ],
    'Protezione Legale': [
        ("Modello 231", ["No", "In corso", "Adottato", "Aggiornato", "ODV attivo"], ["Costruzioni ed Edilizia", "Sanità", "Energia e Utilities"])
    ],
    'Sicurezza sul Lavoro': [
        ("Cultura Sicurezza", ["Solo obblighi", "Registro infortuni", "Prevenzione attuata", "Comportamentale", "Zero Infortuni"], None)
    ],
    'Standard & Qualità': [
        ("Certificazioni ISO", ["No", "In corso", "Formale", "Strumento operativo", "Motore di crescita"], None),
        ("Marcatura CE", ["No", "Documentale", "Certificata", "Controllo filiera", "Audit esterni"], ["Meccanica", "Elettronica", "Costruzioni ed Edilizia"])
    ],
    'Sviluppo Competenze': [
        ("Fondi Interprofessionali", ["Mai usati", "Rari", "Saltuari", "Sempre", "Ottimizzazione massima"], None)
    ]
}

# --- 4. ENGINE AI (BENCHMARK + REPORT) ---
def analizza_con_gemini(dati_cliente, punteggi):
    # Selezione modello
    m_name = "models/gemini-1.5-pro" if "models/gemini-1.5-pro" in modelli_disponibili else "models/gemini-1.5-flash"
    model = genai.GenerativeModel(m_name)
    
    # Prompt per definire il Benchmark Dinamico e il Report
    prompt = f"""
    Sei il Senior Partner di NextaHub. 
    CLIENTE: {dati_cliente['azienda']}
    SETTORE: {dati_cliente['settore']}
    REGIONE: {dati_cliente['regione']}
    COMMERCIALE RIF: {dati_cliente['commerciale']}

    DATI ASSESSMENT (Punteggi da 1 a 5):
    {json.dumps(punteggi, indent=2)}

    COMPITI:
    1. DETERMINA BENCHMARK: In base al settore "{dati_cliente['settore']}" e alla regione "{dati_cliente['regione']}", stabilisci un valore di benchmark (da 1.0 a 5.0) per ognuna delle 9 aree. Sii realistico: un'azienda in Lombardia avrà benchmark digitali più alti di una in regioni meno industrializzate.
    2. ANALISI GAP: Identifica le criticità dove il punteggio è inferiore al benchmark.
    3. CONSIGLI COMMERCIALI: Per ogni gap, suggerisci un servizio specifico NextaHub.
    4. ROADMAP: Crea un piano d'azione in 3 fasi.

    FORMATO OUTPUT (IMPORTANTE):
    Genera il report con una struttura perfetta per Microsoft Word. 
    Usa Titoli (##), Grassetto, Tabelle e elenchi puntati. 
    Includi una tabella iniziale con i dati anagrafici e una tabella comparativa Punteggio vs Benchmark.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Errore generazione: {e}"

# --- 5. LOGICA INTERFACCIA ---
if 'page' not in st.session_state: st.session_state.page = "Anagrafica"
if 'clienti' not in st.session_state: st.session_state.clienti = {}
if 'current_piva' not in st.session_state: st.session_state.current_piva = None

# Sidebar
with st.sidebar:
    st.image(LOGO_URL, width=180)
    st.markdown("---")
    if st.button("🏢 1. Anagrafica"): st.session_state.page = "Anagrafica"
    if st.button("📝 2. Assessment"): st.session_state.page = "Questionario"
    if st.button("📊 3. Report"): st.session_state.page = "Valutazione"

# PAGINA 1: ANAGRAFICA
if st.session_state.page == "Anagrafica":
    st.title("🏢 Anagrafica Cliente & Setup Analisi")
    with st.form("form_anag"):
        c1, c2 = st.columns(2)
        with c1:
            rs = st.text_input("Ragione Sociale *")
            pi = st.text_input("Partita IVA *")
            settore = st.selectbox("Settore Business *", SETTORI)
            comm = st.text_input("Riferimento Commerciale Nexta")
        with c2:
            regione = st.selectbox("Regione *", REGIONI)
            comune = st.text_input("Comune *")
            via = st.text_input("Via")
            civico = st.text_input("Civico")
            cap = st.text_input("CAP")
            prov = st.text_input("Provincia")
            rif_az = st.text_input("Riferimento Aziendale (Nome/Cognome)")

        submit = st.form_submit_button("➡️ Prosegui all'Assessment")
        if submit:
            if not rs or not pi or not comune or not settore:
                st.error("I campi contrassegnati con * sono obbligatori.")
            else:
                st.session_state.clienti[pi] = {
                    "info": {
                        "azienda": rs, "piva": pi, "settore": settore, "regione": regione,
                        "comune": comune, "via": via, "civico": civico, "cap": cap,
                        "provincia": prov, "rif_aziendale": rif_az, "commerciale": comm
                    },
                    "assessments": []
                }
                st.session_state.current_piva = pi
                st.session_state.page = "Questionario"
                st.rerun()

# PAGINA 2: QUESTIONARIO
elif st.session_state.page == "Questionario":
    pi = st.session_state.current_piva
    if not pi: st.warning("Dati mancanti"); st.stop()
    
    info = st.session_state.clienti[pi]['info']
    st.title(f"📝 Assessment per {info['azienda']}")
    st.info(f"Settore: {info['settore']} | Regione: {info['regione']}")

    tabs = st.tabs(list(DOMANDE_MATRICE.keys()))
    temp_scores = {}

    for i, area in enumerate(DOMANDE_MATRICE.keys()):
        with tabs[i]:
            st.subheader(f"Analisi {area}")
            area_scores = []
            # Filtro domande per settore
            for j, (domanda, opzioni, limitazione) in enumerate(DOMANDE_MATRICE[area]):
                if limitazione is None or info['settore'] in limitazione:
                    val = st.radio(f"**{domanda}**", [1,2,3,4,5], 
                                  format_func=lambda x: f"{x}: {opzioni[x-1]}",
                                  key=f"q_{pi}_{area}_{j}")
                    area_scores.append(val)
            temp_scores[area] = sum(area_scores) / len(area_scores) if area_scores else 3.0

    if st.button("📊 Genera Analisi Strategica", use_container_width=True):
        st.session_state.clienti[pi]['assessments'].append({
            "data": datetime.now().strftime("%d/%m/%Y"),
            "punteggi": temp_scores
        })
        st.session_state.page = "Valutazione"
        st.rerun()

# PAGINA 3: VALUTAZIONE E AI
elif st.session_state.page == "Valutazione":
    pi = st.session_state.current_piva
    if not pi or not st.session_state.clienti[pi]['assessments']: st.warning("Esegui prima l'assessment"); st.stop()
    
    cl = st.session_state.clienti[pi]
    ass = cl['assessments'][-1]
    
    st.title(f"📊 Report Strategico: {cl['info']['azienda']}")
    
    if st.button("🚀 Avvia Intelligenza Artificiale (Generazione Report Word-Ready)"):
        with st.spinner("L'AI sta analizzando il settore e la regione per definire i benchmark..."):
            report = analizza_con_gemini(cl['info'], ass['punteggi'])
            st.session_state.last_report = report
            st.rerun()

    if 'last_report' in st.session_state:
        st.markdown("---")
        st.markdown(st.session_state.last_report)
        st.download_button("📥 Scarica Report per Word", st.session_state.last_report, 
                          file_name=f"Report_Nexta_{cl['info']['azienda']}.md")
