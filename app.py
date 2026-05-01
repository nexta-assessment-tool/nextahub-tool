import streamlit as st
import plotly.graph_objects as go
import google.generativeai as genai
from datetime import datetime

# --- 1. CONFIGURAZIONE ---
API_KEY = "AIzaSyBDVGaDPzABpySSiKIkktpLisvjRcMiSqg"
LOGO_URL = "https://www.nextahub.it/wp-content/uploads/2023/05/logo-nextahub.png"

st.set_page_config(page_title="NextaHub Strategic Suite v3.0", layout="wide")

# --- 2. DATABASE BENCHMARK (17 SETTORI) ---
BENCHMARK_DATI = {
    "Agroalimentare (Food & Beverage)": {"Strategia & Controllo": 3.4, "Digitalizzazione": 3.0, "Gestione HR": 3.1, "Finanza & Investimenti": 3.2, "Sostenibilità (ESG)": 3.8, "Protezione Legale": 3.5, "Sicurezza sul Lavoro": 4.2, "Standard & Qualità": 4.5, "Sviluppo Competenze": 3.0},
    "Moda e Tessile (Fashion & Luxury)": {"Strategia & Controllo": 3.6, "Digitalizzazione": 3.8, "Gestione HR": 3.5, "Finanza & Investimenti": 3.4, "Sostenibilità (ESG)": 4.0, "Protezione Legale": 4.2, "Sicurezza sul Lavoro": 3.5, "Standard & Qualità": 4.0, "Sviluppo Competenze": 3.7},
    "Arredo e Design (Furniture)": {"Strategia & Controllo": 3.3, "Digitalizzazione": 3.2, "Gestione HR": 3.0, "Finanza & Investimenti": 3.1, "Sostenibilità (ESG)": 3.5, "Protezione Legale": 3.4, "Sicurezza sul Lavoro": 3.8, "Standard & Qualità": 3.9, "Sviluppo Competenze": 3.2},
    "Meccanica e Automazione": {"Strategia & Controllo": 3.5, "Digitalizzazione": 3.8, "Gestione HR": 3.4, "Finanza & Investimenti": 3.6, "Sostenibilità (ESG)": 3.0, "Protezione Legale": 3.5, "Sicurezza sul Lavoro": 4.5, "Standard & Qualità": 4.2, "Sviluppo Competenze": 3.8},
    "Metallurgia e Siderurgia": {"Strategia & Controllo": 3.2, "Digitalizzazione": 3.0, "Gestione HR": 3.1, "Finanza & Investimenti": 3.4, "Sostenibilità (ESG)": 2.8, "Protezione Legale": 3.6, "Sicurezza sul Lavoro": 4.8, "Standard & Qualità": 4.1, "Sviluppo Competenze": 3.0},
    "Automotive (Automobilistico)": {"Strategia & Controllo": 3.8, "Digitalizzazione": 4.2, "Gestione HR": 3.7, "Finanza & Investimenti": 3.5, "Sostenibilità (ESG)": 3.9, "Protezione Legale": 4.0, "Sicurezza sul Lavoro": 4.6, "Standard & Qualità": 4.8, "Sviluppo Competenze": 4.0},
    "Chimico e Farmaceutico": {"Strategia & Controllo": 3.9, "Digitalizzazione": 3.7, "Gestione HR": 3.8, "Finanza & Investimenti": 3.6, "Sostenibilità (ESG)": 4.2, "Protezione Legale": 4.5, "Sicurezza sul Lavoro": 4.9, "Standard & Qualità": 4.7, "Sviluppo Competenze": 3.9},
    "Energia e Utilities (Gas, Luce, Acqua)": {"Strategia & Controllo": 4.0, "Digitalizzazione": 3.9, "Gestione HR": 3.8, "Finanza & Investimenti": 3.7, "Sostenibilità (ESG)": 4.5, "Protezione Legale": 4.2, "Sicurezza sul Lavoro": 4.7, "Standard & Qualità": 4.3, "Sviluppo Competenze": 3.8},
    "Costruzioni ed Edilizia": {"Strategia & Controllo": 2.8, "Digitalizzazione": 2.5, "Gestione HR": 2.9, "Finanza & Investimenti": 3.0, "Sostenibilità (ESG)": 2.7, "Protezione Legale": 3.4, "Sicurezza sul Lavoro": 4.7, "Standard & Qualità": 3.4, "Sviluppo Competenze": 2.8},
    "Elettronica ed Elettrotecnica": {"Strategia & Controllo": 3.7, "Digitalizzazione": 4.0, "Gestione HR": 3.5, "Finanza & Investimenti": 3.6, "Sostenibilità (ESG)": 3.4, "Protezione Legale": 3.8, "Sicurezza sul Lavoro": 4.0, "Standard & Qualità": 4.4, "Sviluppo Competenze": 3.9},
    "Gomma e Materie Plastiche": {"Strategia & Controllo": 3.2, "Digitalizzazione": 3.3, "Gestione HR": 3.1, "Finanza & Investimenti": 3.2, "Sostenibilità (ESG)": 3.0, "Protezione Legale": 3.5, "Sicurezza sul Lavoro": 4.4, "Standard & Qualità": 4.0, "Sviluppo Competenze": 3.1},
    "Carta e Stampa (Packaging ed Editoria)": {"Strategia & Controllo": 3.4, "Digitalizzazione": 3.5, "Gestione HR": 3.2, "Finanza & Investimenti": 3.3, "Sostenibilità (ESG)": 3.6, "Protezione Legale": 3.5, "Sicurezza sul Lavoro": 4.2, "Standard & Qualità": 4.1, "Sviluppo Competenze": 3.3},
    "ICT e Digitale (Software e Tecnologie)": {"Strategia & Controllo": 4.0, "Digitalizzazione": 4.8, "Gestione HR": 4.2, "Finanza & Investimenti": 3.6, "Sostenibilità (ESG)": 3.5, "Protezione Legale": 4.0, "Sicurezza sul Lavoro": 3.0, "Standard & Qualità": 3.8, "Sviluppo Competenze": 4.5},
    "Logistica e Trasporti": {"Strategia & Controllo": 3.2, "Digitalizzazione": 3.9, "Gestione HR": 3.1, "Finanza & Investimenti": 3.0, "Sostenibilità (ESG)": 3.3, "Protezione Legale": 3.7, "Sicurezza sul Lavoro": 4.4, "Standard & Qualità": 3.9, "Sviluppo Competenze": 3.2},
    "Turismo e Ristorazione (Horeca)": {"Strategia & Controllo": 3.0, "Digitalizzazione": 3.4, "Gestione HR": 3.5, "Finanza & Investimenti": 2.8, "Sostenibilità (ESG)": 3.2, "Protezione Legale": 3.3, "Sicurezza sul Lavoro": 3.9, "Standard & Qualità": 3.7, "Sviluppo Competenze": 3.4},
    "Bancario e Assicurativo": {"Strategia & Controllo": 4.2, "Digitalizzazione": 4.5, "Gestione HR": 4.0, "Finanza & Investimenti": 4.5, "Sostenibilità (ESG)": 4.1, "Protezione Legale": 4.8, "Sicurezza sul Lavoro": 3.5, "Standard & Qualità": 4.6, "Sviluppo Competenze": 4.2},
    "Sanità e Servizi Sociali": {"Strategia & Controllo": 3.8, "Digitalizzazione": 3.5, "Gestione HR": 4.1, "Finanza & Investimenti": 3.2, "Sostenibilità (ESG)": 3.7, "Protezione Legale": 4.4, "Sicurezza sul Lavoro": 4.5, "Standard & Qualità": 4.7, "Sviluppo Competenze": 3.8}
}

