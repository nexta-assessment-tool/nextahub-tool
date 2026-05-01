import streamlit as st
import plotly.graph_objects as go
import google.generativeai as genai
from datetime import datetime
import json

# --- CONFIGURAZIONE API GOOGLE GEMINI ---
API_KEY = "IL_TUO_CODICE_API_QUI" 

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="NextaHub Strategic Suite v3.0", layout="wide", initial_sidebar_state="expanded")

# --- DATABASE BENCHMARK DI SETTORE (Dati Medi Nazionali) ---
BENCHMARK_DATI = {
    "Agroalimentare": {"Strategia & Controllo": 3.4, "Digitalizzazione": 3.0, "Gestione HR": 3.1, "Finanza & Investimenti": 3.2, "Sostenibilità (ESG)": 3.8, "Protezione Legale": 3.5, "Sicurezza sul Lavoro": 4.2, "Standard & Qualità": 4.5, "Sviluppo Competenze": 3.0},
    "Meccanica": {"Strategia & Controllo": 3.5, "Digitalizzazione": 3.8, "Gestione HR": 3.4, "Finanza & Investimenti": 3.6, "Sostenibilità (ESG)": 3.0, "Protezione Legale": 3.5, "Sicurezza sul Lavoro": 4.5, "Standard & Qualità": 4.2, "Sviluppo Competenze": 3.8},
    "Moda/Luxury": {"Strategia & Controllo": 3.6, "Digitalizzazione": 3.8, "Gestione HR": 3.5, "Finanza & Investimenti": 3.4, "Sostenibilità (ESG)": 4.0, "Protezione Legale": 4.2, "Sicurezza sul Lavoro": 3.5, "Standard & Qualità": 4.0, "Sviluppo Competenze": 3.7},
    "ICT/Digitale": {"Strategia & Controllo": 4.0, "Digitalizzazione": 4.8, "Gestione HR": 4.2, "Finanza & Investimenti": 3.6, "Sostenibilità (ESG)": 3.5, "Protezione Legale": 4.0, "Sicurezza sul Lavoro": 3.0, "Standard & Qualità": 3.8, "Sviluppo Competenze": 4.5},
    "Edilizia": {"Strategia & Controllo": 2.8, "Digitalizzazione": 2.5, "Gestione HR": 2.9, "Finanza & Investimenti": 3.0, "Sostenibilità (ESG)": 2.7, "Protezione Legale": 3.4, "Sicurezza sul Lavoro": 4.7, "Standard & Qualità": 3.4, "Sviluppo Competenze": 2.8},
    "Servizi/Consulenza": {"Strategia & Controllo": 3.8, "Digitalizzazione": 4.0, "Gestione HR": 3.9, "Finanza & Investimenti": 3.3, "Sostenibilità (ESG)": 3.5, "Protezione Legale": 4.0, "Sicurezza sul Lavoro": 3.5, "Standard & Qualità": 4.2, "Sviluppo Competenze": 4.0},
    "Logistica/Trasporti": {"Strategia & Controllo": 3.2, "Digitalizzazione": 3.9, "Gestione HR": 3.1, "Finanza & Investimenti": 3.0, "Sostenibilità (ESG)": 3.3, "Protezione Legale": 3.7, "Sicurezza sul Lavoro": 4.4, "Standard & Qualità": 3.9, "Sviluppo Competenze": 3.2}
}

