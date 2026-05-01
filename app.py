import streamlit as st
import plotly.graph_objects as go
import google.generativeai as genai
from datetime import datetime
import pandas as pd

# --- 1. CONFIGURAZIONE DI SISTEMA ---
# Inserisci qui la tua chiave API di Google Gemini
API_KEY = "AIzaSyBDVGaDPzABpySSiKIkktpLisvjRcMiSqg"
LOGO_URL = "https://www.nextahub.it/wp-content/uploads/2023/05/logo-nextahub.png"

st.set_page_config(
    page_title="NextaHub Strategic Suite v3.0",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    "Strategia & Controllo": "Dashboard KPI, Passaggio Generazionale, Temporary Management e Revisione Processi.",
    "Digitalizzazione": "Piano Transizione 5.0, Cybersecurity, E-commerce e Integrazione AI.",
    "Gestione HR": "Welfare Aziendale, Academy, Sistemi di MBO e Ricerca/Selezione profili executive.",
    "Finanza & Investimenti": "Scouting Finanza Agevolata, Rating Bancario e Ottimizzazione Tesoreria.",
    "Sostenibilità (ESG)": "Redazione Bilancio Sostenibilità e Certificazione Parità di Genere.",
    "Protezione Legale": "Modello 231, Compliance GDPR e Asset Protection.",
    "Sicurezza sul Lavoro": "DVR Dinamico, Medicina del Lavoro e Formazione Finanziata.",
    "Standard & Qualità": "Certificazioni ISO e Audit di qualità sulla filiera.",
    "Sviluppo Competenze": "Fondi Interprofessionali, Coaching Manageriale e Reskilling."
}

