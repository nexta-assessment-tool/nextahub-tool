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

setup_gemini()
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

# --- 4. MOTORE DI CONSULENZA AI NEXTAHUB ---
def analizza_con_gemini(dati_cliente, punteggi):
    try:
        # Auto-rilevamento modello
        validi = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        scelto = next((x for x in ["models/gemini-1.5-flash", "models/gemini-1.5-pro", "models/gemini-pro"] if x in validi), validi[0])
        model = genai.GenerativeModel(scelto)
        
        # Costruzione del Prompt Strategico
        prompt = f"""
        Agisci come Senior Partner e Consultant di NextaHub. Il tuo obiettivo è redigere un'analisi strategica che porti il cliente a sottoscrivere i servizi di Nexta.
        
        DATI CLIENTE:
        - Azienda: {dati_cliente['azienda']}
        - Settore: {dati_cliente['settore']}
        - Regione: {dati_cliente['regione']}
        
        SCORE RILEVATI (scala 1-5):
        {json.dumps(punteggi, indent=2)}
        
        STRUTTURA DEL REPORT (Obbligatoria):

        1. TABELLA COMPARATIVA SCORE VS BENCHMARK
           - Definisci un benchmark realistico per il settore "{dati_cliente['settore']}" nella regione "{dati_cliente['regione']}".
           - Crea una tabella con: Area | Score Azienda | Benchmark | Scostamento (Gap).
           - Spiega brevemente perché il benchmark è settato a quel livello in quella specifica regione.

        2. ANALISI DEI GAP E SOLUZIONI NEXTAHUB
           - Analizza i gap più critici. Dividili per URGENZA (Alta, Media, Bassa).
           - Spiega i BENEFICI tangibili (economici, legali, operativi) che l'azienda otterrebbe colmando questi gap.
           - Collega ogni gap a una soluzione NextaHub.

        3. ROADMAP DI TRASFORMAZIONE (12-24 MESI)
           - Crea un percorso a tappe (Fase 1: 0-6 mesi, Fase 2: 6-12 mesi, Fase 3: 12-24 mesi).
           - Definisci priorità e temi di sviluppo.

        4. RESOCONTO CONCLUSIVO E SERVIZI NEXTAHUB (CALL TO ACTION)
           - Identifica al massimo 2/3 servizi PRIORITARI.
           - IMPORTANTE: Uno dei servizi prioritari DEVE essere legato alla FINANZA (es. Formazione Finanziata, Transizione 5.0, Bandi Regionali) per spiegare come questo possa FINANZIARE IN PARTE gli altri interventi (es. GDPR, ISO, Project Management).
           - Elenca i servizi in modo puntuale (es. a) Attivazione GDPR, b) Certificazione ISO 9001, c) Formazione Finanziata).

        TONO: Professionale, autorevole, orientato alla vendita e alla risoluzione dei problemi.
        FORMATO: Markdown pulito, pronto per essere copiato in un documento Microsoft Word.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Errore durante la generazione del report: {str(e)}"

# --- 5. LOGICA APP ---
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

# PAGINA 1: ANAGRAFICA COMPLETA
if st.session_state.page == "Anagrafica":
    st.title("🏢 Anagrafica Cliente")
    with st.form("form_anag"):
        c1, c2 = st.columns(2)
        with c1:
            rs = st.text_input("Ragione Sociale *")
            pi = st.text_input("Partita IVA *")
            comune = st.text_input("Comune *")
            via = st.text_input("Via")
            civico = st.text_input("N. Civico")
        with c2:
            cap = st.text_input("CAP")
            prov = st.text_input("Provincia")
            settore = st.selectbox("Settore Business *", SETTORI)
            regione = st.selectbox("Regione *", REGIONI)
            rif_az = st.text_input("Rif. Aziendale")
            comm = st.text_input("Riferimento Commerciale Nexta")
        
        if st.form_submit_button("➡️ Salva e Continua"):
            if rs and pi and comune and settore:
                st.session_state.clienti[pi] = {
                    "info": {"azienda": rs, "piva": pi, "settore": settore, "regione": regione, "comune": comune, "commerciale": comm},
                    "assessments": []
                }
                st.session_state.current_piva = pi
                st.session_state.page = "Questionario"
                st.rerun()
            else: st.error("Compila i campi obbligatori (*)")

# PAGINA 2: ASSESSMENT 54 DOMANDE
elif st.session_state.page == "Questionario":
    pi = st.session_state.current_piva
    if not pi: st.warning("Torna in anagrafica"); st.stop()
    
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

    if st.button("📊 Elabora Risultati"):
        st.session_state.clienti[pi]['assessments'].append({"punteggi": temp_scores, "report_ai": ""})
        st.session_state.page = "Valutazione"
        st.rerun()

# PAGINA 3: RADAR + TABELLA + AI
elif st.session_state.page == "Valutazione":
    pi = st.session_state.current_piva
    if not pi: st.stop()
    cl = st.session_state.clienti[pi]
    ass = cl['assessments'][-1]
    
    st.title(f"📊 Risultati per {cl['info']['azienda']}")
    
    # Calcolo Benchmark (Fittizio per UI, l'AI lo affinerà nel report)
    bench_val = {"Strategia & Controllo": 3.5, "Digitalizzazione": 3.2, "Gestione HR": 3.4, "Finanza & Investimenti": 3.0, "Sostenibilità (ESG)": 3.1, "Protezione Legale": 3.8, "Sicurezza sul Lavoro": 4.2, "Standard & Qualità": 3.9, "Sviluppo Competenze": 3.3}

    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Radar Chart
        categories = list(ass['punteggi'].keys())
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=list(ass['punteggi'].values()), theta=categories, fill='toself', name='Azienda', line_color='red'))
        fig.add_trace(go.Scatterpolar(r=[bench_val[k] for k in categories], theta=categories, name='Benchmark Settore', line_color='blue'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), height=500)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Tabella Scostamenti
        st.subheader("Tabella Scostamenti")
        for cat in categories:
            diff = ass['punteggi'][cat] - bench_val[cat]
            color = "green" if diff >= 0 else "red"
            st.markdown(f"**{cat}**: {ass['punteggi'][cat]:.1f} ({diff:+.1f})")

    if st.button("🚀 Genera Analisi Strategica AI"):
        with st.spinner("Analisi in corso..."):
            ass['report_ai'] = analizza_con_gemini(cl['info'], ass['punteggi'])
            st.rerun()

    if ass['report_ai']:
        st.markdown("---")
        st.markdown(ass['report_ai'])
