import streamlit as st
import plotly.graph_objects as go
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="NextaHub Strategic Suite", layout="wide", initial_sidebar_state="expanded")

# --- BENCHMARK DI SETTORE (Simulazione dati medi) ---
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

# --- DATABASE INTEGRALE 54 DOMANDE ARTICOLATE ---
DOMANDE_MATRICE = {
    'Strategia & Controllo': [
        ("Pianificazione Industriale: Esiste un Business Plan (documento che definisce obiettivi e risorse)?", {1: "Assente", 2: "Solo budget breve termine", 3: "Piano a 12 mesi", 4: "Piano triennale", 5: "Piano strutturato con revisione trimestrale"}),
        ("Monitoraggio KPI: L'azienda usa indicatori chiave (es. margini, costi acquisizione) per decidere?", {1: "No", 2: "Solo bilancio annuale", 3: "Report mensili Excel", 4: "Dashboard software", 5: "Business Intelligence in tempo reale"}),
        ("Organigramma: Sono definiti ruoli e responsabilità chiare per ogni dipendente?", {1: "Tutti fanno tutto", 2: "Ruoli accennati", 3: "Organigramma base", 4: "Mansionari definiti", 5: "Struttura manageriale autonoma"}),
        ("Analisi Concorrenza: L'azienda monitora i prezzi e le strategie dei competitor?", {1: "Mai fatta", 2: "Reattiva", 3: "Analisi sporadica", 4: "Monitoraggio annuale", 5: "Strategia basata su dati costanti"}),
        ("Sistemi di Delega: Il titolare riesce a delegare decisioni importanti o è tutto accentrato?", {1: "Accentramento totale", 2: "Delega minima", 3: "Prime deleghe operative", 4: "Processi condivisi", 5: "Delega manageriale completa"}),
        ("Continuità Aziendale: Esiste un piano per il passaggio generazionale o l'assenza improvvisa del leader?", {1: "Problema ignorato", 2: "Discussioni vaghe", 3: "Consapevolezza rischio", 4: "Piano abbozzato", 5: "Piano formalizzato"})
    ],
    'Digitalizzazione': [
        ("ERP/Gestionale: Il software aziendale copre tutte le aree (vendite, acquisti, magazzino)?", {1: "Carta/Excel", 2: "Software base", 3: "Gestionale aree separate", 4: "ERP integrato", 5: "ERP cloud con AI"}),
        ("Paperless: Quanti processi sono ancora basati sulla stampa di documenti fisici?", {1: "Tutto cartaceo", 2: "Archivio PDF semplice", 3: "Parziale firma elettronica", 4: "Processi digitali", 5: "100% paperless"}),
        ("CRM: Avete un sistema per tracciare le trattative con i clienti e le opportunità?", {1: "Nessuno", 2: "Agenda contatti", 3: "Tracciamento offerte", 4: "CRM integrato", 5: "CRM predittivo"}),
        ("Cybersecurity: Avete protocolli contro attacchi hacker o perdita dati?", {1: "Nessuna", 2: "Antivirus base", 3: "Backup regolari", 4: "Firewall/Disaster Recovery", 5: "SOC e test periodici"}),
        ("Digital Marketing: L'azienda acquisisce nuovi clienti tramite canali digitali?", {1: "Nessuna", 2: "Sito vetrina", 3: "Social attivi", 4: "Lead generation", 5: "E-commerce avanzato"}),
        ("Competenze Digitali: Il personale è formato sull'uso dei nuovi strumenti tecnologici?", {1: "Analfabetismo", 2: "Base (email)", 3: "Uso Office", 4: "Strumenti collab", 5: "Cultura digitale proattiva"})
    ],
    'Gestione HR': [
        ("Welfare: Esistono benefit per i dipendenti (es. assicurazioni, buoni pasto, asili)?", {1: "Assenti", 2: "Rimborsi minimi", 3: "Convenzioni", 4: "Piano strutturato", 5: "Piattaforma welfare"}),
        ("Performance: Esiste un sistema per valutare il lavoro e dare feedback ai dipendenti?", {1: "Nessuna", 2: "Feedback sporadico", 3: "Incontri annuali", 4: "MBO strutturati", 5: "Feedback costante"}),
        ("Attrazione Talenti: È facile per voi trovare e assumere nuove figure competenti?", {1: "Turnover alto", 2: "Difficoltà reperimento", 3: "Brand noto locale", 4: "Strategie attive", 5: "Top Employer"}),
        ("Clima Aziendale: Viene misurato il benessere dei lavoratori?", {1: "Tensioni frequenti", 2: "Comunicazione verticale", 3: "Riunioni reparto", 4: "Sondaggi clima", 5: "Trasparenza totale"}),
        ("Formazione: Esiste un budget per la crescita professionale non obbligatoria?", {1: "Nessuno", 2: "Solo obbligatoria", 3: "Corsi sporadici", 4: "Piano annuale", 5: "Academy interna"}),
        ("Flessibilità: L'azienda permette forme di lavoro agile (Smart Working)?", {1: "Solo presenza", 2: "Eccezioni rare", 3: "Flessibilità oraria", 4: "Policy attiva", 5: "Lavoro per obiettivi"})
    ],
    'Finanza & Investimenti': [
        ("Cash Flow: Avete una previsione delle entrate/uscite di cassa a 6 mesi?", {1: "Nessuna", 2: "Estratto conto", 3: "Previsione 30gg", 4: "Budget 6 mesi", 5: "Software real-time"}),
        ("Finanza Agevolata: Sfruttate bandi, crediti d'imposta o contributi a fondo perduto?", {1: "Mai usata", 2: "Informati", 3: "Uso occasionale", 4: "Monitoraggio attivo", 5: "Strategia sistematica"}),
        ("Banche: Com'è il rapporto con gli istituti di credito?", {1: "Difficile", 2: "Affidamenti base", 3: "Trasparenza", 4: "Rating monitorato", 5: "Mix bilanciato fonti"}),
        ("Marginalità: Conoscete l'esatto guadagno netto per ogni singolo prodotto/servizio?", {1: "Sconosciuti", 2: "Margine globale", 3: "Per commessa", 4: "Analisi mensile", 5: "Analisi predittiva"}),
        ("Gestione Credito: Quanto è strutturato il recupero delle fatture scadute?", {1: "Assente", 2: "Solleciti rari", 3: "Assicurazione credito", 4: "Procedura rigida", 5: "Scoring preventivo"}),
        ("R&S: Quanto investite in nuovi prodotti o processi innovativi?", {1: "Nulli", 2: "Migliorie base", 3: "Progetti sporadici", 4: "Budget annuale", 5: "Innovazione core"})
    ],
    'Sostenibilità (ESG)': [
        ("Sensibilità ESG: L'azienda conosce i criteri Ambientali, Sociali e di Governance?", {1: "Sconosciuta", 2: "Solo curiosità", 3: "Base", 4: "Obiettivi nel piano", 5: "DNA aziendale"}),
        ("Ambiente: Avete certificazioni verdi o sistemi di riduzione rifiuti?", {1: "Nessuna", 2: "Studio", 3: "Gestione rifiuti", 4: "ISO 14001", 5: "Carbon Neutral"}),
        ("Sociale: Promuovete la parità di genere e l'inclusione?", {1: "Nessuna", 2: "Sensibilità", 3: "Equità base", 4: "Certificata", 5: "Leadership bilanciata"}),
        ("Filiera: Selezionate i fornitori anche in base alla loro sostenibilità?", {1: "Solo prezzo", 2: "Audit base", 3: "Codice etico", 4: "Valutazione ESG", 5: "Filiera tracciata"}),
        ("Energia: Avete fatto audit energetici per ridurre i costi delle bollette?", {1: "Sprechi", 2: "Monitoraggio", 3: "Efficientamento", 4: "Audit professionale", 5: "Rinnovabili"}),
        ("Bilancio Sostenibilità: Producete un report annuale sull'impatto non finanziario?", {1: "Nulla", 2: "News sito", 3: "Report base", 4: "Bilancio annuale", 5: "Report GRI"})
    ],
    'Protezione Legale': [
        ("Modello 231: Avete un sistema di controllo per evitare responsabilità penali aziendali?", {1: "Assente", 2: "In valutazione", 3: "Vecchio", 4: "Aggiornato", 5: "ODV attivo"}),
        ("GDPR: La gestione della privacy è conforme alle ultime normative europee?", {1: "Nulla", 2: "Informative", 3: "Registri", 4: "Audit", 5: "DPO presente"}),
        ("Contrattualistica: I contratti con clienti e fornitori sono solidi o standard?", {1: "Verbali", 2: "Web standard", 3: "Revisioni rare", 4: "Contratti ad hoc", 5: "Risk Management"}),
        ("Tutela IP: Avete protetto marchi, brevetti o il know-how aziendale?", {1: "Nessuna", 2: "Marchio", 3: "Know-how protetto", 4: "Brevetti", 5: "Strategia IP globale"}),
        ("Recupero Crediti: Avete un legale o un processo per recuperare i mancati pagamenti?", {1: "Assente", 2: "Sporadico", 3: "Solleciti", 4: "Procedura strutturata", 5: "Legale integrato"}),
        ("Assicurazioni: Avete polizze per danni Cyber o responsabilità degli amministratori (D&O)?", {1: "Nessuna", 2: "Obbligatorie", 3: "Base", 4: "Analisi Broker", 5: "All-risk attiva"})
    ],
    'Sicurezza sul Lavoro': [
        ("DVR: Il Documento Valutazione Rischi è aggiornato e conosciuto dai responsabili?", {1: "Inesistente", 2: "Obsoleto", 3: "Base", 4: "Analitico", 5: "Dinamico"}),
        ("Formazione Sicurezza: Tutti i dipendenti hanno i corsi aggiornati secondo legge?", {1: "Scaduta", 2: "In corso", 3: "Monitorata", 4: "Pienamente conforme", 5: "Cultura sicurezza"}),
        ("Sorveglianza Sanitaria: Il Medico del Lavoro effettua le visite regolarmente?", {1: "Assente", 2: "Ritardi", 3: "Nomina presente", 4: "Regolare", 5: "Focus benessere"}),
        ("Manutenzioni: Avete un registro per il controllo periodico di macchinari e impianti?", {1: "Nessuno", 2: "Casual", 3: "Cartaceo", 4: "Programmata", 5: "Software dedicato"}),
        ("Appalti (DUVRI): Gestite correttamente la sicurezza dei lavoratori esterni/fornitori?", {1: "Assente", 2: "Standard", 3: "Grandi lavori", 4: "Accurato", 5: "Real-time"}),
        ("Near Miss: Tracciate i 'quasi infortuni' per prevenire incidenti futuri?", {1: "Nessuna", 2: "Solo infortuni", 3: "Tracciamento base", 4: "Analisi cause", 5: "Zero infortuni"})
    ],
    'Standard & Qualità': [
        ("ISO 9001: Esiste un sistema Qualità certificato e realmente applicato?", {1: "Assente", 2: "In corso", 3: "Formale", 4: "Sostanziale", 5: "Miglioramento"}),
        ("Procedure: I processi aziendali sono scritti o affidati alla memoria dei singoli?", {1: "Memoria", 2: "Note", 3: "Manuale base", 4: "Procedure scritte", 5: "Ottimizzati"}),
        ("Non Conformità: Gestite e risolvete sistematicamente gli errori di produzione/servizio?", {1: "Ignorate", 2: "Reattive", 3: "Registro", 4: "Analisi cause", 5: "Kaizen"}),
        ("Customer Satisfaction: Misurate periodicamente quanto i clienti sono soddisfatti?", {1: "Mai", 2: "Solo reclami", 3: "Sondaggio", 4: "Analisi NPS", 5: "Customer Centric"}),
        ("Audit: Effettuate controlli interni per verificare il rispetto delle procedure?", {1: "Mai", 2: "Rari", 3: "Pre-rinnovo", 4: "Semestrali", 5: "Auto-controllo"}),
        ("Fornitori: Valutate i fornitori periodicamente tramite indicatori (KPI)?", {1: "Prezzo", 2: "Base", 3: "Albo", 4: "Valutazione annuale", 5: "Partnership"})
    ],
    'Sviluppo Competenze': [
        ("Piano Formativo: Avete un piano di crescita basato sui gap di competenza reali?", {1: "Assente", 2: "Percezione", 3: "Tecnica", 4: "Matrice competenze", 5: "Individuale"}),
        ("Fondi: Usate Fondimpresa o altri fondi per finanziare la formazione?", {1: "No", 2: "Iscritti", 3: "Occasionale", 4: "Pianificato", 5: "Saturazione"}),
        ("Coaching: Esistono percorsi per la crescita dei futuri manager/responsabili?", {1: "Assente", 2: "Affiancamento", 3: "Tutor", 4: "Coaching", 5: "Cultura Mentoring"}),
        ("Soft Skills: Formate il personale su leadership, comunicazione e gestione tempo?", {1: "No", 2: "Base", 3: "Discrete", 4: "Problem solving", 5: "Agilità"}),
        ("Tracciamento: Sapete esattamente quali competenze ha ogni dipendente?", {1: "No", 2: "CV", 3: "Excel", 4: "Digitale", 5: "Libretto formativo"}),
        ("Knowledge Sharing: Il know-how è condiviso o rimane bloccato nelle persone?", {1: "Bloccato", 2: "Appunti", 3: "Cartelle", 4: "Manuali", 5: "Wiki aziendale"})
    ]
}