# --- 4. MATRICE 54 DOMANDE ---
DOMANDE_MATRICE = {
    'Strategia & Controllo': [
        ("Piano Strategico", ["Nessun piano", "Obiettivi verbali", "Budget annuale", "Piano triennale", "Piano dinamico"]),
        ("Monitoraggio KPI", ["Assente", "Solo bilancio", "Excel saltuario", "Dashboard mensile", "BI real-time"]),
        ("Organigramma", ["Solo titolare", "Confuso", "Schema base", "Deleghe definite", "Manager autonomi"]),
        ("Analisi Competitor", ["Mai", "Informale", "Annuale", "Costante", "Data-driven"]),
        ("Delega", ["Nessuna", "Solo semplici", "Autonomia limitata", "Responsabilità budget", "Direzione autonoma"]),
        ("Passaggio Generazionale", ["Tabù", "Informale", "Successori scelti", "Affiancamento attivo", "Patti famiglia"])
    ],
    'Digitalizzazione': [
        ("Infrastruttura IT", ["Obsolescente", "Base", "Server locale", "Cloud ibrido", "Full Cloud"]),
        ("ERP/Gestionale", ["Solo fatture", "Contabilità", "Settoriale", "Integrato", "Ecosistema API"]),
        ("Processi Paperless", ["Cartaceo", "Scansioni", "Misto", "Digitale prevalente", "Workflow automatici"]),
        ("Cybersecurity", ["Base/Free", "Backup saltuari", "Firewall/Cloud", "Audit regolari", "SOC 24/7"]),
        ("Presenza Web", ["Assente", "Sito vetrina", "Social aggiornati", "ADS/SEO", "Lead generation"]),
        ("Innovazione AI", ["Nessuna", "Uso sporadico", "Test area", "Integrata", "AI-driven"])
    ],
    'Gestione HR': [
        ("Welfare", ["Assente", "Rimborsi", "Convenzioni", "Piattaforma attiva", "Benefit evoluti"]),
        ("Valutazione", ["Nessuna", "Sensazioni", "Colloquio annuo", "MBO/KPI", "Feedback 360"]),
        ("Retention", ["Fuga talenti", "Media", "Bonus sporadici", "Employer Branding", "Top Employer"]),
        ("Clima", ["Tensioni", "Ignorato", "Saltuario", "Indagine strutturata", "Monitoraggio continuo"]),
        ("Formazione", ["Solo obbligatoria", "Corsi rari", "Budget annuo", "Piani crescita", "Academy"]),
        ("Flessibilità", ["Presenza rigida", "Rara", "Oraria", "Smart strutturato", "Per obiettivi"])
    ],
    'Finanza & Investimenti': [
        ("Cash Flow", ["Nessuna", "Saldo banca", "Mensile", "Previsionale 6m", "Tesoreria predittiva"]),
        ("Finanza Agevolata", ["Mai", "Rara", "Bandi semplici", "Monitoraggio attivo", "Pianificazione"]),
        ("Rating Bancario", ["Sconosciuto", "Vago", "Annuo", "Trimestrale", "Ottimizzazione"]),
        ("Marginalità", ["Utile fine anno", "Stime macro", "Per commessa", "Analitica real-time", "Predittiva"]),
        ("Gestione Credito", ["Reattiva", "Solleciti", "Procedura scritta", "Ufficio dedicato", "Assicurazione"]),
        ("Investimenti R&S", ["0%", "Reattiva", "1-2%", "5%", ">5%"])
    ],
    'Sostenibilità (ESG)': [
        ("Cultura ESG", ["No", "Solo legge", "Iniziative isolate", "Piano industriale", "Rating certificato"]),
        ("Ambiente", ["No", "Differenziata", "Monitoraggio", "Carbon Footprint", "Net Zero"]),
        ("Inclusione", ["No", "Sensibilità", "Donne leader", "Policy scritte", "Certificazione Parità"]),
        ("Etica", ["No", "Leggi base", "Codice Etico", "Bilancio Sostenibilità", "Società Benefit"]),
        ("Governance", ["Padronale", "Famigliare", "CdA", "Indipendenti", "Evoluta"]),
        ("Catena Fornitori", ["Solo prezzo", "Vicinanza", "Autocertificazioni", "Audit ESG", "Solo certificati"])
    ],
    'Protezione Legale': [
        ("Modello 231", ["Assente", "Studio", "Adottato base", "Aggiornato", "ODV attivo"]),
        ("Privacy (GDPR)", ["Nomine base", "Obsoleta", "Conformità", "Audit periodici", "DPO nominato"]),
        ("Contrattualistica", ["Verbali", "Generici", "Standard", "Ad hoc", "Legal Management"]),
        ("Marchi/IP", ["No", "Marchio", "Monitoraggio", "Strategia brevetti", "Asset a bilancio"]),
        ("Gestione Rischi", ["Emergenza", "Al bisogno", "Tutela legale", "Prevenzione", "Proattiva"]),
        ("Asset Protection", ["No", "Polizze base", "Holding/Fondo", "Trust", "Pianificazione"])
    ],
    'Sicurezza sul Lavoro': [
        ("Conformità DVR", ["Scaduto", "Base", "Aggiornato", "Dinamico", "Eccellenza"]),
        ("Formazione", ["Incompleta", "Obbligatoria", "In regola", "Comportamentale", "Cultura diffusa"]),
        ("Salute", ["Assente", "Obbligatoria", "Pianificata", "KPI salute", "Prevenzione"]),
        ("Gestione DPI", ["Informale", "Cartaceo", "Controllo", "Digitale", "IoT"]),
        ("Manutenzioni", ["A guasto", "Registro", "Programmata", "Software", "Predittiva"]),
        ("Gestione Appalti", ["No", "DURC", "DUVRI", "Coordinamento", "Audit costante"])
    ],
    'Standard & Qualità': [
        ("ISO 9001", ["No", "In corso", "Formale", "Strumento", "Motore"]),
        ("Processi", ["No", "Parziale", "Procedure core", "Mappatura totale", "Lean"]),
        ("Controllo Qualità", ["Fine", "Campionamento", "Sistemico", "Sensori", "Zero difetti"]),
        ("Soddisfazione", ["Reclami", "Sporadica", "Strutturata", "NPS", "Co-progettazione"]),
        ("Qualifica Fornitori", ["Prezzo", "Storici", "Albo", "Rating", "Partnership"]),
        ("Non Conformità", ["Risolte", "Excel", "Cause radice", "Azioni efficaci", "Prevenzione"])
    ],
    'Sviluppo Competenze': [
        ("Gap Analysis", ["Mai", "Urgenze", "Su richiesta", "Annuale", "Mappatura futuro"]),
        ("Uso Fondi", ["Mai", "Rari", "Saltuari", "Sempre", "Ottimizzazione"]),
        ("Learning", ["Aula", "Affiancamento", "E-learning", "Blended", "Academy"]),
        ("Leadership", ["No", "Titolare", "Manager", "Coaching", "Diffusa"]),
        ("Carriera", ["No", "Anzianità", "Opportunità", "Percorsi chiari", "Meritocrazia"]),
        ("Mindset", ["Resistenza", "Timore", "Pionieri", "Apertura", "DNA Innovazione"])
    ]
}

# --- 5. FUNZIONI LOGICHE ---
def genera_consulenza_ai(punteggi, info):
    peggiori = sorted(punteggi.items(), key=lambda x: x[1])[:3]
    prompt = f"""
    Agisci come Partner NextaHub. Analizza l'azienda {info['azienda']} ({info['settore']}).
    Punteggi: {punteggi}. Criticità: {peggiori}. 
    Usa il catalogo: {SERVIZI_NEXTA}.
    Genera un report professionale, con roadmap a 12 mesi.
    """
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(prompt).text
    except:
        return "⚠️ Configurare la Chiave API Gemini per ricevere l'analisi avanzata."

# --- 6. GESTIONE STATO ---
if 'page' not in st.session_state: st.session_state.page = "Anagrafica"
if 'clienti' not in st.session_state: st.session_state.clienti = {}
if 'current_piva' not in st.session_state: st.session_state.current_piva = None

