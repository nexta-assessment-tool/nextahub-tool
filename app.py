import streamlit as st
import plotly.graph_objects as go
import google.generativeai as genai
from datetime import datetime

# --- 1. CONFIGURAZIONE API E PAGINA ---
st.set_page_config(page_title="NextaHub Strategic Suite v3.0", layout="wide")

# Caricamento della chiave con il nuovo nome coerente: GEMINI_API_KEY
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    except Exception as e:
        st.error(f"Errore configurazione Gemini: {e}")
else:
    st.error("⚠️ Chiave non trovata! Assicurati di aver impostato 'GEMINI_API_KEY' nei Secrets di Streamlit.")
    st.stop()

LOGO_URL = "https://nextahub.it/wp-content/uploads/2026/02/Nexta_Logo_Def_PiccoloHUB.png"

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

# --- 4. MATRICE 54 DOMANDE ---
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

# --- 5. AGENTE GEMINI (MULTI-MODELLO AUTO-ADATTIVO) ---
def genera_report_ai(punteggi, info, benchmark):
    # Gemini prova i suoi motori migliori in sequenza
    modelli_tentativo = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
    
    gap_testo = "\n".join([f"- {k}: Azienda {v:.2f}/5 (Benchmark {benchmark[k]}/5)" for k,v in punteggi.items()])
    
    prompt = f"""
    Sei il Senior Partner di NextaHub. Crea un Report Strategico ANALISI GAP per {info['azienda']} ({info['settore']}).
    DATI ASSESSMENT:
    {gap_testo}
    
    CATALOGO SERVIZI NEXTAHUB DA PROPORRE: {SERVIZI_NEXTA}

    STRUTTURA DEL REPORT:
    1. EXECUTIVE SUMMARY: Sintesi del posizionamento attuale.
    2. ANALISI DEI GAP: Per ogni area, spiega il rischio di restare sotto il benchmark di settore.
    3. ROADMAP STRATEGICA (24 MESI):
       - Fase 1 (0-6m): Azioni urgenti.
       - Fase 2 (6-18m): Consolidamento.
       - Fase 3 (18-24m): Eccellenza.
    4. CONCLUSIONI: Il valore aggiunto finale dell'intervento NextaHub.
    
    Usa tabelle Markdown, un tono autorevole e professionale.
    """

    for nome in modelli_tentativo:
        try:
            model = genai.GenerativeModel(nome)
            response = model.generate_content(prompt)
            return response.text
        except Exception:
            continue
            
    return "⚠️ L'intelligenza Gemini non è riuscita a generare il report. Verifica la tua GEMINI_API_KEY."

# --- 6. LOGICA DI NAVIGAZIONE ---
if 'page' not in st.session_state: st.session_state.page = "Anagrafica"
if 'clienti' not in st.session_state: st.session_state.clienti = {}
if 'current_piva' not in st.session_state: st.session_state.current_piva = None

with st.sidebar:
    st.image(LOGO_URL, width=200)
    st.markdown("---")
    if st.button("🏢 Anagrafica Cliente", use_container_width=True): st.session_state.page = "Anagrafica"
    if st.button("📝 Esegui Assessment", use_container_width=True): st.session_state.page = "Questionario"
    if st.button("📊 Report Strategico", use_container_width=True): st.session_state.page = "Valutazione"
    if st.button("📁 Archivio Storico", use_container_width=True): st.session_state.page = "Archivio"
    st.markdown("---")
    if st.session_state.current_piva:
        cl_info = st.session_state.clienti[st.session_state.current_piva]['info']
        st.success(f"Dati di: {cl_info['azienda']}")

