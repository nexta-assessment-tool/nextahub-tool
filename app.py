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

# --- 2. DATABASE E COSTANTI ---
if 'db_clienti' not in st.session_state:
    st.session_state.db_clienti = {}
if 'page' not in st.session_state:
    st.session_state.page = "Anagrafica"
if 'current_piva' not in st.session_state:
    st.session_state.current_piva = None

SETTORI = ["Agroalimentare", "Moda e Tessile", "Arredo e Design", "Meccanica e Automazione", "Metallurgia", "Automotive", "Chimico e Farmaceutico", "Energia e Utilities", "Costruzioni ed Edilizia", "Elettronica", "Gomma e Materie Plastiche", "Carta e Stampa", "ICT e Digitale", "Logistica e Trasporti", "Turismo e Ristorazione", "Bancario e Assicurativo", "Sanità"]
REGIONI = ["Abruzzo", "Basilicata", "Calabria", "Campania", "Emilia-Romagna", "Friuli-Venezia Giulia", "Lazio", "Liguria", "Lombardia", "Marche", "Molise", "Piemonte", "Puglia", "Sardegna", "Sicilia", "Toscana", "Trentino-Alto Adige", "Umbria", "Valle d'Aosta", "Veneto"]

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
        validi = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        scelto = next((x for x in ["models/gemini-1.5-flash", "models/gemini-1.5-pro", "models/gemini-pro"] if x in validi), validi[0])
        model = genai.GenerativeModel(scelto)
        
        prompt = f"""
        Agisci come Senior Partner e Consultant di NextaHub. Il tuo obiettivo è convertire questa analisi in un mandato di consulenza.
        
        CLIENTE: {dati_cliente['azienda']} | SETTORE: {dati_cliente['settore']} | REGIONE: {dati_cliente['regione']}
        CONSULENTE NEXTA: {dati_cliente['commerciale']}

        SCORE RILEVATI (scala 1-5): {json.dumps(punteggi, indent=2)}
        
        STRUTTURA DEL REPORT:
        1. TABELLA COMPARATIVA SCORE VS BENCHMARK (Regione: {dati_cliente['regione']}).
        2. ANALISI DEI GAP E SOLUZIONI NEXTAHUB: Dividi i gap per URGENZA. Per ogni gap spiega il rischio di inazione e il beneficio del servizio NextaHub consigliato.
        3. ROADMAP DI TRASFORMAZIONE (12-24 MESI).
        4. RESOCONTO CONCLUSIVO E SERVIZI PRIORITARI: Identifica max 3 servizi. Uno deve essere di FINANZA AGEVOLATA/FORMAZIONE FINANZIATA per spiegare come finanziare gli altri due.
        
        FIRMA: "Analisi a cura di: {dati_cliente['commerciale']} - Senior Consultant NextaHub"
        """
        return model.generate_content(prompt).text
    except Exception as e:
        return f"❌ Errore AI: {str(e)}"

# --- 5. LOGICA NAVIGAZIONE ---
with st.sidebar:
    st.image(LOGO_URL, width=180)
    st.markdown("---")
    if st.button("🏢 1. Nuova Anagrafica"): st.session_state.page = "Anagrafica"
    if st.button("📝 2. Assessment Corrente"): st.session_state.page = "Questionario"
    if st.button("📊 3. Report & AI"): st.session_state.page = "Valutazione"
    if st.button("🗄️ 4. Archivio Valutazioni"): st.session_state.page = "Archivio"

# PAGINA 1: ANAGRAFICA
if st.session_state.page == "Anagrafica":
    st.title("🏢 Anagrafica Cliente")
    with st.form("form_anag"):
        c1, c2 = st.columns(2)
        with c1:
            rs = st.text_input("Ragione Sociale *")
            pi = st.text_input("Partita IVA *")
            comune = st.text_input("Comune *")
            settore = st.selectbox("Settore Business *", SETTORI)
        with c2:
            regione = st.selectbox("Regione *", REGIONI)
            comm = st.text_input("Riferimento Commerciale Nexta *")
            rif_az = st.text_input("Rif. Aziendale (Contatto)")
        
        if st.form_submit_button("➡️ Avvia Assessment"):
            if rs and pi and settore and comm:
                st.session_state.current_piva = pi
                if pi not in st.session_state.db_clienti:
                    st.session_state.db_clienti[pi] = {
                        "info": {"azienda": rs, "piva": pi, "settore": settore, "regione": regione, "comune": comune, "commerciale": comm, "contatto": rif_az},
                        "storia": []
                    }
                st.session_state.page = "Questionario"
                st.rerun()
            else: st.error("Compila i campi obbligatori (*)")