# --- 3. CATALOGO SERVIZI NEXTAHUB ---
SERVIZI_NEXTA = {
    "Strategia & Controllo": "Dashboard KPI, Passaggio Generazionale, Temporary Management.",
    "Digitalizzazione": "Transizione 5.0, Cybersecurity, Integrazione AI.",
    "Gestione HR": "Welfare Aziendale, Academy, Sistemi MBO.",
    "Finanza & Investimenti": "Finanza Agevolata, Rating Bancario, Crediti d'imposta.",
    "Sostenibilità (ESG)": "Bilancio di Sostenibilità, Certificazione Parità di Genere.",
    "Protezione Legale": "Modello 231, Compliance GDPR, Asset Protection.",
    "Sicurezza sul Lavoro": "DVR Dinamico, Medicina del Lavoro, Formazione 81/08.",
    "Standard & Qualità": "Certificazioni ISO, Ottimizzazione Processi.",
    "Sviluppo Competenze": "Fondi Interprofessionali, Coaching Manageriale."
}

# --- 4. MATRICE COMPLETA 54 DOMANDE ---
DOMANDE_MATRICE = {
    'Strategia & Controllo': [
        ("Piano Strategico", ["Nessun piano", "Verbali", "Budget annuale", "Piano triennale", "Piano dinamico"]),
        ("Monitoraggio KPI", ["Assente", "Solo bilancio", "Excel saltuario", "Dashboard", "BI real-time"]),
        ("Organigramma", ["Titolare", "Confuso", "Schema base", "Deleghe", "Manager autonomi"]),
        ("Analisi Competitor", ["Mai", "Informale", "Annuale", "Costante", "Data-driven"]),
        ("Delega", ["Nessuna", "Compiti base", "Capi area", "Responsabilità budget", "Direzione autonoma"]),
        ("Passaggio Generazionale", ["Tabù", "Informale", "Successori scelti", "Affiancamento", "Patti famiglia"])
    ],
    'Digitalizzazione': [
        ("Infrastruttura IT", ["Obsolescente", "Base", "Server locale", "Cloud ibrido", "Full Cloud"]),
        ("ERP/Gestionale", ["Fatture", "Contabilità", "Settoriale", "Integrato", "Ecosistema API"]),
        ("Processi Paperless", ["Cartaceo", "Pochi PDF", "Misto", "Digitale", "Workflow automatici"]),
        ("Cybersecurity", ["Base", "Backup saltuari", "Firewall", "Audit", "SOC 24/7"]),
        ("Marketing Digitale", ["No", "Sito vetrina", "Social", "ADS/SEO", "Lead Gen"]),
        ("Innovazione AI", ["No", "Sporadico", "Test area", "Integrata", "AI-driven"])
    ],
    'Gestione HR': [
        ("Welfare", ["No", "Rimborsi", "Convenzioni", "Piattaforma", "Benefit evoluti"]),
        ("Valutazione", ["No", "Sensazioni", "Annuale", "MBO/KPI", "Feedback 360"]),
        ("Retention", ["Fuga", "Media", "Bonus", "Employer Branding", "Top Employer"]),
        ("Clima", ["Tensioni", "Ignorato", "Saltuario", "Indagine str.", "Monitoraggio cont."]),
        ("Formazione", ["Legge", "Rari", "Budget", "Piani crescita", "Academy"]),
        ("Smart Working", ["No", "Rara", "Flessibile", "Smart str.", "Anywhere"])
    ],
    'Finanza & Investimenti': [
        ("Cash Flow", ["No", "Saldo banca", "Mensile", "Previsionale 6m", "Tesoreria AI"]),
        ("Agevolata", ["Mai", "Casuale", "Bandi base", "Monitoraggio", "Strategica"]),
        ("Rating Bancario", ["No", "Vago", "Annuo", "Trimestrale", "Ottimizzazione"]),
        ("Marginalità", ["Utile fine anno", "Stime", "Per commessa", "Analitica", "Predittiva"]),
        ("Gestione Credito", ["Reattiva", "Solleciti", "Scritta", "Ufficio dedicato", "Assicurazione"]),
        ("R&S", ["0%", "Reattiva", "1-2%", "5%", ">5%"])
    ],
    'Sostenibilità (ESG)': [
        ("Cultura ESG", ["No", "Solo legge", "Isolate", "Piano Ind.", "Rating cert."]),
        ("Ambiente", ["No", "Differenziata", "Monitoraggio", "Carbon Footprint", "Net Zero"]),
        ("Inclusione", ["No", "Sensibilità", "Donne leader", "Policy", "Certificazione"]),
        ("Etica", ["No", "Leggi", "Codice Etico", "Bilancio Sost.", "Società Benefit"]),
        ("Governance", ["Padronale", "Famigliare", "CdA", "Indipendenti", "Evoluta"]),
        ("Fornitori ESG", ["Prezzo", "Vicinanza", "Autocertificazione", "Audit", "Solo cert."])
    ],
    'Protezione Legale': [
        ("Modello 231", ["No", "Studio", "Adottato", "Aggiornato", "ODV attivo"]),
        ("Privacy", ["Base", "Obsoleta", "Conformità", "Audit", "DPO"]),
        ("Contratti", ["Verbali", "Web", "Standard", "Ad hoc", "Legal Management"]),
        ("Marchi/IP", ["No", "Marchio", "Monitoraggio", "Strategia", "Brevetti"]),
        ("Rischi", ["Emergenza", "Avvocato", "Tutela", "Prevenzione", "Proattiva"]),
        ("Asset Protection", ["No", "Polizze", "Holding", "Trust", "Pianificazione"])
    ],
    'Sicurezza sul Lavoro': [
        ("DVR", ["Scaduto", "Standard", "Regolare", "Dinamico", "Eccellenza"]),
        ("Formazione", ["Incompleta", "Legge", "In regola", "Comportamentale", "Cultura"]),
        ("Salute", ["No", "Obbligatoria", "Pianificata", "KPI salute", "Prevenzione"]),
        ("DPI", ["Libero", "Registro", "Controllo", "Digitale", "IoT"]),
        ("Manutenzione", ["Guasto", "Registro", "Programmata", "Software", "Predittiva"]),
        ("Appalti", ["No", "DURC", "DUVRI", "Coordinamento", "Audit"])
    ],
    'Standard & Qualità': [
        ("ISO 9001", ["No", "In corso", "Formale", "Strumento", "Motore"]),
        ("Processi", ["No", "Parziale", "Procedure", "Mappatura", "Lean"]),
        ("Controllo Qualità", ["Fine", "Campione", "Sistemico", "Sensori", "Zero difetti"]),
        ("Clienti", ["Reclami", "Sondaggio", "Indagine", "NPS", "Co-progettazione"]),
        ("Fornitori", ["Prezzo", "Storici", "Albo", "Rating", "Partnership"]),
        ("Non Conformità", ["Risolte", "Excel", "Analisi Cause", "Azioni eff.", "Prevenzione"])
    ],
    'Sviluppo Competenze': [
        ("Gap Analysis", ["Mai", "Urgenze", "Su richiesta", "Annuale", "Mappatura"]),
        ("Fondi", ["Mai", "Rari", "Saltuari", "Sempre", "Ottimizzazione"]),
        ("Learning", ["Aula", "Affiancamento", "E-learning", "Mix", "Academy"]),
        ("Leadership", ["No", "Titolare", "Manager", "Coaching", "Diffusa"]),
        ("Carriera", ["No", "Anzianità", "Crescita", "Percorsi chiari", "Meritocrazia"]),
        ("Mindset", ["Resistenza", "Timore", "Pionieri", "Apertura", "DNA"])
    ]
}