# --- CATALOGO SERVIZI NEXTAHUB (Istruzioni per l'Agente) ---
SERVIZI_NEXTA = {
    "Strategia & Controllo": "Dashboard KPI, Passaggio Generazionale, Temporary Management e Revisione Processi Aziendali.",
    "Digitalizzazione": "Piano Transizione 5.0, Cybersecurity, E-commerce avanzato e Integrazione AI nei processi produttivi.",
    "Gestione HR": "Piani di Welfare Aziendale, Academy interna, Sistemi di MBO e Ricerca/Selezione Talenti.",
    "Finanza & Investimenti": "Scouting Finanza Agevolata (Bandi Regionali/Nazionali), Crediti d'imposta R&S e Ottimizzazione Rating.",
    "Sostenibilità (ESG)": "Bilancio di Sostenibilità (ESG), Certificazione Parità di Genere, ISO 14001 e Carbon Footprint.",
    "Protezione Legale": "Modello 231, Compliance GDPR, Contrattualistica Internazionale e Tutela del Patrimonio.",
    "Sicurezza sul Lavoro": "DVR Dinamico, Medicina del Lavoro, Formazione Finanziata 81/08 e Gestione Cantieri.",
    "Standard & Qualità": "Certificazioni ISO (9001, 45001, 27001) e Audit di qualità sui fornitori.",
    "Sviluppo Competenze": "Formazione tramite Fondi Interprofessionali, Coaching Manageriale e Piani di Reskilling tecnico."
}