# PAGINA 2: QUESTIONARIO (54 DOMANDE)
elif st.session_state.page == "Questionario":
    pi = st.session_state.get('current_piva')
    if not pi: st.warning("Seleziona o crea un cliente"); st.stop()
    cl = st.session_state.db_clienti[pi]
    st.title(f"📝 Assessment: {cl['info']['azienda']}")
    
    tabs = st.tabs(list(DOMANDE_MATRICE.keys()))
    temp_scores = {}
    
    for i, area in enumerate(DOMANDE_MATRICE.keys()):
        with tabs[i]:
            scores = []
            for j, (dom, opt, lim) in enumerate(DOMANDE_MATRICE[area]):
                if lim is None or cl['info']['settore'] in lim:
                    s = st.radio(f"**{dom}**", [1,2,3,4,5], format_func=lambda x: f"{x}: {opt[x-1]}", key=f"{pi}_{area}_{j}_{len(cl['storia'])}")
                    scores.append(s)
            temp_scores[area] = sum(scores)/len(scores) if scores else 3.0
            
    if st.button("📊 Genera Report"):
        cl['storia'].append({
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "punteggi": temp_scores,
            "report": ""
        })
        st.session_state.page = "Valutazione"
        st.rerun()

# PAGINA 3: VALUTAZIONE (LOGO CENTRATO + GRAFICI COLORATI)
elif st.session_state.page == "Valutazione":
    pi = st.session_state.get('current_piva')
    if not pi or not st.session_state.db_clienti[pi]['storia']: st.warning("Dati mancanti"); st.stop()
    
    cl = st.session_state.db_clienti[pi]
    ass = cl['storia'][-1]
    
    # 1. Logo Centrato
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2: st.image(LOGO_URL, use_container_width=True)
    
    st.markdown(f"<h1 style='text-align: center;'>Analisi Strategica: {cl['info']['azienda']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'><b>Data:</b> {ass['data']} | <b>Analista:</b> {cl['info']['commerciale']}</p>", unsafe_allow_html=True)

    # 2. Grafici (Radar e Barre Colorate)
    bench_val = {"Strategia & Controllo": 3.5, "Digitalizzazione": 3.2, "Gestione HR": 3.4, "Finanza & Investimenti": 3.0, "Sostenibilità (ESG)": 3.1, "Protezione Legale": 3.8, "Sicurezza sul Lavoro": 4.2, "Standard & Qualità": 3.9, "Sviluppo Competenze": 3.3}
    
    c1, c2 = st.columns(2)
    categories = list(ass['punteggi'].keys())
    values = list(ass['punteggi'].values())
    
    with c1:
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', name='Azienda', line_color='#E63946'))
        fig_radar.add_trace(go.Scatterpolar(r=[bench_val[k] for k in categories], theta=categories, name='Benchmark', line_color='#1D3557'))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=True)
        st.plotly_chart(fig_radar, use_container_width=True)

    with c2:
        diffs = [ass['punteggi'][cat] - bench_val[cat] for cat in categories]
        colors = []
        for d in diffs:
            if d >= 0: colors.append('#2D6A4F') # Verde
            elif d > -0.5: colors.append('#FFD60A') # Giallo
            elif d > -1.5: colors.append('#FB8500') # Arancio
            else: colors.append('#AE2012') # Rosso
        
        fig_bar = go.Figure(go.Bar(x=diffs, y=categories, orientation='h', marker_color=colors))
        fig_bar.update_layout(xaxis_title="Gap vs Benchmark", yaxis_autorange="reversed")
        st.plotly_chart(fig_bar, use_container_width=True)

    if st.button("🚀 Genera Analisi Strategica AI"):
        with st.spinner("L'AI NextaHub sta elaborando..."):
            ass['report'] = analizza_con_gemini(cl['info'], ass['punteggi'])
            st.rerun()
            
    if ass['report']:
        st.markdown("---")
        st.markdown(ass['report'])
        st.markdown(f"\n\n**Analisi a cura di:** {cl['info']['commerciale']} - Senior Consultant NextaHub")

# PAGINA 4: ARCHIVIO (Ripesca, Ricarica e Confronta)
elif st.session_state.page == "Archivio":
    st.title("🗄️ Archivio Valutazioni NextaHub")
    if not st.session_state.db_clienti:
        st.info("Nessuna valutazione in archivio.")
    else:
        for piva, dati in st.session_state.db_clienti.items():
            with st.expander(f"🏢 {dati['info']['azienda']} (P.IVA: {piva})"):
                st.write(f"**Referente Nexta:** {dati['info']['commerciale']}")
                for idx, sessione in enumerate(dati['storia']):
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"📅 Valutazione del {sessione['data']}")
                    if c2.button(f"🔎 Visualizza Report", key=f"view_{piva}_{idx}"):
                        # Spostiamo l'assessment selezionato in fondo per farlo vedere come "ultimo"
                        selected = dati['storia'].pop(idx)
                        dati['storia'].append(selected)
                        st.session_state.current_piva = piva
                        st.session_state.page = "Valutazione"
                        st.rerun()
                if st.button(f"➕ Nuova Analisi per questo cliente", key=f"new_an_{piva}"):
                    st.session_state.current_piva = piva
                    st.session_state.page = "Questionario"
                    st.rerun()
