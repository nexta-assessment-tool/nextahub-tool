import streamlit as st
import plotly.graph_objects as go
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="NextaHub Business Suite", layout="wide", initial_sidebar_state="expanded")

# --- INIZIALIZZAZIONE STATI (Session Storage) ---
if 'page' not in st.session_state:
    st.session_state.page = "Anagrafica"
if 'clienti' not in st.session_state:
    st.session_state.clienti = {} # Formato: {piva: {anagrafica: {}, punteggi: {}, analisi_ai: ""}}
if 'current_client_piva' not in st.session_state:
    st.session_state.current_client_piva = None

# --- DATABASE INTEGRALE DELLE 9 AREE (54 DOMANDE) ---
DOMANDE_MATRICE = {
    'Strategia & Controllo': [
        ("Esiste un business plan o piano industriale?", {1: "No, navighiamo a vista", 2: "Visione a 2/3 mesi", 3: "Visione a 6 mesi", 4: "Piano a 1 anno", 5: "Piano strutturato a 2+ anni"}),
        ("Monitoraggio KPI e cruscotti aziendali", {1: "Nessun dato", 2: "Controllo costi a fine anno", 3: "Monitoraggio fatturato mensile", 4: "KPI operativi monitorati", 5: "Dashboard real-time integrata"}),
        ("Definizione dell'organigramma e ruoli", {1: "Tutti fanno tutto", 2: "Ruoli accennati", 3: "Organigramma base", 4: "Mansionari definiti", 5: "Struttura manageriale autonoma"}),
        ("Analisi della concorrenza e del mercato", {1: "Mai fatta", 2: "Reattiva (seguiamo gli altri)", 3: "Analisi sporadica", 4: "Monitoraggio annuale", 5: "Strategia basata su dati costanti"}),
        ("Sistemi di delega e processi decisionali", {1: "Accentramento totale", 2: "Delega minima", 3: "Prime deleghe operative", 4: "Processi condivisi", 5: "Delega manageriale completa"}),
        ("Passaggio generazionale/continuità", {1: "Problema ignorato", 2: "Discussioni vaghe", 3: "Consapevolezza rischio", 4: "Piano abbozzato", 5: "Piano formalizzato"})
    ],
    'Digitalizzazione': [
        ("Grado di adozione ERP/Gestionale", {1: "Carta/Excel", 2: "Software base", 3: "Gestionale aree separate", 4: "ERP integrato", 5: "ERP cloud con AI"}),
        ("Digitalizzazione dei processi (Paperless)", {1: "Tutto cartaceo", 2: "Archivio PDF semplice", 3: "Parziale firma elettronica", 4: "Processi digitali", 5: "100% paperless"}),
        ("Presenza di un CRM", {1: "Nessuno", 2: "Agenda contatti", 3: "Tracciamento offerte", 4: "CRM integrato", 5: "CRM predittivo"}),
        ("Cybersecurity e protezione dati", {1: "Nessuna", 2: "Antivirus base", 3: "Backup regolari", 4: "Firewall/Disaster Recovery", 5: "SOC e test periodici"}),
        ("Presenza online e strategia digital", {1: "Nessuna", 2: "Sito vetrina", 3: "Social attivi", 4: "Lead generation", 5: "E-commerce avanzato"}),
        ("Competenze digitali del team", {1: "Analfabetismo", 2: "Base (email)", 3: "Uso Office", 4: "Strumenti collab", 5: "Cultura digitale proattiva"})
    ],
    'Gestione HR': [
        ("Politiche di Welfare", {1: "Assenti", 2: "Rimborsi minimi", 3: "Convenzioni", 4: "Piano strutturato", 5: "Piattaforma welfare"}),
        ("Valutazione performance", {1: "Nessuna", 2: "Feedback sporadico", 3: "Incontri annuali", 4: "MBO strutturati", 5: "Feedback costante"}),
        ("Attrazione talenti (Employer Branding)", {1: "Turnover alto", 2: "Difficoltà reperimento", 3: "Brand noto locale", 4: "Strategie attive", 5: "Top Employer"}),
        ("Clima aziendale", {1: "Tensioni frequenti", 2: "Comunicazione verticale", 3: "Riunioni di reparto", 4: "Sondaggi clima periodici", 5: "Trasparenza e benessere totale"}),
        ("Piani di formazione/upskilling", {1: "Nessuno", 2: "Solo obbligatoria", 3: "Corsi sporadici", 4: "Piano formativo annuale", 5: "Academy interna strutturata"}),
        ("Flessibilità e Smart Working", {1: "Solo presenza fisica", 2: "Eccezioni rare", 3: "Flessibilità oraria", 4: "Policy smart working attiva", 5: "Lavoro per obiettivi e fiducia"})
    ],
    'Finanza & Investimenti': [
        ("Pianificazione Cash Flow", {1: "Nessuna", 2: "Controllo estratto conto", 3: "Previsione a 30gg", 4: "Budget a 6 mesi", 5: "Software cash-flow real-time"}),
        ("Utilizzo Finanza Agevolata", {1: "Mai usata", 2: "Informati ma scettici", 3: "Uso occasionale", 4: "Monitoraggio attivo bandi", 5: "Strategia sistematica di finanza agevolata"}),
        ("Rapporto con Istituti di Credito", {1: "Difficile/Teso", 2: "Solo affidamenti base", 3: "Trasparenza informativa", 4: "Rating monitorato", 5: "Mix bilanciato di fonti finanziarie"}),
        ("Controllo Gestione/Margini", {1: "Sconosciuti", 2: "Margine globale a fine anno", 3: "Margine per commessa/prodotto", 4: "Analisi mensile scostamenti", 5: "Analisi predittiva dei margini"}),
        ("Gestione Credito/Insoluti", {1: "Nessun controllo", 2: "Solleciti rari", 3: "Assicurazione credito", 4: "Procedura rigida di recupero", 5: "Scoring preventivo clienti"}),
        ("Investimenti R&S", {1: "Nulli", 2: "Migliorie base", 3: "Progetti sporadici", 4: "Budget annuale R&S", 5: "Innovazione come pilastro core"})
    ],
    'Sostenibilità (ESG)': [
        ("Sensibilità ai temi ESG", {1: "Sconosciuta", 2: "Solo curiosità", 3: "Prime azioni base", 4: "Obiettivi ESG nel piano", 5: "DNA aziendale sostenibile"}),
        ("Certificazioni Ambientali", {1: "Nessuna", 2: "In fase di studio", 3: "Gestione rifiuti corretta", 4: "ISO 14001 o simili", 5: "Bilancio Carbon Neutral"}),
        ("Parità di Genere e Inclusion", {1: "Nessuna policy", 2: "Sensibilità", 3: "Equità salariale base", 4: "Certificazione parità", 5: "Leadership bilanciata"}),
        ("Sostenibilità della Filiera", {1: "Prezzo come unico driver", 2: "Audit base fornitori", 3: "Codice etico fornitori", 4: "Valutazione ESG fornitori", 5: "Filiera 100% tracciata/sostenibile"}),
        ("Efficienza Energetica", {1: "Alti sprechi", 2: "Monitoraggio bollette", 3: "Efficientamento base", 4: "Audit energetico professionale", 5: "Autoproduzione da rinnovabili"}),
        ("Bilancio di Sostenibilità", {1: "Nulla", 2: "Comunicazione su sito", 3: "Report descrittivo", 4: "Bilancio annuale", 5: "Report GRI certificato"})
    ],
    'Protezione Legale': [
        ("Presenza Modello 231", {1: "Assente", 2: "In valutazione", 3: "Presente ma non aggiornato", 4: "Aggiornato regolarmente", 5: "Efficace con ODV attivo"}),
        ("Conformità GDPR", {1: "Nulla", 2: "Solo informative sito", 3: "Registri trattamenti presenti", 4: "Audit periodici", 5: "Compliance totale con DPO"}),
        ("Contrattualistica Clienti/Fornitori", {1: "Accordi verbali", 2: "Modelli standard web", 3: "Revisionati raramente", 4: "Contratti legali ad hoc", 5: "Sistema integrato Risk Management"}),
        ("Tutela Proprietà Intellettuale", {1: "Nessuna", 2: "Marchio registrato", 3: "Protezione know-how base", 4: "Portafoglio brevetti/marchi", 5: "Strategia IP globale"}),
        ("Recupero Crediti Legale", {1: "Assente", 2: "Azione sporadica", 3: "Fase di sollecito legale", 4: "Procedura strutturata", 5: "Assicurazione e ufficio legale integrato"}),
        ("Analisi Rischi Assicurativi", {1: "Nessuna", 2: "Solo obbligatorie", 3: "Coperture base", 4: "Analisi con Broker dedicata", 5: "Polizze Cyber e D&O attive"})
    ],
    'Sicurezza sul Lavoro': [
        ("Aggiornamento DVR", {1: "Inesistente", 2: "Obsoleto (>3 anni)", 3: "Aggiornato al minimo", 4: "Analitico e recente", 5: "Documento dinamico digitale"}),
        ("Formazione Obbligatoria", {1: "Scaduta/Assente", 2: "In corso di recupero", 3: "Monitorata su Excel", 4: "Pienamente conforme", 5: "Cultura della sicurezza diffusa"}),
        ("Sorveglianza Sanitaria", {1: "Assente", 2: "Ritardi nelle visite", 3: "Nomina presente", 4: "Scadenze regolari", 5: "Focus su benessere e prevenzione"}),
        ("DPI e Manutenzioni", {1: "Nessun registro", 2: "Gestione casuale", 3: "Registro cartaceo", 4: "Programmata regolarmente", 5: "Software gestione manutenzioni"}),
        ("Gestione Appalti (DUVRI)", {1: "Mai fatto", 2: "Solo per grandi lavori", 3: "Standard base", 4: "Processo accurato", 5: "Monitoraggio fornitori real-time"}),
        ("Gestione Infortuni e Near Miss", {1: "Nessuna traccia", 2: "Solo denunce obbligatorie", 3: "Analisi cause infortuni", 4: "Tracciamento quasi-infortuni", 5: "Sistema di prevenzione partecipativa"})
    ],
    'Standard & Qualità': [
        ("Certificazione ISO 9001", {1: "Assente", 2: "In fase di avvio", 3: "Ottenuta (formale)", 4: "Sostanziale nei processi", 5: "Driver di miglioramento continuo"}),
        ("Manuale Procedure", {1: "Tutto a memoria", 2: "Note sparse", 3: "Manuale base", 4: "Procedure scritte e note", 5: "Processi ottimizzati e digitali"}),
        ("Gestione Non Conformità", {1: "Ignorate", 2: "Gestite se gravi", 3: "Registro presente", 4: "Analisi cause radice", 5: "Cicli PDCA/Kaizen attivi"}),
        ("Soddisfazione Cliente", {1: "Mai misurata", 2: "Solo gestione reclami", 3: "Sondaggio annuale", 4: "Analisi NPS e feedback", 5: "Strategia Customer Centric"}),
        ("Audit Interni", {1: "Mai fatti", 2: "Rari/Pre-rinnovo", 3: "Annuali obbligatori", 4: "Semestrali/Incrociati", 5: "Cultura dell'auto-valutazione"}),
        ("Qualità Fornitori", {1: "Scelta solo su prezzo", 2: "Valutazione soggettiva", 3: "Albo fornitori base", 4: "Valutazione annuale KPI", 5: "Partnership strategiche certificate"})
    ],
    'Sviluppo Competenze': [
        ("Analisi Gap Competenze", {1: "Mai fatta", 2: "Percezione del titolare", 3: "Analisi tecnica base", 4: "Mappa delle competenze", 5: "Piano di sviluppo individuale"}),
        ("Utilizzo Fondi Interprofessionali", {1: "Ignorati", 2: "Iscritti ma non usati", 3: "Uso sporadico", 4: "Pianificazione annuale", 5: "Saturazione totale dei fondi"}),
        ("Percorsi di Coaching/Mentoring", {1: "Assenti", 2: "Affiancamento tecnico", 3: "Tutor per neoassunti", 4: "Percorsi di coaching", 5: "Cultura di mentoring diffusa"}),
        ("Soft Skills e Digital Mindset", {1: "Nessuna attenzione", 2: "Base", 3: "Discrete", 4: "Focus su problem solving", 5: "Leadership diffusa e agilità"}),
        ("Tracciamento Formazione", {1: "Nessuno", 2: "Raccoglitore attestati", 3: "File Excel", 4: "Database digitale", 5: "Libretto formativo digitale"}),
        ("Condivisione del Know-how", {1: "Informazione gelosa", 2: "Appunti personali", 3: "Cartelle condivise", 4: "Manuali tecnici", 5: "Wiki/Knowledge Base aziendale"})
    ]
}

