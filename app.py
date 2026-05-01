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
    return ["gemini-1.5-flash", "gemini-1.5-pro"] # Modelli standard 2026

modelli_disponibili = setup_gemini()
LOGO_URL = "https://nextahub.it/wp-content/uploads/2026/02/Nexta_Logo_Def_PiccoloHUB.png"

# --- 2. COSTANTI ---
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

# --- 3. MATRICE COMPLETA 54 DOMANDE ---
DOMANDE_MATRICE = {
    'Strategia & Controllo': [
        ("Piano Strategico", ["Nessun piano", "Verbali", "Budget annuale", "Piano triennale", "Piano dinamico"], None),
        ("Monitoraggio KPI", ["Assente", "Solo bilancio", "Excel saltuario", "Dashboard", "BI real-time"], None),
        ("Organigramma", ["Titolare", "Confuso", "Schema base", "Deleghe", "Manager autonomi"], None),
        ("Analisi Competitor", ["Mai", "Informale", "Annuale", "Costante", "Data-driven"], None),
        ("Delega", ["Nessuna", "Compiti base", "Capi area", "Responsabilità budget", "Direzione autonoma"], None),
        ("Passaggio Generazionale", ["Tabù", "Informale", "Successori scelti", "Affiancamento", "Patti famiglia"], None)
    ],
    'Digitalizzazione': [
        ("Infrastruttura IT", ["Obsolescente", "Base", "Server locale", "Cloud ibrido", "Full Cloud"], None),
        ("ERP/Gestionale", ["Fatture", "Contabilità", "Settoriale", "Integrato", "Ecosistema API"], None),
        ("Processi Paperless", ["Cartaceo", "Pochi PDF", "Misto", "Digitale", "Workflow automatici"], None),
        ("Cybersecurity", ["Base", "Backup saltuari", "Firewall", "Audit", "SOC 24/7"], None),
        ("Marketing Digitale", ["No", "Sito vetrina", "Social", "ADS/SEO", "Lead Gen"], None),
        ("Innovazione AI", ["No", "Sporadico", "Test area", "Integrata", "AI-driven"], ["ICT e Digitale", "Elettronica", "Meccanica"])
    ],
    'Gestione HR': [
        ("Welfare", ["No", "Rimborsi", "Convenzioni", "Piattaforma", "Benefit evoluti"], None),
        ("Valutazione", ["No", "Sensazioni", "Annuale", "MBO/KPI", "Feedback 360"], None),
        ("Retention", ["Fuga", "Media", "Bonus", "Employer Branding", "Top Employer"], None),
        ("Clima Aziendale", ["Tensioni", "Ignorato", "Saltuario", "Indagine str.", "Monitoraggio cont."], None),
        ("Formazione", ["Solo Legge", "Rari", "Budget dedicato", "Piani crescita", "Academy"], None),
        ("Smart Working", ["No", "Rara", "Flessibile", "Smart str.", "Anywhere"], None)
    ],
    'Finanza & Investimenti': [
        ("Cash Flow", ["No", "Saldo banca", "Mensile", "Previsionale 6m", "Tesoreria AI"], None),
        ("Finanza Agevolata", ["Mai", "Casuale", "Bandi base", "Monitoraggio", "Strategica"], None),
        ("Rating Bancario", ["No", "Vago", "Annuo", "Trimestrale", "Ottimizzazione"], None),
        ("Marginalità", ["Utile fine anno", "Stime", "Per commessa", "Analitica", "Predittiva"], None),
        ("Gestione Credito", ["Reattiva", "Solleciti", "Scritta", "Ufficio dedicato", "Assicurazione"], None),
        ("Investimenti R&S", ["0%", "Reattiva", "1-2%", "5%", ">5%"], None)
    ],
    'Sostenibilità (ESG)': [
        ("Cultura ESG", ["No", "Solo legge", "Isolate", "Piano Ind.", "Rating cert."], None),
        ("Ambiente", ["No", "Differenziata", "Monitoraggio", "Carbon Footprint", "Net Zero"], None),
        ("Inclusione", ["No", "Sensibilità", "Donne leader", "Policy", "Certificazione"], None),
        ("Etica", ["No", "Leggi", "Codice Etico", "Bilancio Sost.", "Società Benefit"], None),
        ("Governance", ["Padronale", "Famigliare", "CdA", "Indipendenti", "Evoluta"], None),
        ("Fornitori ESG", ["Prezzo", "Vicinanza", "Autocertificazione", "Audit", "Solo cert."], None)
    ],
    'Protezione Legale': [
        ("Modello 231", ["No", "Studio", "Adottato", "Aggiornato", "ODV attivo"], ["Costruzioni ed Edilizia", "Sanità", "Energia e Utilities"]),
        ("Privacy/GDPR", ["Base", "Obsoleta", "Conformità", "Audit", "DPO"], None),
        ("Contrattualistica", ["Verbali", "Web", "Standard", "Ad hoc", "Legal Management"], None),
        ("Marchi/IP", ["No", "Marchio", "Monitoraggio", "Strategia", "Brevetti"], None),
        ("Gestione Rischi", ["Emergenza", "Avvocato", "Tutela", "Prevenzione", "Proattiva"], None),
        ("Asset Protection", ["No", "Polizze", "Holding", "Trust", "Pianificazione"], None)
    ],
    'Sicurezza sul Lavoro': [
        ("DVR", ["Scaduto", "Standard", "Regolare", "Dinamico", "Eccellenza"], None),
        ("Formazione Sicurezza", ["Incompleta", "Legge", "In regola", "Comportamentale", "Cultura"], None),
        ("Salute", ["No", "Obbligatoria", "Pianificata", "KPI salute", "Prevenzione"], None),
        ("DPI", ["Libero", "Registro", "Controllo", "Digitale", "IoT"], None),
        ("Manutenzione", ["Guasto", "Registro", "Programmata", "Software", "Predittiva"], None),
        ("Appalti/DUVRI", ["No", "DURC", "DUVRI", "Coordinamento", "Audit"], None)
    ],
    'Standard & Qualità': [
        ("ISO 9001", ["No", "In corso", "Formale", "Strumento", "Motore"], None),
        ("Mappatura Processi", ["No", "Parziale", "Procedure", "Mappatura", "Lean"], None),
        ("Controllo Qualità", ["Fine", "Campione", "Sistemico", "Sensori", "Zero difetti"], None),
        ("Customer Satisfaction", ["Reclami", "Sondaggio", "Indagine", "NPS", "Co-progettazione"], None),
        ("Marcatura CE", ["No", "Documentale", "Certificata", "Controllo filiera", "Audit esterni"], ["Meccanica", "Elettronica", "Costruzioni ed Edilizia"]),
        ("Gestione Non Conformità", ["Risolte", "Excel", "Analisi Cause", "Azioni eff.", "Prevenzione"], None)
    ],
    'Sviluppo Competenze': [
        ("Gap Analysis", ["Mai", "Urgenze", "Su richiesta", "Annuale", "Mappatura"], None),
        ("Fondi Interprofessionali", ["Mai", "Rari", "Saltuari", "Sempre", "Ottimizzazione"], None),
        ("Learning", ["Aula", "Affiancamento", "E-learning", "Mix", "Academy"], None),
        ("Leadership", ["No", "Titolare", "Manager", "Coaching", "Diffusa"], None),
        ("Carriera", ["No", "Anzianità", "Crescita", "Percorsi chiari", "Meritocrazia"], None),
        ("Mindset", ["Resistenza", "Timore", "Pionieri", "Apertura", "DNA"], None)
    ]
}