def go_to(page): st.session_state.page = page

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://www.nextahub.it/wp-content/uploads/2023/05/logo-nextahub.png", width=200)
    st.markdown("---")
    st.button("🏠 1. Anagrafica", on_click=go_to, args=("Anagrafica",), use_container_width=True)
    st.button("📝 2. Questionario (54 Domande)", on_click=go_to, args=("Questionario",), use_container_width=True)
    st.button("📊 3. Radar & Analisi AI", on_click=go_to, args=("Valutazione",), use_container_width=True)
    st.button("💼 4. Servizi & Urgenze", on_click=go_to, args=("Servizi",), use_container_width=True)
    st.button("📁 5. Archivio", on_click=go_to, args=("Lista",), use_container_width=True)

# --- PAGINA 1: ANAGRAFICA ---
if st.session_state.page == "Anagrafica":
    st.header("🏢 Anagrafica Cliente")
    with st.form("anag_form"):
        col1, col2 = st.columns(2)
        with col1:
            azienda = st.text_input("Ragione Sociale")
            piva = st.text_input("Partita IVA")
        with col2:
            settore = st.selectbox("Settore per Benchmark", list(BENCHMARK_DATI.keys()))
            regione = st.selectbox("Regione", ["Lombardia", "Veneto", "Emilia-Romagna", "Piemonte", "Lazio", "Campania", "Altro"])
        indirizzo = st.text_input("Indirizzo Sede")
        if st.form_submit_button("Avvia Assessment"):
            if azienda and piva:
                st.session_state.current_client_piva = piva
                st.session_state.clienti[piva] = {
                    "anagrafica": {"azienda": azienda, "piva": piva, "settore": settore, "regione": regione, "indirizzo": indirizzo},
                    "punteggi": {}, "analisi_ai": ""
                }
                go_to("Questionario")
                st.rerun()