# --- PAGINE ---
if st.session_state.page == "Anagrafica":
    st.title("🏢 Anagrafica Cliente")
    with st.form("anag"):
        c1, c2 = st.columns(2)
        with c1:
            rs = st.text_input("Ragione Sociale")
            pi = st.text_input("P.IVA / Codice Univoco")
            via = st.text_input("Indirizzo")
            civ = st.text_input("Civico")
        with c2:
            cap = st.text_input("CAP")
            com = st.text_input("Comune")
            pr = st.text_input("Provincia (Sigla)")
            set_ = st.selectbox("Settore Business", list(BENCHMARK_DATI.keys()))
        if st.form_submit_button("Apri Pratica"):
            if rs and pi:
                st.session_state.clienti[pi] = {
                    "info": {"azienda": rs, "piva": pi, "settore": set_, "loc": f"{via} {civ}, {cap} {com} ({pr})"},
                    "assessments": []
                }
                st.session_state.current_piva = pi
                st.session_state.page = "Questionario"
                st.rerun()
            else:
                st.error("Inserisci Ragione Sociale e P.IVA per procedere.")

elif st.session_state.page == "Questionario":
    pi = st.session_state.current_piva
    if not pi:
        st.warning("Torna in Anagrafica e seleziona un cliente.")
        st.stop()
    
    st.title(f"📝 Assessment Digitale: {st.session_state.clienti[pi]['info']['azienda']}")
    tabs = st.tabs(list(DOMANDE_MATRICE.keys()))
    current_results = {}
    
    for i, area in enumerate(DOMANDE_MATRICE.keys()):
        with tabs[i]:
            st.subheader(f"Parametri {area}")
            scores = []
            for j, (q, opts) in enumerate(DOMANDE_MATRICE[area]):
                choice = st.radio(f"**{j+1}. {q}**", [1,2,3,4,5], 
                                  format_func=lambda x: f"{x}: {opts[x-1]}", 
                                  key=f"q_{pi}_{area}_{j}")
                scores.append(choice)
            current_results[area] = sum(scores) / 6
            
    if st.button("Salva e Analizza Risultati", use_container_width=True):
        st.session_state.clienti[pi]['assessments'].append({
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "punteggi": current_results,
            "report_ai": ""
        })
        st.session_state.page = "Valutazione"
        st.rerun()

elif st.session_state.page == "Valutazione":
    pi = st.session_state.current_piva
    if not pi or not st.session_state.clienti[pi]['assessments']:
        st.warning("Completa prima il questionario.")
        st.stop()
        
    cl = st.session_state.clienti[pi]
    ass = cl['assessments'][-1]
    bench = BENCHMARK_DATI[cl['info']['settore']]
    
    st.title(f"📊 Dashboard Strategica: {cl['info']['azienda']}")
    
    categories = list(ass['punteggi'].keys())
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=list(ass['punteggi'].values()), theta=categories, fill='toself', name='Situazione Azienda', line_color='#E63946'))
    fig.add_trace(go.Scatterpolar(r=[bench[k] for k in categories], theta=categories, name='Benchmark Settore', line_color='#1D3557', line_dash='dash'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), height=600)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("🤖 Generatore di Strategia NextaHub (Powered by Gemini)")
    
    if not ass['report_ai']:
        if st.button("✨ Genera Report con Intelligenza Artificiale", use_container_width=True):
            with st.spinner("L'intelligenza Gemini sta elaborando la roadmap personalizzata..."):
                ass['report_ai'] = genera_report_ai(ass['punteggi'], cl['info'], bench)
                st.rerun()
    else:
        st.markdown(ass['report_ai'])
        st.download_button("📥 Scarica Report PDF (MD)", ass['report_ai'], file_name=f"Strategia_{cl['info']['azienda']}.md")

elif st.session_state.page == "Archivio":
    st.title("📁 Archivio Storico Clienti")
    if not st.session_state.clienti:
        st.info("L'archivio è vuoto.")
    else:
        for p, d in st.session_state.clienti.items():
            with st.expander(f"🏢 {d['info']['azienda']} (P.IVA: {p})"):
                for i, a in enumerate(d['assessments']):
                    if st.button(f"Visualizza Analisi del {a['data']}", key=f"arch_{p}_{i}"):
                        st.session_state.current_piva = p
                        st.session_state.page = "Valutazione"
                        st.rerun()
