import streamlit as st
import plotly.graph_objects as go
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="NextaHub Strategic Suite", layout="wide", initial_sidebar_state="expanded")

# --- BENCHMARK DI SETTORE ---
BENCHMARK_DATI = {
    "Manifatturiero": {"Strategia & Controllo": 3.2, "Digitalizzazione": 2.8, "Gestione HR": 3.0, "Finanza & Investimenti": 3.5, "Sostenibilità (ESG)": 2.5, "Protezione Legale": 3.8, "Sicurezza sul Lavoro": 4.5, "Standard & Qualità": 4.0, "Sviluppo Competenze": 2.9},
    "IT & Digital": {"Strategia & Controllo": 3.8, "Digitalizzazione": 4.5, "Gestione HR": 4.0, "Finanza & Investimenti": 3.2, "Sostenibilità (ESG)": 3.0, "Protezione Legale": 3.5, "Sicurezza sul Lavoro": 3.0, "Standard & Qualità": 3.5, "Sviluppo Competenze": 4.2},
    "Servizi": {"Strategia & Controllo": 3.0, "Digitalizzazione": 3.5, "Gestione HR": 3.5, "Finanza & Investimenti": 3.0, "Sostenibilità (ESG)": 2.8, "Protezione Legale": 3.2, "Sicurezza sul Lavoro": 3.5, "Standard & Qualità": 3.0, "Sviluppo Competenze": 3.5},
    "Edilizia": {"Strategia & Controllo": 2.5, "Digitalizzazione": 2.2, "Gestione HR": 2.8, "Finanza & Investimenti": 2.8, "Sostenibilità (ESG)": 2.2, "Protezione Legale": 3.0, "Sicurezza sul Lavoro": 4.8, "Standard & Qualità": 3.2, "Sviluppo Competenze": 2.5}
}

# --- INIZIALIZZAZIONE STATI ---
if 'page' not in st.session_state: st.session_state.page = "Anagrafica"
if 'clienti' not in st.session_state: st.session_state.clienti = {}
if 'current_client_piva' not in st.session_state: st.session_state.current_client_piva = None
if 'rev_index' not in st.session_state: st.session_state.rev_index = -1 