# --- 4. ENGINE AI (FIXED FOR 2026 API) ---
def analizza_con_gemini(dati_cliente, punteggi):
    # Lista di tentativi con i nomi ufficiali completi
    tentativi_modelli = [
        "models/gemini-1.5-flash", 
        "models/gemini-1.5-pro", 
        "gemini-1.5-flash",
        "gemini-pro"
    ]
    
    gap_details = "\n".join([f"- {k}: {v:.1f}/5" for k,v in punteggi.items()])
    
    prompt = f"""
    Sei il Senior Partner di NextaHub. Analisi strategica per {dati_cliente['azienda']}.
    Settore: {dati_cliente['settore']} | Regione: {dati_cliente['regione']}
    
    DATI ASSESSMENT:
    {gap_details}
    
    COMPITI:
    1. Definisci un BENCHMARK realistico per il settore nella regione {dati_cliente['regione']}.
    2. Identifica i GAP critici.
    3. Proponi soluzioni NextaHub specifiche (Transizione 5.0, Certificazioni, Welfare, ecc.).
    4. Crea una ROADMAP 24 mesi pronta per copia-incolla su Word.
    """

    for model_name in tentativi_modelli:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            if response.text:
                return response.text
        except Exception as e:
            # Se questo modello fallisce, passa al prossimo della lista
            ultimo_errore = str(e)
            continue
            
    return f"❌ Errore critico: Nessun modello AI disponibile. Dettaglio: {ultimo_errore}"