# --- 5. AGENTE AI ---
def genera_report_ai(punteggi, info, benchmark):
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        gap_testo = "\n".join([f"- {k}: Azienda {v}/5 (Target Settore {benchmark[k]}/5)" for k,v in punteggi.items()])
        
        prompt = f"""
        Sei il Senior Partner di NextaHub. Crea un Report Strategico di ANALISI GAP per {info['azienda']} ({info['settore']}).
        DATI:
        {gap_testo}
        SERVIZI NEXTA: {SERVIZI_NEXTA}

        STRUTTURA RICHIESTA (Sii estremamente prolisso, tecnico e descrittivo - puntiamo a 4 pagine di contenuto):
        1. ANALISI DELLO STATO DELL'ARTE: Spiega perché l'azienda si trova in questa posizione rispetto al mercato.
        2. DETTAGLIO GAP PER AREA: Analizza ognuna delle 9 aree. Spiega cosa manca per raggiungere il benchmark e i rischi del non agire.
        3. PIANO DI AZIONE NEXTAHUB (ROADMAP 24 MESI): Suggerisce quali servizi Nexta attivare subito e quali dopo.
        4. VANTAGGIO COMPETITIVO: Come queste azioni trasformeranno l'azienda in un leader di settore.
        
        Usa un tono autorevole, linguaggio da alta consulenza e formatta in Markdown elegante.
        """
        return model.generate_content(prompt).text
    except:
        return "⚠️ Errore AI. Controlla API Key o connessione."