# --- FUNZIONI DI NAVIGAZIONE ---
def go_to(page_name):
    st.session_state.page = page_name

# --- SIDEBAR NAVIGAZIONE ---
with st.sidebar:
    st.image("https://www.nextahub.it/wp-content/uploads/2023/05/logo-nextahub.png", width=180)
    st.title("Menu Principale")
    st.button("🏠 1. Anagrafica Cliente", on_click=go_to, args=("Anagrafica",), use_container_width=True)
    st.button("📝 2. Questionario", on_click=go_to, args=("Questionario",), use_container_width=True)
    st.button("📊 3. Radar & Analisi AI", on_click=go_to, args=("Valutazione",), use_container_width=True)
    st.button("💼 4. Servizi NextaHub", on_click=go_to, args=("Servizi",), use_container_width=True)
    st.button("📁 5. Archivio Clienti", on_click=go_to, args=("Lista",), use_container_width=True)

# --- PAGINA 1: ANAGRAFICA ---
if st.session_state.page == "Anagrafica":
    st.header("1️⃣ Anagrafica Potenziale Cliente")
    with st.form("anagrafica_form"):
        col1, col2 = st.columns(2)
        with col1:
            azienda = st.text_input("Ragione Sociale")
            piva = st.text_input("Partita IVA")
        with col2:
            indirizzo = st.text_input("Indirizzo Sede Completo")
            regione = st.selectbox("Regione Prevalente", ["Lombardia", "Veneto", "Emilia-Romagna", "Piemonte", "Toscana", "Lazio", "Campania", "Altro"])
        
        settore = st.selectbox("Settore merceologico", ["Manifatturiero", "Servizi", "Edilizia", "IT & Digital", "Agri-Food", "Retail"])
        note = st.text_area("Note e contesto (es. numero dipendenti, fatturato stimato)")
        
        if st.form_submit_button("Salva e Vai al Questionario"):
            if azienda and piva:
                st.session_state.current_client_piva = piva
                st.session_state.clienti[piva] = {
                    "anagrafica": {"azienda": azienda, "piva": piva, "indirizzo": indirizzo, "regione": regione, "settore": settore, "note": note},
                    "punteggi": {},
                    "analisi_ai": ""
                }
                go_to("Questionario")
                st.rerun()
            else:
                st.error("⚠️ Ragione Sociale e P.IVA sono obbligatori.")