# --- 5. INTERFACCIA ---
if 'page' not in st.session_state: st.session_state.page = "Anagrafica"
if 'clienti' not in st.session_state: st.session_state.clienti = {}
if 'current_piva' not in st.session_state: st.session_state.current_piva = None

with st.sidebar:
    st.image(LOGO_URL, width=180)
    st.markdown("---")
    if st.button("🏢 1. Anagrafica"): st.session_state.page = "Anagrafica"
    if st.button("📝 2. Assessment"): st.session_state.page = "Questionario"
    if st.button("📊 3. Report"): st.session_state.page = "Valutazione"

# PAGINA 1: ANAGRAFICA
if st.session_state.page == "Anagrafica":
    st.title("🏢 Anagrafica Cliente")
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
            rif_az = st.text_input("Rif. Aziendale")

        if st.form_submit_button("➡️ Prosegui"):
            if rs and pi and comune:
                st.session_state.clienti[pi] = {
                    "info": {"azienda": rs, "piva": pi, "settore": settore, "regione": regione, "comune": comune, "commerciale": comm},
                    "assessments": []
                }
                st.session_state.current_piva = pi
                st.session_state.page = "Questionario"
                st.rerun()

# PAGINA 2: QUESTIONARIO
elif st.session_state.page == "Questionario":
    pi = st.session_state.current_piva
    if not pi: st.warning("Inserisci anagrafica"); st.stop()
    
    st.title(f"📝 Assessment: {st.session_state.clienti[pi]['info']['azienda']}")
    tabs = st.tabs(list(DOMANDE_MATRICE.keys()))
    temp_scores = {}

    for i, area in enumerate(DOMANDE_MATRICE.keys()):
        with tabs[i]:
            scores = []
            for j, (dom, opt, lim) in enumerate(DOMANDE_MATRICE[area]):
                if lim is None or st.session_state.clienti[pi]['info']['settore'] in lim:
                    s = st.radio(f"**{dom}**", [1,2,3,4,5], format_func=lambda x: f"{x}: {opt[x-1]}", key=f"{pi}_{area}_{j}")
                    scores.append(s)
            temp_scores[area] = sum(scores)/len(scores) if scores else 3.0

    if st.button("📊 Genera Report"):
        st.session_state.clienti[pi]['assessments'].append({"punteggi": temp_scores, "report_ai": ""})
        st.session_state.page = "Valutazione"
        st.rerun()

# PAGINA 3: VALUTAZIONE
elif st.session_state.page == "Valutazione":
    pi = st.session_state.current_piva
    if not pi or not st.session_state.clienti[pi]['assessments']: st.warning("Dati mancanti"); st.stop()
    
    cl = st.session_state.clienti[pi]
    ass = cl['assessments'][-1]
    
    st.title(f"📊 Analisi {cl['info']['azienda']}")
    
    # RADAR CHART (FISSA)
    categories = list(ass['punteggi'].keys())
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=list(ass['punteggi'].values()), theta=categories, fill='toself', name='Azienda', line_color='#E63946'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    if st.button("🚀 Genera Report AI Word-Ready"):
        with st.spinner("L'AI sta analizzando settore e regione..."):
            ass['report_ai'] = analizza_con_gemini(cl['info'], ass['punteggi'])
            st.rerun()

    if ass['report_ai']:
        st.markdown("---")
        st.markdown(ass['report_ai'])