# --- DATABASE INTEGRALE 54 DOMANDE ---
DOMANDE_MATRICE = {
    'Strategia & Controllo': [
        ("Esiste un Business Plan triennale?", {1: "Assente", 2: "Solo budget", 3: "12 mesi", 4: "Triennale", 5: "Revisione trimestrale"}),
        ("Monitorate KPI (margini, EBITDA)?", {1: "No", 2: "Solo bilancio", 3: "Excel", 4: "Dashboard", 5: "BI Real-time"}),
        ("Ruoli e responsabilità sono chiari?", {1: "No", 2: "Verbali", 3: "Organigramma base", 4: "Mansionari", 5: "Struttura manageriale"}),
        ("Analizzate i competitor regolarmente?", {1: "Mai", 2: "Raro", 3: "Annuale", 4: "Sistematico", 5: "Data-driven"}),
        ("Il titolare delega l'operatività?", {1: "No", 2: "Minimo", 3: "Prime deleghe", 4: "Autonomia", 5: "Delega totale"}),
        ("Esiste un piano di passaggio generazionale?", {1: "No", 2: "Discusso", 3: "Consapevolezza", 4: "Bozza", 5: "Formalizzato"})
    ],
    'Digitalizzazione': [
        ("Il gestionale ERP copre tutta l'azienda?", {1: "No", 2: "Base", 3: "Settoriale", 4: "Integrato", 5: "Cloud/Evoluto"}),
        ("Grado di digitalizzazione processi (Paperless)?", {1: "Carta", 2: "Misto", 3: "Digitale base", 4: "Digitale", 5: "Automazione"}),
        ("Usate un CRM per i clienti?", {1: "No", 2: "Contatti", 3: "Offerte", 4: "Integrato", 5: "Marketing Automation"}),
        ("Avete protocolli di Cybersecurity?", {1: "No", 2: "Minimo", 3: "Backup", 4: "Audit", 5: "Standard massimi"}),
        ("Investite in Digital Marketing?", {1: "No", 2: "Sito", 3: "Social", 4: "Lead Gen", 5: "Omnicanale"}),
        ("Usate strumenti di AI nei processi?", {1: "No", 2: "Test", 3: "Base", 4: "Operativa", 5: "AI-driven"})
    ],
    'Gestione HR': [
        ("Esiste un piano Welfare?", {1: "No", 2: "Minimo", 3: "Base", 4: "Strutturato", 5: "Evoluto"}),
        ("Misurate le performance dei dipendenti?", {1: "No", 2: "Informale", 3: "Annuale", 4: "MBO", 5: "Feedback continuo"}),
        ("Attrattività per nuovi talenti?", {1: "Bassa", 2: "Passiva", 3: "Networking", 4: "Branding", 5: "Top Employer"}),
        ("Monitorate il clima aziendale?", {1: "No", 2: "Raro", 3: "Annuale", 4: "Sistematico", 5: "Benessere core"}),
        ("Piani di formazione continua?", {1: "No", 2: "Obbligo", 3: "Sporadica", 4: "Annuale", 5: "Academy"}),
        ("Smart working o flessibilità?", {1: "No", 2: "Eccezioni", 3: "Flessibilità", 4: "Policy", 5: "Per obiettivi"})
    ],
    'Finanza & Investimenti': [
        ("Previsioni di tesoreria (Cash Flow)?", {1: "No", 2: "Settimana", 3: "Mensile", 4: "Trimestre", 5: "Real-time"}),
        ("Sfruttate la Finanza Agevolata?", {1: "No", 2: "Raro", 3: "Occasionale", 4: "Pianificato", 5: "Strategico"}),
        ("Monitorate il rating bancario?", {1: "No", 2: "Vago", 3: "Annuale", 4: "Costante", 5: "Ottimizzazione"}),
        ("Marginalità per prodotto/commessa?", {1: "No", 2: "Globale", 3: "Stima", 4: "Analitica", 5: "Predittiva"}),
        ("Gestione recupero crediti?", {1: "No", 2: "Reattiva", 3: "Procedura", 4: "Assicurazione", 5: "Sistemica"}),
        ("Investimenti in R&S sul fatturato?", {1: "0%", 2: "1%", 3: "2%", 4: "5%", 5: ">5%"})
    ],
    'Sostenibilità (ESG)': [
        ("Conoscenza criteri ESG?", {1: "No", 2: "Vaga", 3: "Base", 4: "Integrazione", 5: "Bilancio ESG"}),
        ("Riduzione impatto ambientale?", {1: "No", 2: "Rifiuti", 3: "Energia", 4: "ISO 14001", 5: "Carbon Neutral"}),
        ("Inclusione e parità di genere?", {1: "No", 2: "Base", 3: "Azioni", 4: "Policy", 5: "Certificazione"}),
        ("Etica e trasparenza (Governance)?", {1: "No", 2: "Base", 3: "Codice Etico", 4: "Compliance", 5: "Trasparenza"}),
        ("Valutazione ESG dei fornitori?", {1: "No", 2: "Raro", 3: "Questionari", 4: "Audit", 5: "Partnership"}),
        ("Certificazioni Green?", {1: "No", 2: "Studio", 3: "Base", 4: "Multiple", 5: "Rating Gold/B-Corp"})
    ],
    'Protezione Legale': [
        ("Modello 231 implementato?", {1: "No", 2: "In corso", 3: "Adottato", 4: "Aggiornato", 5: "ODV attivo"}),
        ("Conformità GDPR?", {1: "No", 2: "Minima", 3: "Conforme", 4: "Audit", 5: "DPO presente"}),
        ("Contrattualistica aggiornata?", {1: "Standard", 2: "Base", 3: "Revisionata", 4: "Ad hoc", 5: "Legal Management"}),
        ("Tutela marchi e brevetti (IP)?", {1: "No", 2: "Marchio", 3: "Protetto", 4: "Attivo", 5: "Asset strategico"}),
        ("Sistema recupero crediti legale?", {1: "No", 2: "Sporadico", 3: "Protocollo", 4: "Interno", 5: "Massima efficienza"}),
        ("Polizze D&O o Cyber Risk?", {1: "No", 2: "Base", 3: "RC", 4: "D&O/Cyber", 5: "Broker dedicato"})
    ],
    'Sicurezza sul Lavoro': [
        ("DVR aggiornato e dinamico?", {1: "No", 2: "Vecchio", 3: "Base", 4: "Digitale", 5: "Evolutivo"}),
        ("Formazione sicurezza tracciata?", {1: "No", 2: "Parziale", 3: "Sì", 4: "Digitale", 5: "Zero scadenze"}),
        ("Sorveglianza sanitaria regolare?", {1: "No", 2: "Base", 3: "Sì", 4: "Monitorata", 5: "Eccellenza"}),
        ("Consegna DPI tracciata?", {1: "No", 2: "Verbale", 3: "Sì", 4: "Digitale", 5: "Automatico"}),
        ("Piano manutenzione impianti?", {1: "No", 2: "Guasto", 3: "Base", 4: "Programmata", 5: "Predittiva"}),
        ("Analisi dei 'Near Miss'?", {1: "No", 2: "Raro", 3: "Gravi", 4: "Sempre", 5: "Cultura prevenzione"})
    ],
    'Standard & Qualità': [
        ("ISO 9001 reale e attiva?", {1: "No", 2: "Formale", 3: "Sì", 4: "Ottima", 5: "Eccellenza"}),
        ("Processi mappati e scritti?", {1: "No", 2: "Minimo", 3: "Core", 4: "Tutti", 5: "Kaizen"}),
        ("Audit interni regolari?", {1: "No", 2: "Raro", 3: "Annuale", 4: "Sempre", 5: "Auto-miglioramento"}),
        ("Misurazione Customer Satisfaction?", {1: "No", 2: "Reclami", 3: "Sondaggi", 4: "NPS", 5: "Customer Centric"}),
        ("Qualifica fornitori (KPI)?", {1: "No", 2: "Base", 3: "Sì", 4: "Monitorati", 5: "Partnership"}),
        ("Gestione Non Conformità?", {1: "No", 2: "Base", 3: "Sì", 4: "Analisi Cause", 5: "Risoluzione Radice"})
    ],
    'Sviluppo Competenze': [
        ("Analisi gap competenze?", {1: "No", 2: "Vaga", 3: "Base", 4: "Analitica", 5: "Strategica"}),
        ("Uso fondi interprofessionali?", {1: "No", 2: "Iscritti", 3: "Raro", 4: "Sempre", 5: "Massimizzazione"}),
        ("Academy interna/Condivisione?", {1: "No", 2: "Minimo", 3: "Tutor", 4: "Manuali", 5: "Academy"}),
        ("Formazione Leadership/Manager?", {1: "No", 2: "Minimo", 3: "Soft Skills", 4: "Coaching", 5: "Leadership diffusa"}),
        ("Piani di carriera definiti?", {1: "No", 2: "Vaghi", 3: "Sì", 4: "Chiariti", 5: "Meritocrazia"}),
        ("Apertura all'innovazione (Mindset)?", {1: "No", 2: "Resistenza", 3: "Base", 4: "Aperti", 5: "Proattivi"})
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
            indirizzo = st.text_input("Indirizzo Aziendale (Via, Civico, CAP, Città)")
        with col2:
            settore = st.selectbox("Settore", list(BENCHMARK_DATI.keys()))
            regione = st.selectbox("Regione", ["Lombardia", "Veneto", "Emilia-Romagna", "Piemonte", "Lazio", "Campania", "Altro"])
        
        if st.form_submit_button("Salva Cliente"):
            if azienda and piva:
                st.session_state.current_client_piva = piva
                if piva not in st.session_state.clienti:
                    st.session_state.clienti[piva] = {
                        "anagrafica": {
                            "azienda": azienda, 
                            "piva": piva, 
                            "indirizzo": indirizzo,
                            "settore": settore, 
                            "regione": regione
                        }, 
                        "revisioni": []
                    }
                else:
                    # Aggiorna anagrafica esistente
                    st.session_state.clienti[piva]["anagrafica"].update({
                        "azienda": azienda, "indirizzo": indirizzo, "settore": settore, "regione": regione
                    })
                st.success("Anagrafica salvata!")
                go_to("Questionario")
                st.rerun()

# --- PAGINA 2: QUESTIONARIO ---
elif st.session_state.page == "Questionario":
    piva = st.session_state.current_client_piva
    if not piva: st.warning("Seleziona o crea un cliente in Anagrafica.")
    else:
        st.header(f"📝 Nuova Revisione: {st.session_state.clienti[piva]['anagrafica']['azienda']}")
        scores = {}
        tabs = st.tabs(list(DOMANDE_MATRICE.keys()))
        for i, area in enumerate(DOMANDE_MATRICE.keys()):
            with tabs[i]:
                p_area = []
                for j, (q, opts) in enumerate(DOMANDE_MATRICE[area]):
                    val = st.radio(q, options=[1,2,3,4,5], format_func=lambda x: f"{x}: {opts[x]}", key=f"q_{piva}_{area}_{j}_{len(st.session_state.clienti[piva]['revisioni'])}")
                    p_area.append(val)
                scores[area] = sum(p_area)/len(p_area)
        
        if st.button("Salva Assessment come Revisione"):
            st.session_state.clienti[piva]['revisioni'].append({
                "data": datetime.now().strftime("%d/%m/%Y %H:%M"), 
                "punteggi": scores, 
                "analisi_ai": ""
            })
            st.session_state.rev_index = len(st.session_state.clienti[piva]['revisioni']) - 1
            go_to("Valutazione")
            st.rerun()

# --- PAGINA 3: RADAR & AI ---
elif st.session_state.page == "Valutazione":
    piva = st.session_state.current_client_piva
    if not piva or not st.session_state.clienti[piva]['revisioni']: st.warning("Nessun dato disponibile.")
    else:
        cliente = st.session_state.clienti[piva]
        rev = cliente['revisioni'][st.session_state.rev_index]
        st.header(f"📊 Report Revisione: {rev['data']}")
        st.caption(f"Azienda: {cliente['anagrafica']['azienda']} | Sede: {cliente['anagrafica']['indirizzo']}")
        
        # Radar
        settore = cliente['anagrafica']['settore']
        categorie = list(rev['punteggi'].keys())
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=list(rev['punteggi'].values()), theta=categorie, fill='toself', name='Cliente', line_color='#e63946'))
        fig.add_trace(go.Scatterpolar(r=[BENCHMARK_DATI[settore].get(c, 3.0) for c in categorie], theta=categorie, name='Benchmark Settore', line_color='gray', line_dash='dash'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), height=500)
        st.plotly_chart(fig, use_container_width=True)

        if not rev['analisi_ai']:
            if st.button("🤖 Genera Analisi AI"):
                try:
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    model_id = next((m for m in models if "flash" in m), models[0])
                    model = genai.GenerativeModel(model_id)
                    
                    prompt = f"Analizza l'azienda {cliente['anagrafica']['azienda']} in {cliente['anagrafica']['indirizzo']}. Settore {settore}. Punteggi: {rev['punteggi']}. Benchmark: {BENCHMARK_DATI[settore]}. Fornisci analisi dei gap e 3 consigli strategici."
                    
                    with st.spinner("L'AI sta elaborando..."):
                        res = model.generate_content(prompt)
                        rev['analisi_ai'] = res.text
                        st.rerun()
                except Exception as e: st.error(f"Errore AI: {e}")
        else:
            st.markdown("### Report Strategico AI")
            st.markdown(rev['analisi_ai'])