# --- PAGINA 2: QUESTIONARIO ---
elif st.session_state.page == "Questionario":
    piva = st.session_state.current_client_piva
    if not piva:
        st.warning("Inserisci prima i dati in Anagrafica.")
    else:
        st.header(f"📝 Assessment Diagnostico: {st.session_state.clienti[piva]['anagrafica']['azienda']}")
        st.info("Rispondi a tutte le domande selezionando il livello che meglio descrive l'azienda.")
        
        final_scores = {}
        tabs = st.tabs(list(DOMANDE_MATRICE.keys()))
        
        for i, area in enumerate(DOMANDE_MATRICE.keys()):
            with tabs[i]:
                punteggi_area = []
                for j, (testo, opzioni) in enumerate(DOMANDE_MATRICE[area]):
                    val = st.radio(testo, options=[1, 2, 3, 4, 5], 
                                  format_func=lambda x: f"{x}: {opzioni[x]}", 
                                  key=f"q_{piva}_{area}_{j}")
                    punteggi_area.append(val)
                final_scores[area] = sum(punteggi_area) / len(punteggi_area)
        
        if st.button("Finalizza Questionario"):
            st.session_state.clienti[piva]['punteggi'] = final_scores
            go_to("Valutazione")
            st.rerun()

# --- PAGINA 3: RADAR & AI ---
elif st.session_state.page == "Valutazione":
    piva = st.session_state.current_client_piva
    cliente = st.session_state.clienti.get(piva)
    
    if not cliente or not cliente['punteggi']:
        st.warning("Completa il questionario per visualizzare i risultati.")
    else:
        st.header(f"📊 Risultati Analisi: {cliente['anagrafica']['azienda']}")
        
        # Diagramma a Radar
        categories = list(cliente['punteggi'].keys())
        values = list(cliente['punteggi'].values())
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values, theta=categories, fill='toself', 
            name=cliente['anagrafica']['azienda'], line_color='#e63946'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            height=600, title="Matrice di Maturità Aziendale"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        if st.button("✨ Genera Report AI Strategico"):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                
                # LOGICA RESILIENTE PER IL MODELLO
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                selected_model = next((m for m in available_models if "flash" in m), available_models[0])
                model = genai.GenerativeModel(selected_model)
                
                prompt = f"""
                Agisci come un esperto Business Consultant di NextaHub.
                Analizza l'azienda {cliente['anagrafica']['azienda']} (Settore: {cliente['anagrafica']['settore']}).
                Località: {cliente['anagrafica']['indirizzo']}, Regione: {cliente['anagrafica']['regione']}.
                P.IVA: {cliente['anagrafica']['piva']}.
                
                Dati dell'Assessment (Punteggio da 1 a 5):
                {cliente['punteggi']}
                
                Note aggiuntive: {cliente['anagrafica']['note']}
                
                Compito:
                1. ANALISI TERRITORIALE: Identifica bandi regionali o opportunità nel distretto di {cliente['anagrafica']['regione']}.
                2. INTERPRETAZIONE P.IVA E SETTORE: Analizza la complessità normativa legata al settore {cliente['anagrafica']['settore']}.
                3. PRIORITÀ: Indica le 3 aree critiche (punteggio più basso) e spiega i rischi reali.
                4. ROADMAP: Piano d'azione in 2 fasi (0-6 mesi e 6-18 mesi).
                """
                
                with st.spinner("L'AI sta incrociando i dati territoriali e settoriali..."):
                    res = model.generate_content(prompt)
                    cliente['analisi_ai'] = res.text
                    st.success("Report Generato!")
                    st.markdown("---")
                    st.markdown(res.text)
            except Exception as e:
                st.error(f"Errore generazione AI: {e}")