# --- 6. LOGICA APP ---
if 'page' not in st.session_state: st.session_state.page = "Anagrafica"
if 'clienti' not in st.session_state: st.session_state.clienti = {}
if 'current_piva' not in st.session_state: st.session_state.current_piva = None

# --- SIDEBAR ---
with st.sidebar:
    st.image(LOGO_URL, width=200)
    if st.button("🏢 Anagrafica"): st.session_state.page = "Anagrafica"
    if st.button("📝 Assessment"): st.session_state.page = "Questionario"
    if st.button("📊 Report"): st.session_state.page = "Valutazione"
    if st.button("📁 Archivio"): st.session_state.page = "Archivio"
    if st.session_state.current_piva:
        st.info(f"Cliente: {st.session_state.clienti[st.session_state.current_piva]['info']['azienda']}")

# --- PAGINA 1: ANAGRAFICA ---
if st.session_state.page == "Anagrafica":
    st.title("🏢 Anagrafica Cliente")
    with st.form("anag"):
        c1, c2 = st.columns(2)
        with c1:
            rs = st.text_input("Ragione Sociale")
            pi = st.text_input("P.IVA")
            via = st.text_input("Via")
            civ = st.text_input("Civico")
        with c2:
            cap = st.text_input("CAP")
            pa = st.text_input("Paese", "Italia")
            pr = st.text_input("Provincia")
            set_ = st.selectbox("Settore", list(BENCHMARK_DATI.keys()))
        if st.form_submit_button("Salva"):
            if rs and pi:
                st.session_state.clienti[pi] = {"info": {"azienda": rs, "piva": pi, "settore": set_, "indirizzo": f"{via} {civ}, {cap} {pr} ({pa})"}, "assessments": []}
                st.session_state.current_piva = pi
                st.session_state.page = "Questionario"
                st.rerun()