# --- PAGINA 4: SERVIZI ---
elif st.session_state.page == "Servizi":
    piva = st.session_state.current_client_piva
    if piva and st.session_state.clienti[piva]['revisioni']:
        rev = st.session_state.clienti[piva]['revisioni'][st.session_state.rev_index]
        settore = st.session_state.clienti[piva]['anagrafica']['settore']
        st.header("💼 Urgenze e Servizi Consigliati")
        c1, c2, c3 = st.columns(3)
        for area, s in rev['punteggi'].items():
            b = BENCHMARK_DATI[settore].get(area, 3.0)
            if s < 2.5: c1.error(f"🚨 **{area}**: Priorità Alta")
            elif s < b: c2.warning(f"⚠️ **{area}**: Da migliorare")
            else: c3.success(f"✅ **{area}**: In linea")

# --- PAGINA 5: ARCHIVIO ---
elif st.session_state.page == "Lista":
    st.header("📁 Archivio Storico Clienti")
    if not st.session_state.clienti: st.info("Nessun cliente registrato.")
    for p, d in st.session_state.clienti.items():
        with st.expander(f"🏢 {d['anagrafica']['azienda']} (P.IVA: {p})"):
            st.write(f"📍 **Indirizzo:** {d['anagrafica'].get('indirizzo', 'Non specificato')}")
            st.write(f"🏭 **Settore:** {d['anagrafica']['settore']} | 📍 **Regione:** {d['anagrafica']['regione']}")
            st.markdown("---")
            st.write("**Revisioni disponibili:**")
            for idx, r in enumerate(d['revisioni']):
                col_data, col_btn = st.columns([3, 1])
                col_data.write(f"Analisi del {r['data']}")
                if col_btn.button("Carica", key=f"v_{p}_{idx}"):
                    st.session_state.current_client_piva = p
                    st.session_state.rev_index = idx
                    go_to("Valutazione")
                    st.rerun()
            
            st.markdown("---")
            if st.button("➕ Nuova Revisione per questo cliente", key=f"n_{p}"):
                st.session_state.current_client_piva = p
                go_to("Questionario")
                st.rerun()
