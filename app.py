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
        ("Pianificazione: Esiste un Business Plan o piano industriale triennale?", {1: "Assente", 2: "Solo budget a breve", 3: "Piano a 12 mesi", 4: "Piano triennale", 5: "Piano con revisione trimestrale"}),
        ("KPI: Monitorate indicatori chiave (margini, EBITDA, costi acquisizione)?", {1: "No", 2: "Solo bilancio", 3: "Excel mensili", 4: "Dashboard software", 5: "BI Real-time"}),
        ("Organigramma: Ruoli e responsabilità sono definiti chiaramente?", {1: "Confusione", 2: "Solo verbali", 3: "Organigramma base", 4: "Mansionari completi", 5: "Struttura manageriale"}),
        ("Mercato: Effettuate analisi regolari dei competitor e del mercato?", {1: "Mai", 2: "Raramente", 3: "Annuale", 4: "Sistematico", 5: "Strategia guidata dai dati"}),
        ("Delega: Il titolare riesce a delegare le decisioni operative?", {1: "Nessuna", 2: "Minima", 3: "Prime deleghe", 4: "Processi autonomi", 5: "Delega manageriale"}),
        ("Continuità: Esiste un piano formale per il passaggio generazionale?", {1: "No", 2: "Discusso", 3: "Consapevolezza", 4: "Bozza di piano", 5: "Piano formalizzato"})
    ],
    'Digitalizzazione': [
        ("ERP: Il sistema gestionale copre tutte le aree aziendali?", {1: "Nessuno", 2: "Base", 3: "Settoriale", 4: "Integrato", 5: "Evoluto/Cloud"}),
        ("Processi: Grado di digitalizzazione dei processi interni (Paperless)?", {1: "Carta", 2: "Misto", 3: "Prevalentemente digitale", 4: "Digitale", 5: "Automatizzato"}),
        ("CRM: Gestite la relazione clienti con un software dedicato?", {1: "No", 2: "Contatti", 3: "Offerte", 4: "Integrato", 5: "Marketing Automation"}),
        ("Cybersecurity: Avete protocolli di difesa e disaster recovery?", {1: "Nulla", 2: "Minima", 3: "Backup", 4: "Audit periodici", 5: "Standard massimi"}),
        ("Web/Marketing: L'azienda investe in canali digitali per l'acquisizione?", {1: "No", 2: "Sito base", 3: "Social", 4: "Lead generation", 5: "Omnicanalità"}),
        ("AI: L'azienda utilizza o sperimenta strumenti di Intelligenza Artificiale?", {1: "No", 2: "Curiosità", 3: "Test base", 4: "Strumenti operativi", 5: "Processi AI-driven"})
    ],
    'Gestione HR': [
        ("Welfare: Esiste un piano di welfare aziendale per i dipendenti?", {1: "No", 2: "Minimo", 3: "Base", 4: "Strutturato", 5: "Evoluto"}),
        ("Valutazione: Esiste un sistema di misurazione delle performance?", {1: "No", 2: "Informale", 3: "Annuale", 4: "MBO", 5: "Feedback continuo"}),
        ("Talent: Avete strategie attive per attrarre e trattenere talenti?", {1: "No", 2: "Passivo", 3: "Networking", 4: "Branding", 5: "Leader di settore"}),
        ("Clima: Viene monitorato regolarmente il clima aziendale?", {1: "No", 2: "Raramente", 3: "Annuale", 4: "Sistematico", 5: "Cultura del benessere"}),
        ("Upskilling: Esistono piani di formazione continua per le soft/hard skills?", {1: "No", 2: "Solo obbligatoria", 3: "Sporadica", 4: "Piano annuale", 5: "Academy interna"}),
        ("Flessibilità: Sono attive politiche di smart working o orari flessibili?", {1: "No", 2: "Eccezioni", 3: "Flessibilità", 4: "Policy chiara", 5: "Lavoro per obiettivi"})
    ],
    'Finanza & Investimenti': [
        ("Cash Flow: Avete previsioni di tesoreria affidabili?", {1: "No", 2: "Settimanali", 3: "Mensili", 4: "Trimestrali", 5: "Real-time"}),
        ("Agevolata: Sfruttate sistematicamente i bandi e i crediti d'imposta?", {1: "No", 2: "Raramente", 3: "Occasionale", 4: "Pianificato", 5: "Strategico"}),
        ("Rating: Conoscete e monitorate il vostro rating bancario?", {1: "No", 2: "Vago", 3: "Annuale", 4: "Costante", 5: "Ottimizzazione attiva"}),
        ("Margini: Conoscete la marginalità analitica per prodotto/commessa?", {1: "No", 2: "Globale", 3: "Stima", 4: "Analitica", 5: "Predittiva"}),
        ("Credito: Esiste una procedura rigida di gestione e recupero crediti?", {1: "No", 2: "Reattiva", 3: "Procedure base", 4: "Assicurazione/Legale", 5: "Sistemica"}),
        ("R&D: Qual è l'incidenza degli investimenti in innovazione sul fatturato?", {1: "0%", 2: "<1%", 3: "1-3%", 4: "3-5%", 5: ">5%"})
    ],
    'Sostenibilità (ESG)': [
        ("Cultura: L'azienda conosce e applica i criteri ESG?", {1: "No", 2: "Vaga", 3: "Base", 4: "Integrazione", 5: "Bilancio ESG"}),
        ("Ambiente: Avete attuato politiche di riduzione dell'impatto ambientale?", {1: "No", 2: "Rifiuti", 3: "Energy saving", 4: "ISO 14001", 5: "Carbon Neutral"}),
        ("Sociale: Promuovete diversità, inclusione e parità di genere?", {1: "No", 2: "Sensibilità", 3: "Azioni base", 4: "Policy", 5: "Certificazione"}),
        ("Governance: Avete una struttura di governo trasparente ed etica?", {1: "No", 2: "Base", 3: "Codice Etico", 4: "Compliance", 5: "Trasparenza Totale"}),
        ("Supply Chain: Valutate i fornitori in base a criteri di sostenibilità?", {1: "No", 2: "Raramente", 3: "Questionari", 4: "Audit", 5: "Partnership ESG"}),
        ("Certificazioni: Possedete certificazioni legate alla sostenibilità?", {1: "No", 2: "In corso", 3: "Singole", 4: "Multiple", 5: "B-Corp/Rating Gold"})
    ],
    'Protezione Legale': [
        ("Modello 231: Avete implementato il Modello di Organizzazione e Gestione?", {1: "No", 2: "In corso", 3: "Adottato", 4: "Aggiornato", 5: "Efficace/ODV attivo"}),
        ("GDPR: Siete pienamente conformi al regolamento sulla privacy?", {1: "No", 2: "Base", 3: "Conforme", 4: "Audit regolarmente", 5: "DPO presente"}),
        ("Contrattualistica: I vostri contratti sono aggiornati e vi tutelano?", {1: "Standard", 2: "Base", 3: "Revisionati", 4: "Ad hoc", 5: "Legal Management"}),
        ("IP: Marchi e brevetti sono registrati e protetti?", {1: "No", 2: "Marchio", 3: "IP protetta", 4: "Gestione attiva", 5: "Patrimonio strategico"}),
        ("Recupero: Esiste un sistema legale strutturato per il recupero crediti?", {1: "No", 2: "Saltuario", 3: "Protocollo", 4: "Legale interno", 5: "Efficienza Massima"}),
        ("Assicurazioni: Avete polizze D&O o Cyber Risk adeguate?", {1: "No", 2: "Base", 3: "RC Professionale", 4: "D&O/Cyber", 5: "Gestione Broker"})
    ],
    'Sicurezza sul Lavoro': [
        ("DVR: Il Documento Valutazione Rischi è aggiornato e dinamico?", {1: "No", 2: "Obsoleto", 3: "Aggiornato", 4: "Digitale", 5: "Miglioramento Continuo"}),
        ("Formazione: La formazione obbligatoria è tracciata e aggiornata?", {1: "No", 2: "Parziale", 3: "Aggiornata", 4: "Tracciata digitale", 5: "Zero scadenze"}),
        ("Sorveglianza: La sorveglianza sanitaria è gestita correttamente?", {1: "No", 2: "Base", 3: "Regolare", 4: "Monitorata", 5: "Eccellenza"}),
        ("DPI: Gestione e consegna DPI sono tracciate formalmente?", {1: "No", 2: "Verbale", 3: "Cartaceo", 4: "Digitale", 5: "Automatizzato"}),
        ("Manutenzioni: Esiste un piano di manutenzione impianti/macchine?", {1: "No", 2: "Guasto", 3: "Base", 4: "Programmata", 5: "Predittiva"}),
        ("Infortuni: Analizzate i 'Near Miss' (quasi infortuni)?", {1: "No", 2: "Raramente", 3: "Solo gravi", 4: "Sistematico", 5: "Zero Infortuni Target"})
    ],
    'Standard & Qualità': [
        ("ISO 9001: L'azienda è certificata e il sistema è realmente attivo?", {1: "No", 2: "Formale", 3: "Attivo", 4: "Ottimizzato", 5: "Eccellenza"}),
        ("Procedure: I processi sono mappati e proceduralizzati?", {1: "No", 2: "Minimo", 3: "Core", 4: "Tutti", 5: "PDCA/Kaizen"}),
        ("Audit: Effettuate audit interni regolari sulla qualità?", {1: "No", 2: "Raramente", 3: "Annuale", 4: "Sistematico", 5: "Cultura Qualità"}),
        ("Customer: Misurate la soddisfazione cliente (NPS)?", {1: "No", 2: "Reclami", 3: "Sondaggi", 4: "Sistematico", 5: "Customer Centric"}),
        ("Fornitori: Avete un sistema di qualifica e monitoraggio fornitori?", {1: "No", 2: "Base", 3: "Qualifica", 4: "Monitoring", 5: "Rating"}),
        ("Non Conformità: Esiste un sistema di gestione errori e reclami?", {1: "No", 2: "Base", 3: "Registro", 4: "Analisi Cause", 5: "Risoluzione Radice"})
    ],
    'Sviluppo Competenze': [
        ("Gaps: Effettuate l'analisi dei gap di competenza?", {1: "No", 2: "Percezione", 3: "Base", 4: "Analitica", 5: "Strategica"}),
        ("Fondi: Sfruttate i fondi interprofessionali per la formazione?", {1: "No", 2: "Iscritti", 3: "Raramente", 4: "Sistematico", 5: "Massimizzazione"}),
        ("Academy: Esiste un sistema interno di condivisione conoscenza?", {1: "No", 2: "Minimo", 3: "Affiancamento", 4: "Manuali", 5: "Academy"}),
        ("Leadership: Formate i responsabili sulla gestione del team?", {1: "No", 2: "Minimo", 3: "Soft Skills", 4: "Coaching", 5: "Leadership diffusa"}),
        ("Piani: Esistono piani di carriera definiti per le figure chiave?", {1: "No", 2: "Vaghi", 3: "Consapevolezza", 4: "Definiti", 5: "Meritocrazia"}),
        ("Digital Mindset: Il team è pronto ai cambiamenti tecnologici?", {1: "No", 2: "Resistenza", 3: "Base", 4: "Aperti", 5: "Proattivi/Innovatori"})
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
        with col2:
            settore = st.selectbox("Settore per Benchmark", list(BENCHMARK_DATI.keys()))
            regione = st.selectbox("Regione", ["Lombardia", "Veneto", "Emilia-Romagna", "Piemonte", "Lazio", "Campania", "Altro"])
        if st.form_submit_button("Salva Cliente"):
            if azienda and piva:
                st.session_state.current_client_piva = piva
                if piva not in st.session_state.clienti:
                    st.session_state.clienti[piva] = {
                        "anagrafica": {"azienda": azienda, "piva": piva, "settore": settore, "regione": regione},
                        "revisioni": []
                    }
                go_to("Questionario")
                st.rerun()

# --- PAGINA 2: QUESTIONARIO ---
elif st.session_state.page == "Questionario":
    piva = st.session_state.current_client_piva
    if not piva: st.warning("Seleziona o crea un cliente.")
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
        
        if st.button("Salva Assessment"):
            st.session_state.clienti[piva]['revisioni'].append({
                "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "punteggi": scores, "analisi_ai": ""
            })
            st.session_state.rev_index = len(st.session_state.clienti[piva]['revisioni']) - 1
            go_to("Valutazione")
            st.rerun()

# --- PAGINA 3: RADAR & AI ---
elif st.session_state.page == "Valutazione":
    piva = st.session_state.current_client_piva
    if not piva or not st.session_state.clienti[piva]['revisioni']: st.warning("Dati mancanti.")
    else:
        cliente = st.session_state.clienti[piva]
        rev = cliente['revisioni'][st.session_state.rev_index]
        st.header(f"📊 Report del {rev['data']}")
        
        # RADAR COMPARATIVO
        settore = cliente['anagrafica']['settore']
        categorie = list(rev['punteggi'].keys())
        v_client = list(rev['punteggi'].values())
        v_bench = [BENCHMARK_DATI[settore].get(c, 3.0) for c in categorie]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=v_client, theta=categorie, fill='toself', name='Cliente', line_color='#e63946'))
        fig.add_trace(go.Scatterpolar(r=v_bench, theta=categorie, name='Media Settore', line_color='gray', line_dash='dash'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), height=500)
        st.plotly_chart(fig, use_container_width=True)

        if not rev['analisi_ai']:
            if st.button("🤖 Genera Analisi AI"):
                try:
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"Analizza l'azienda {cliente['anagrafica']['azienda']} (P.IVA {piva}) con punteggi {rev['punteggi']} nel settore {settore}."
                    res = model.generate_content(prompt)
                    rev['analisi_ai'] = res.text
                    st.rerun()
                except Exception as e: st.error(f"Errore: {e}")
        else:
            st.markdown("### Report AI Strategico")
            st.markdown(rev['analisi_ai'])