# --- MATRICE COMPLETA 54 DOMANDE ---
# Ogni area ha 6 domande specifiche = 54 totali
DOMANDE_MATRICE = {
    'Strategia & Controllo': [
        ("Piano Strategico", ["Nessun piano definito", "Obiettivi solo verbali", "Budget annuale presente", "Piano triennale scritto", "Piano dinamico con revisione trimestrale"]),
        ("Monitoraggio KPI", ["Assente", "Solo bilancio annuale", "Excel aggiornato saltuariamente", "Dashboard mensile", "Business Intelligence real-time"]),
        ("Organigramma e Ruoli", ["Tutto in testa al titolare", "Ruoli confusi", "Schema base presente", "Organigramma definito", "Manager autonomi con deleghe"]),
        ("Analisi Competitor", ["Mai fatta", "Rara e informale", "Annuale su fatturati", "Monitoraggio costante", "Benchmarking data-driven"]),
        ("Sistema di Delega", ["Nessuna", "Solo compiti semplici", "Capi area operativi", "Responsabilità di budget", "Direzione generale autonoma"]),
        ("Passaggio Generazionale", ["Argomento tabù", "Discussioni informali", "Successori individuati", "Piano di affiancamento", "Formalizzato con patti di famiglia"])
    ],
    'Digitalizzazione': [
        ("Infrastruttura IT", ["Obsolescente", "Base (Mail/Office)", "Server locale gestito", "Cloud ibrido", "Full Cloud/SaaS"]),
        ("ERP/Gestionale", ["Solo fatturazione", "Contabilità base", "Settoriale specifico", "Integrato (Produzione/Magazzino)", "Ecosistema interconnesso"]),
        ("Processi Paperless", ["100% Cartaceo", "Pochi PDF", "Misto (Archiviazione digitale)", "Quasi tutto digitale", "100% digitale/Workflow automatici"]),
        ("Cybersecurity", ["Solo Antivirus free", "Backup saltuari", "Firewall e Backup Cloud", "Policy e Audit regolari", "SOC 24/7 e Disaster Recovery"]),
        ("Presenza Web/Digital Marketing", ["Assente", "Sito vetrina statico", "Sito aggiornato e Social", "Strategia ADS e SEO", "Lead generation automatizzata"]),
        ("Innovazione (AI/IoT)", ["Nessuna", "Uso sporadico (es. ChatGPT)", "Sperimentazione in un'area", "Integrata nei processi", "Business Model AI-driven"])
    ],
    'Gestione HR': [
        ("Welfare Aziendale", ["Assente", "Rimborsi spese minimi", "Convenzioni base", "Piattaforma Welfare", "Benefit evoluti e personalizzati"]),
        ("Sistemi di Valutazione", ["Nessuno", "Basata su sensazioni", "Colloquio annuale", "MBO correlati a KPI", "Feedback continuo 360°"]),
        ("Retention e Turnover", ["Fuga di talenti", "Turnover nella media", "Bonus sporadici", "Employer Branding attivo", "Azienda 'Top Employer'"]),
        ("Clima Aziendale", ["Tensioni frequenti", "Ignorato", "Rilevato saltuariamente", "Indagine annuale", "Monitoraggio continuo del benessere"]),
        ("Piani di Formazione", ["Solo obbligatoria", "Corsi tecnici rari", "Budget annuo definito", "Piani di crescita individuali", "Academy aziendale interna"]),
        ("Flessibilità e Smart Working", ["Presenza rigida", "Permessi rari", "Flessibilità oraria", "Smart working strutturato", "Lavoro per obiettivi/Anywhere"])
    ],
    'Finanza & Investimenti': [
        ("Pianificazione Finanziaria", ["Nessuna", "Saldo banca", "Cash flow mensile", "Previsionale a 6 mesi", "Software di tesoreria predittiva"]),
        ("Accesso Finanza Agevolata", ["Mai utilizzata", "Rara/Casuale", "Utilizzata per bandi semplici", "Monitoraggio attivo", "Pianificazione strategica bandi"]),
        ("Rating Bancario", ["Sconosciuto", "Vago", "Controllato annualmente", "Monitorato trimestralmente", "Ottimizzazione attiva del merito creditizio"]),
        ("Analisi Marginalità", ["Solo utile a fine anno", "Stime per prodotto", "Calcolo per commessa", "Analisi analitica in tempo reale", "Analisi predittiva margini"]),
        ("Gestione Credito", ["Reattiva (si aspetta)", "Solleciti sporadici", "Procedura scritta", "Ufficio recupero crediti", "Assicurazione credito e automazione"]),
        ("Investimenti in R&S", ["0%", "Solo reattiva", "1-2% del fatturato", "5% del fatturato", ">5% con brevetti/IP"])
    ],
    'Sostenibilità (ESG)': [
        ("Cultura ESG", ["Sconosciuta", "Solo obblighi di legge", "Prime iniziative isolate", "Integrazione nel piano industriale", "Rating ESG certificato"]),
        ("Impatto Ambientale", ["Nessuna misura", "Raccolta differenziata base", "Monitoraggio consumi", "Carbon Footprint calcolata", "Target Net Zero e ISO 14001"]),
        ("Inclusione e Diversità", ["Nessuna policy", "Sensibilità generica", "Presenza donne in ruoli chiave", "Policy scritte e monitorate", "Certificazione Parità di Genere"]),
        ("Etica e Trasparenza", ["Nessuna", "Leggi base", "Codice Etico adottato", "Bilancio di Sostenibilità", "Società Benefit o B-Corp"]),
        ("Governance", ["Padronale", "Famigliare semplice", "Consiglio di Amministrazione", "Presenza di Indipendenti", "Modello di governance evoluto"]),
        ("Catena di Fornitura ESG", ["Solo prezzo", "Vicinanza", "Richiesta autocertificazioni", "Audit ESG sui fornitori", "Solo fornitori certificati"])
    ],
    'Protezione Legale': [
        ("Modello 231", ["Assente", "In fase di studio", "Adottato base", "Aggiornato costantemente", "Organismo di Vigilanza attivo"]),
        ("Privacy (GDPR)", ["Nomine base", "Documentazione vecchia", "Conformità aggiornata", "Audit periodici", "DPO nominato e processi sicuri"]),
        ("Contrattualistica", ["Accordi verbali", "Modelli scaricati dal web", "Contratti standard revisionati", "Contratti ad hoc per cliente", "Legal Management strutturato"]),
        ("Proprietà Intellettuale", ["Nessuna tutela", "Marchio registrato", "Monitoraggio marchi", "Strategia IP brevettuale", "Asset immateriali a bilancio"]),
        ("Gestione Contenzioso", ["Emergenziale", "Avvocato al bisogno", "Assicurazione tutela legale", "Prevenzione contrattuale", "Consulenza legale proattiva"]),
        ("Asset Protection", ["Nessuna separazione", "Solo polizze base", "Fondo patrimoniale/Holding", "Trust o vincoli mirati", "Pianificazione successoria legale"])
    ],
    'Sicurezza sul Lavoro': [
        ("Conformità DVR", ["Scaduto", "Base/Standard", "Aggiornato", "Dinamico/Analisi rischi mirata", "Zero infortuni target/Eccellenza"]),
        ("Formazione Sicurezza", ["Incompleta", "Solo base obbligatoria", "Tutti formati in tempo", "Formazione avanzata/comportamentale", "Cultura della sicurezza diffusa"]),
        ("Salute e Sorveglianza", ["Assente", "Solo visite obbligatorie", "Pianificata regolarmente", "Monitorata con KPI salute", "Programmi di prevenzione extra"]),
        ("Gestione DPI/Attrezzature", ["Consegna informale", "Registro cartaceo", "Controllo periodico", "Gestione digitale/automatizzata", "DPI innovativi/IoT"]),
        ("Manutenzioni Impianti", ["A guasto", "Registro scadenze", "Programmata", "Software di manutenzione", "Manutenzione predittiva"]),
        ("Gestione Appalti/Cantieri", ["Nessun controllo", "Verifica base (DURC)", "Gestione DUVRI corretta", "Coordinamento attivo", "Audit in cantiere costanti"])
    ],
    'Standard & Qualità': [
        ("Certificazione ISO 9001", ["No", "In corso", "Solo formale", "Vissuta come strumento", "Motore di miglioramento"]),
        ("Gestione Processi", ["Nessuna mappatura", "Mappatura parziale", "Procedure scritte core", "Mappatura totale", "Ottimizzazione Lean/Six Sigma"]),
        ("Controllo Qualità", ["A fine processo", "Campionamento", "Sistemico su ogni fase", "Controllo con sensori/dati", "Zero difetti/Qualità predittiva"]),
        ("Soddisfazione Cliente", ["Solo reclami", "Sondaggio sporadico", "Indagine annuale strutturata", "NPS monitorato costantemente", "Focus group e co-progettazione"]),
        ("Qualifica Fornitori", ["Solo prezzo", "Storici", "Albo fornitori base", "Rating fornitori", "Partnership e co-development"]),
        ("Gestione Non Conformità", ["Risolte e dimenticate", "Registro Excel", "Analisi cause radice", "Azioni correttive efficaci", "Prevenzione statistica"])
    ],
    'Sviluppo Competenze': [
        ("Analisi dei Gap", ["Mai fatta", "Basata su necessità urgenti", "Su richiesta dei dipendenti", "Annuale strutturata", "Mappatura competenze futuro"]),
        ("Uso Fondi Formazione", ["Mai usati", "Raramente", "Saltuariamente", "Sempre per formazione core", "Ottimizzazione totale budget"]),
        ("Metodi di Apprendimento", ["Solo aula", "Affiancamento informale", "E-learning base", "Mix (Blended/Mentoring)", "Social Learning/Academy interna"]),
        ("Leadership e Soft Skills", ["Nessun focus", "Solo per il titolare", "Corso sporadico manager", "Percorso coaching strutturato", "Leadership diffusa a tutti i livelli"]),
        ("Piani di Carriera", ["Assenti", "Solo per anzianità", "Crescita legata a opportunità", "Percorsi chiari definiti", "Meritocrazia trasparente"]),
        ("Mindset Innovativo", ["Resistenza al cambiamento", "Timore dell'errore", "Alcuni pionieri", "Apertura al test/fallimento", "Innovazione nel DNA aziendale"])
    ]
}