# --- PAGINA 2: QUESTIONARIO ---
elif st.session_state.page == "Questionario":
    piva = st.session_state.current_client_piva
    cliente = st.session_state.clienti.get(piva)
    st.header(f"📝 Assessment Completo: {cliente['anagrafica']['azienda']}")
    
    scores = {}
    tabs = st.tabs(list(DOMANDE_MATRICE.keys()))
    for i, area in enumerate(DOMANDE_MATRICE.keys()):
        with tabs[i]:
            p_area = []
            for j, (q, opts) in enumerate(DOMANDE_MATRICE[area]):
                val = st.radio(q, options=[1,2,3,4,5], format_func=lambda x: f"{x}: {opts[x]}", key=f"{piva}_{area}_{j}")
                p_area.append(val)
            scores[area] = sum(p_area)/len(p_area)
    
    if st.button("Salva Risultati"):
        st.session_state.clienti[piva]['punteggi'] = scores
        go_to("Valutazione")
        st.rerun()

# --- PAGINA 3: RADAR & AI ---
elif st.session_state.page == "Valutazione":
    piva = st.session_state.current_client_piva
    cliente = st.session_state.clienti.get(piva)
    st.header(f"📊 Risultati e Analisi AI: {cliente['anagrafica']['azienda']}")
    
    settore = cliente['anagrafica']['settore']
    categorie = list(cliente['punteggi'].keys())
    valori_cliente = list(cliente['punteggi'].values())
    valori_benchmark = [BENCHMARK_DATI[settore].get(c, 3.0) for c in categorie]
    
    # Radar
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=valori_cliente, theta=categorie, fill='toself', name='Tua Azienda', line_color='#e63946'))
    fig.add_trace(go.Scatterpolar(r=valori_benchmark, theta=categorie, name=f'Media Settore {settore}', line_color='gray', line_dash='dash'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), height=500)
    st.plotly_chart(fig, use_container_width=True)

    if st.button("🤖 Genera Report Strategico con AI"):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            # Auto-rilevamento modello resiliente
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            model_name = next((m for m in models if "flash" in m), models[0])
            model = genai.GenerativeModel(model_name)
            
            prompt = f"""
            Analizza l'azienda {cliente['anagrafica']['azienda']} (P.IVA {cliente['anagrafica']['piva']}).
            Settore: {settore}, Regione: {cliente['anagrafica']['regione']}.
            Punteggi (1-5): {cliente['punteggi']}.
            Benchmark Settore: {BENCHMARK_DATI[settore]}.
            
            Produci un'analisi di:
            1. Opportunità locali (bandi in {cliente['anagrafica']['regione']}).
            2. Analisi competitiva basata sui gap con il settore.
            3. Roadmap prioritaria 2026.
            """
            with st.spinner("L'intelligenza artificiale NextaHub sta elaborando..."):
                res = model.generate_content(prompt)
                cliente['analisi_ai'] = res.text
                st.markdown(res.text)
        except Exception as e: st.error(f"Errore AI: {e}")