# --- PAGINA 4: SERVIZI ---
elif st.session_state.page == "Servizi":
    piva = st.session_state.current_client_piva
    if piva and st.session_state.clienti[piva]['revisioni']:
        rev = st.session_state.clienti[piva]['revisioni'][st.session_state.rev_index]
        settore = st.session_state.clienti[piva]['anagrafica']['settore']
        st.header("💼 Urgenze e Servizi NextaHub")
        c1, c2, c3 = st.columns(3)
        for area, s in rev['punteggi'].items():
            bench = BENCHMARK_DATI[settore].get(area, 3.0)
            if s < 2 or (bench - s) > 1.2: c1.error(f"🚨 **{area}**: Urgente")
            elif s < bench: c2.warning(f"⚠️ **{area}**: Programmare")
            else: c3.success(f"✅ **{area}**: In linea")

# --- PAGINA 5: ARCHIVIO ---
elif st.session_state.page == "Lista":
    st.header("📁 Archivio Storico Clienti")
    for p, d in st.session_state.clienti.items():
        with st.expander(f"🏢 {d['anagrafica']['azienda']} (P.IVA: {p})"):
            for idx, r in enumerate(d['revisioni']):
                if st.button(f"Visualizza Revisione {r['data']}", key=f"v_{p}_{idx}"):
                    st.session_state.current_client_piva = p
                    st.session_state.rev_index = idx
                    go_to("Valutazione")
                    st.rerun()
            if st.button(f"➕ Nuova Valutazione per {d['anagrafica']['azienda']}", key=f"n_{p}"):
                st.session_state.current_client_piva = p
                go_to("Questionario")
                st.rerun()