# --- PAGINA 2: QUESTIONARIO ---
elif st.session_state.page == "Questionario":
    pi = st.session_state.current_piva
    if not pi: st.error("Inserisci anagrafica"); st.stop()
    st.title("📝 Assessment Strategico")
    tabs = st.tabs(list(DOMANDE_MATRICE.keys()))
    res = {}
    for i, area in enumerate(DOMANDE_MATRICE.keys()):
        with tabs[i]:
            scores = []
            for j, (q, opts) in enumerate(DOMANDE_MATRICE[area]):
                s = st.radio(q, [1,2,3,4,5], format_func=lambda x: f"{x}: {opts[x-1]}", key=f"{pi}{area}{j}")
                scores.append(s)
            res[area] = sum(scores)/6
    if st.button("Salva Assessment"):
        st.session_state.clienti[pi]['assessments'].append({"data": datetime.now().strftime("%d/%m/%Y"), "punteggi": res, "ai": ""})
        st.session_state.page = "Valutazione"
        st.rerun()

# --- PAGINA 3: VALUTAZIONE ---
elif st.session_state.page == "Valutazione":
    pi = st.session_state.current_piva
    if not pi or not st.session_state.clienti[pi]['assessments']: st.error("Dati mancanti"); st.stop()
    cl = st.session_state.clienti[pi]
    ass = cl['assessments'][-1]
    
    st.title(f"📊 Report: {cl['info']['azienda']}")
    
    # Grafico Radar
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=list(ass['punteggi'].values()), theta=list(ass['punteggi'].keys()), fill='toself', name='Azienda'))
    fig.add_trace(go.Scatterpolar(r=[BENCHMARK_DATI[cl['info']['settore']][k] for k in ass['punteggi'].keys()], theta=list(ass['punteggi'].keys()), name='Benchmark'))
    st.plotly_chart(fig)

    if st.button("🚀 Genera Analisi AI Profonda"):
        with st.spinner("L'Agente Nexta sta scrivendo..."):
            ass['ai'] = genera_report_ai(ass['punteggi'], cl['info'], BENCHMARK_DATI[cl['info']['settore']])
            st.rerun()
    if ass['ai']:
        st.markdown(ass['ai'])

# --- PAGINA 4: ARCHIVIO ---
elif st.session_state.page == "Archivio":
    st.title("📁 Archivio")
    for p, d in st.session_state.clienti.items():
        if st.button(f"{d['info']['azienda']} ({p})"):
            st.session_state.current_piva = p
            st.session_state.page = "Valutazione"
            st.rerun()