# --- FUNZIONE LOGICA AI (BRIDGE) ---
def genera_consulenza_nexta(punteggi, info_azienda):
    """
    Tenta di usare Gemini per un'analisi raffinata. 
    In caso di errore, genera un'analisi strutturata basata sui dati.
    """
    peggiori = sorted(punteggi.items(), key=lambda x: x[1])[:3]
    
    prompt = f"""
    Agisci come Senior Partner di NextaHub. Analizza l'azienda {info_azienda['azienda']} del settore {info_azienda['settore']} situata in {info_azienda['regione']}.
    Punteggi medi ottenuti (scala 1-5): {punteggi}.
    Aree critiche rilevate: {peggiori}.
    Catalogo Servizi NextaHub: {SERVIZI_NEXTA}.
    
    Genera un report consulenziale che:
    1. Spieghi il rischio specifico per il settore {info_azienda['settore']} nell'avere punteggi bassi in {peggiori[0][0]}.
    2. Colleghi ogni area critica a uno specifico servizio NextaHub.
    3. Definisca una roadmap di 6 mesi.
    Usa un tono autorevole, diretto e formattazione Markdown professionale.
    """

    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # LOGICA DI BACKUP: Analisi "Simulata" ma accurata
        analisi_backup = f"## 🎯 Piano d'Azione Strategico NextaHub\n\n"
        analisi_backup += f"Gentile Direzione di **{info_azienda['azienda']}**, l'analisi evidenzia una necessità prioritaria di intervento nelle seguenti aree:\n\n"
        for area, score in peggiori:
            analisi_backup += f"### 🔴 AREA: {area} (Rating: {score:.1f}/5)\n"
            analisi_backup += f"- **Rischio Rilevato:** La carenza in questa funzione impatta direttamente sulla marginalità del settore {info_azienda['settore']}.\n"
            analisi_backup += f"- **Soluzione NextaHub:** {SERVIZI_NEXTA.get(area, 'Consulenza specialistica dedicata.')}\n\n"
        analisi_backup += "--- \n*Nota: Connessione AI non disponibile. Analisi basata su logica predefinita NextaHub.*"
        return analisi_backup