# --- PAGINA 4: SERVIZI ---
elif st.session_state.page == "Servizi":
    piva = st.session_state.current_client_piva
    if not piva: st.warning("Seleziona un cliente.")
    else:
        st.header("💼 Soluzioni NextaHub su Misura")
        scores = st.session_state.clienti[piva]['punteggi']
        azienda = st.session_state.clienti[piva]['anagrafica']['azienda']
        
        st.subheader(f"Piano consigliato per {azienda}")
        
        # Logica di raccomandazione automatica
        col1, col2 = st.columns(2)
        with col1:
            st.info("🔍 Focus Servizi Necessari")
            for area, s in scores.items():
                if s < 3:
                    st.write(f"- **{area}**: Intervento urgente specialistico.")
        
        with col2:
            avg = sum(scores.values()) / len(scores)
            if avg < 2.5:
                st.error("📦 Modello consigliato: NEXTA ELITE (Gestione Integrata)")
            elif avg < 4:
                st.warning("📦 Modello consigliato: NEXTA FLEX (Supporto Specialistico)")
            else:
                st.success("📦 Modello consigliato: NEXTA ENTRY (Maintenance & Audit)")

# --- PAGINA 5: ARCHIVIO ---
elif st.session_state.page == "Lista":
    st.header("📁 Archivio Analisi Effettuate")
    if not st.session_state.clienti:
        st.info("Nessuna analisi salvata in memoria.")
    else:
        for p, dati in st.session_state.clienti.items():
            with st.expander(f"{dati['anagrafica']['azienda']} (P.IVA: {p})"):
                st.write(f"**Data:** {datetime.now().strftime('%d/%m/%Y')}")
                st.write(f"**Regione:** {dati['anagrafica']['regione']} | **Settore:** {dati['anagrafica']['settore']}")
                
                c1, c2 = st.columns(2)
                if c1.button("Recupera Report AI", key=f"rep_{p}"):
                    st.session_state.current_client_piva = p
                    go_to("Valutazione")
                    st.rerun()
                if c2.button("Rifai Assessment", key=f"rif_{p}"):
                    st.session_state.current_client_piva = p
                    go_to("Questionario")
                    st.rerun()