# --- 7. SIDEBAR ---
with st.sidebar:
    st.image(LOGO_URL, width=200)
    st.markdown("### 🛠️ Menu")
    if st.button("🏢 Anagrafica Cliente", use_container_width=True): st.session_state.page = "Anagrafica"
    if st.button("📝 Assessment", use_container_width=True): st.session_state.page = "Questionario"
    if st.button("📊 Report & Gap", use_container_width=True): st.session_state.page = "Valutazione"
    if st.button("📁 Archivio Storico", use_container_width=True): st.session_state.page = "Archivio"
    st.markdown("---")
    if st.session_state.current_piva:
        cl_name = st.session_state.clienti[st.session_state.current_piva]['info']['azienda']
        st.success(f"Attivo: {cl_name}")

# --- 8. PAGINA 1: ANAGRAFICA ---
if st.session_state.page == "Anagrafica":
    st.title("🏢 Anagrafica Cliente")
    with st.form("form_anag"):
        c1, c2 = st.columns(2)
        with c1:
            rag_soc = st.text_input("Ragione Sociale")
            p_iva = st.text_input("P.IVA / CF")
            v_ia = st.text_input("Via/Piazza")
            c_iv = st.text_input("Civico")
        with c2:
            c_ap = st.text_input("CAP")
            c_om = st.text_input("Comune")
            p_rov = st.text_input("Provincia (Sigla)")
            settore = st.selectbox("Settore", list(BENCHMARK_DATI.keys()))
        
        if st.form_submit_button("Salva e Procedi"):
            if rag_soc and p_iva:
                st.session_state.clienti[p_iva] = {
                    "info": {
                        "azienda": rag_soc, "piva": p_iva, "via": v_ia, "civico": c_iv,
                        "cap": c_ap, "comune": c_om, "provincia": p_rov, "settore": settore
                    },
                    "assessments": []
                }
                st.session_state.current_piva = p_iva
                st.session_state.page = "Questionario"
                st.rerun()
            else:
                st.error("Ragione Sociale e P.IVA sono obbligatori.")

# --- 9. PAGINA 2: QUESTIONARIO (54 DOMANDE) ---
elif st.session_state.page == "Questionario":
    piva = st.session_state.current_piva
    if not piva: 
        st.warning("Seleziona un cliente."); st.stop()
    
    st.title(f"📝 Assessment: {st.session_state.clienti[piva]['info']['azienda']}")
    tabs = st.tabs(list(DOMANDE_MATRICE.keys()))
    temp_scores = {}

    for i, area in enumerate(DOMANDE_MATRICE.keys()):
        with tabs[i]:
            sc_area = []
            for j, (q, opts) in enumerate(DOMANDE_MATRICE[area]):
                st.markdown(f"**{j+1}. {q}**")
                s = st.radio(f"q_{area}_{j}", [1,2,3,4,5], format_func=lambda x: f"{x}: {opts[x-1]}", key=f"sel_{piva}_{area}_{j}", label_visibility="collapsed")
                sc_area.append(s)
            temp_scores[area] = sum(sc_area) / 6

    if st.button("✅ Salva Analisi", use_container_width=True):
        st.session_state.clienti[piva]['assessments'].append({
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "punteggi": temp_scores,
            "analisi": ""
        })
        st.session_state.page = "Valutazione"
        st.rerun()

# --- 10. PAGINA 3: VALUTAZIONE & AI ---
elif st.session_state.page == "Valutazione":
    piva = st.session_state.current_piva
    if not piva or not st.session_state.clienti[piva]['assessments']:
        st.warning("Nessun dato."); st.stop()
    
    cl = st.session_state.clienti[piva]
    ass = cl['assessments'][-1]
    info = cl['info']

    st.title(f"📊 Report: {info['azienda']}")
    st.caption(f"📍 {info['via']} {info['civico']}, {info['cap']} {info['comune']} ({info['provincia']})")

    # Radar Chart
    fig = go.Figure()
    categories = list(ass['punteggi'].keys())
    fig.add_trace(go.Scatterpolar(r=list(ass['punteggi'].values()), theta=categories, fill='toself', name='Azienda', line_color='red'))
    fig.add_trace(go.Scatterpolar(r=[BENCHMARK_DATI[info['settore']][k] for k in categories], theta=categories, name='Benchmark', line_color='gray', line_dash='dash'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), height=550)
    st.plotly_chart(fig, use_container_width=True)

    # AI Agent
    st.subheader("🤖 Analisi Strategica NextaHub (AI)")
    if not ass['analisi']:
        if st.button("Genera Report con AI"):
            with st.spinner("Elaborazione..."):
                ass['analisi'] = genera_consulenza_ai(ass['punteggi'], info)
                st.rerun()
    else:
        st.markdown(ass['analisi'])

# --- 11. PAGINA 4: ARCHIVIO ---
elif st.session_state.page == "Archivio":
    st.title("📁 Archivio Storico")
    if not st.session_state.clienti:
        st.info("Nessun cliente registrato.")
    else:
        for p, d in st.session_state.clienti.items():
            with st.expander(f"🏢 {d['info']['azienda']} (PI: {p})"):
                st.write(f"**Settore:** {d['info']['settore']}")
                for i, a in enumerate(d['assessments']):
                    if st.button(f"Vedi Report del {a['data']}", key=f"arch_{p}_{i}"):
                        st.session_state.current_piva = p
                        st.session_state.page = "Valutazione"
                        st.rerun()