# --- INIZIALIZZAZIONE SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = "Anagrafica"
if 'clienti' not in st.session_state: st.session_state.clienti = {}
if 'current_piva' not in st.session_state: st.session_state.current_piva = None

# --- SIDEBAR DI NAVIGAZIONE ---
with st.sidebar:
    st.image(LOGO_URL, width=200)
    st.markdown("### 🛠️ Strategic Suite")
    if st.button("🏢 1. Nuova Anagrafica", use_container_width=True): st.session_state.page = "Anagrafica"
    if st.button("📝 2. Assessment 54", use_container_width=True): st.session_state.page = "Questionario"
    if st.button("📊 3. Visualizza Report", use_container_width=True): st.session_state.page = "Valutazione"
    if st.button("📁 4. Archivio Storico", use_container_width=True): st.session_state.page = "Archivio"
    st.markdown("---")
    if st.session_state.current_piva:
        cl_info = st.session_state.clienti[st.session_state.current_piva]['info']
        st.caption(f"📍 Lavorando su: **{cl_info['azienda']}**")

# --- PAGINA 1: ANAGRAFICA ---
if st.session_state.page == "Anagrafica":
    st.title("🏢 Setup Nuovo Cliente")
    with st.form("form_anag"):
        c1, c2 = st.columns(2)
        with c1:
            rag_soc = st.text_input("Ragione Sociale")
            piva = st.text_input("Partita IVA / ID")
            email = st.text_input("Email Referente")
        with c2:
            settore = st.selectbox("Settore Business", list(BENCHMARK_DATI.keys()))
            regione = st.selectbox("Regione Sede", ["Lombardia", "Veneto", "Emilia-Romagna", "Piemonte", "Lazio", "Campania", "Toscana", "Puglia", "Sicilia", "Altro"])
            dimensione = st.select_slider("Dimensione Aziendale", options=["Micro", "Piccola", "Media", "Grande"])
        
        if st.form_submit_button("Crea Fascicolo Strategico"):
            if rag_soc and piva:
                st.session_state.clienti[piva] = {
                    "info": {"azienda": rag_soc, "piva": piva, "settore": settore, "regione": regione, "dimensione dimensione": dimensione, "email": email},
                    "assessments": []
                }
                st.session_state.current_piva = piva
                st.session_state.page = "Questionario"
                st.success("Fascicolo creato con successo!")
                st.rerun()
            else:
                st.error("Inserire Ragione Sociale e P.IVA per procedere.")