# --- PAGINA 4: SERVIZI & URGENZE ---
elif st.session_state.page == "Servizi":
    piva = st.session_state.current_client_piva
    cliente = st.session_state.clienti.get(piva)
    st.header("💼 Piano Servizi NextaHub")
    
    scores = cliente['punteggi']
    settore = cliente['anagrafica']['settore']
    
    col1, col2, col3 = st.columns(3)
    col1.subheader("🚨 URGENZA ALTA")
    col2.subheader("⚠️ URGENZA MEDIA")
    col3.subheader("✅ MANTENIMENTO")
    
    for area, s in scores.items():
        bench = BENCHMARK_DATI[settore].get(area, 3.0)
        gap = bench - s
        if s < 2 or gap > 1.2:
            col1.error(f"**{area}**")
            col1.caption(f"Punteggio: {s:.1f} (Settore: {bench})")
            col1.write("→ Intervento urgente necessario.")
        elif s < bench:
            col2.warning(f"**{area}**")
            col2.caption(f"Punteggio: {s:.1f} (Settore: {bench})")
            col2.write("→ Miglioramento programmato.")
        else:
            col3.success(f"**{area}**")
            col3.caption(f"Punteggio: {s:.1f} (Settore: {bench})")
            col3.write("→ In linea o superiore.")

# --- PAGINA 5: LISTA ---
elif st.session_state.page == "Lista":
    st.header("📁 Archivio Analisi")
    for p, d in st.session_state.clienti.items():
        if st.button(f"{d['anagrafica']['azienda']} - {p}", use_container_width=True):
            st.session_state.current_client_piva = p
            go_to("Valutazione")
            st.rerun()