# --- PAGINA 2: QUESTIONARIO (54 DOMANDE IN TAB) ---
elif st.session_state.page == "Questionario":
    piva = st.session_state.current_piva
    if not piva: 
        st.warning("Seleziona o crea un cliente in Anagrafica.")
        st.stop()
    
    st.title(f"📝 Assessment Strategico: {st.session_state.clienti[piva]['info']['azienda']}")
    st.info("Rispondi a tutte le 54 domande per ottenere un'analisi accurata.")
    
    tabs = st.tabs(list(DOMANDE_MATRICE.keys()))
    temp_scores = {}

    for i, area in enumerate(DOMANDE_MATRICE.keys()):
        with tabs[i]:
            st.subheader(f"Area {area}")
            sc_area = []
            for j, (domanda, opzioni) in enumerate(DOMANDE_MATRICE[area]):
                st.markdown(f"**{j+1}. {domanda}**")
                # Radio button orizzontale per risparmiare spazio
                sc = st.radio(f"Seleziona per {domanda}", options=[1, 2, 3, 4, 5], 
                              format_func=lambda x: f"{x}: {opzioni[x-1]}", 
                              key=f"q_{piva}_{area}_{j}", label_visibility="collapsed")
                sc_area.append(sc)
            temp_scores[area] = sum(sc_area) / len(sc_area)
    
    if st.button("SALVA E GENERA ANALISI AI", use_container_width=True):
        new_ass = {
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "punteggi": temp_scores,
            "analisi_ai": ""
        }
        st.session_state.clienti[piva]['assessments'].append(new_ass)
        st.session_state.page = "Valutazione"
        st.rerun()

# --- PAGINA 3: VALUTAZIONE (REOPORT & AI) ---
elif st.session_state.page == "Valutazione":
    piva = st.session_state.current_piva
    if not piva or not st.session_state.clienti[piva]['assessments']:
        st.warning("Nessun assessment trovato. Torna al questionario.")
        st.stop()
    
    cl = st.session_state.clienti[piva]
    ass = cl['assessments'][-1]
    
    # Header Report
    st.markdown(f"## 📊 Report Strategico: {cl['info']['azienda']}")
    st.caption(f"Data Assessment: {ass['data']} | Settore: {cl['info']['settore']}")
    
    # Radar Chart
    categories = list(ass['punteggi'].keys())
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=list(ass['punteggi'].values()), theta=categories, fill='toself', name='Azienda Cliente', line_color='#e63946'))
    # Benchmark
    bench_vals = [BENCHMARK_DATI[cl['info']['settore']][c] for c in categories]
    fig.add_trace(go.Scatterpolar(r=bench_vals, theta=categories, name='Benchmark Settore', line_color='gray', line_dash='dash'))
    
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=True, height=600)
    st.plotly_chart(fig, use_container_width=True)

    # Analisi AI
    st.markdown("---")
    st.subheader("🤖 Agente AI NextaHub")
    
    if not ass['analisi_ai']:
        if st.button("🪄 Elabora Analisi Consulenziale con AI"):
            with st.spinner("L'AI sta analizzando i dati e cercando soluzioni nel catalogo Nexta..."):
                ass['analisi_ai'] = genera_consulenza_nexta(ass['punteggi'], cl['info'])
                st.rerun()
    else:
        st.markdown(ass['analisi_ai'])
        if st.button("🔄 Rigenera Analisi"):
            ass['analisi_ai'] = ""
            st.rerun()

# --- PAGINA 4: ARCHIVIO ---
elif st.session_state.page == "Archivio":
    st.title("📁 Archivio Storico Clienti")
    if not st.session_state.clienti:
        st.info("Nessun cliente in archivio.")
    else:
        for p, dati in st.session_state.clienti.items():
            with st.expander(f"🏢 {dati['info']['azienda']} (PI: {p})"):
                st.write(f"**Dati:** {dati['info']['regione']} - {dati['info']['settore']}")
                for i, a in enumerate(dati['assessments']):
                    col_a, col_b = st.columns([3, 1])
                    col_a.write(f"Assessment del {a['data']}")
                    if col_b.button("Apri", key=f"open_{p}_{i}"):
                        st.session_state.current_piva = p
                        st.session_state.page = "Valutazione"
                        st.rerun()
