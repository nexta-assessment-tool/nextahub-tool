import streamlit as st
import plotly.graph_objects as go
import google.generativeai as genai
from datetime import datetime
import pandas as pd

# --- 1. CONFIGURAZIONE DI SISTEMA ---
API_KEY = "AIzaSyBDVGaDPzABpySSiKIkktpLisvjRcMiSqg"
LOGO_URL = "https://www.nextahub.it/wp-content/uploads/2023/05/logo-nextahub.png"

st.set_page_config(
    page_title="NextaHub Strategic Suite v3.0",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. DATABASE BENCHMARK (Dati Medi Nazionali per Settore) ---
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

# --- 3. CATALOGO SERVIZI NEXTAHUB (Istruzioni per l'Agente AI) ---
SERVIZI_NEXTA = {
    "Strategia & Controllo": "Implementazione Dashboard KPI, Piani di Passaggio Generazionale, Temporary Management e Revisione Processi Aziendali.",
    "Digitalizzazione": "Piano Transizione 5.0, Audit Cybersecurity, E-commerce B2B/B2C e Integrazione AI nei processi operativi.",
    "Gestione HR": "Sviluppo Piani di Welfare, Academy Aziendali, Sistemi di MBO e Ricerca/Selezione di profili executive.",
    "Finanza & Investimenti": "Scouting Finanza Agevolata (Bandi), Crediti d'imposta R&S, Ottimizzazione Rating Bancario e Tesoreria.",
    "Sostenibilità (ESG)": "Redazione Bilancio di Sostenibilità, Certificazione Parità di Genere, Implementazione ISO 14001 e ESG Rating.",
    "Protezione Legale": "Implementazione Modello 231, Compliance GDPR, Contrattualistica Internazionale e Asset Protection.",
    "Sicurezza sul Lavoro": "DVR Dinamico, Medicina del Lavoro, Formazione Finanziata 81/08 e Gestione Sicurezza Cantieri.",
    "Standard & Qualità": "Ottenimento Certificazioni ISO (9001, 45001, 27001) e Audit di qualità sulla filiera dei fornitori.",
    "Sviluppo Competenze": "Formazione tramite Fondi Interprofessionali, Coaching Manageriale e Piani di Reskilling per la forza vendita."
}

# --- 4. MATRICE COMPLETA 54 DOMANDE (9 Aree x 6 Domande) ---
DOMANDE_MATRICE = {
    'Strategia & Controllo': [
        ("Piano Strategico", ["Nessun piano definito", "Obiettivi solo verbali", "Budget annuale presente", "Piano triennale scritto", "Piano dinamico con revisione trimestrale"]),
        ("Monitoraggio KPI", ["Assente", "Solo bilancio annuale", "Excel aggiornato saltuariamente", "Dashboard mensile", "Business Intelligence real-time"]),
        ("Organigramma e Ruoli", ["Tutto in testa al titolare", "Ruoli confusi e sovrapposti", "Schema base presente", "Organigramma definito con deleghe", "Manager autonomi con obiettivi chiari"]),
        ("Analisi Competitor", ["Mai effettuata", "Rara e informale", "Annuale basata su fatturati", "Monitoraggio costante quote mercato", "Benchmarking data-driven proattivo"]),
        ("Sistema di Delega", ["Nessuna delega operativa", "Solo compiti semplici", "Capi area con autonomia limitata", "Responsabilità di budget ai manager", "Direzione generale autonoma"]),
        ("Passaggio Generazionale", ["Argomento tabù", "Discussioni informali", "Successori individuati", "Piano di affiancamento attivo", "Formalizzato con patti di famiglia"])
    ],
    'Digitalizzazione': [
        ("Infrastruttura IT", ["Obsolescente", "Base (Mail e Office)", "Server locale gestito", "Cloud ibrido", "Infrastruttura Full Cloud/SaaS"]),
        ("ERP/Gestionale", ["Solo fatturazione", "Contabilità base", "Software settoriale specifico", "ERP integrato (Prod/Mag)", "Ecosistema interconnesso e API"]),
        ("Processi Paperless", ["100% Cartaceo", "Pochi PDF/Scansioni", "Misto (Archiviazione digitale)", "Quasi tutto digitale", "100% digitale con Workflow automatici"]),
        ("Cybersecurity", ["Solo Antivirus free", "Backup saltuari", "Firewall e Backup Cloud", "Policy e Audit regolari", "SOC 24/7 e Disaster Recovery"]),
        ("Presenza Web/Marketing", ["Assente", "Sito vetrina statico", "Sito aggiornato e Social", "Strategia ADS e SEO attiva", "Lead generation automatizzata"]),
        ("Innovazione (AI/IoT)", ["Nessuna", "Uso sporadico AI", "Sperimentazione in un'area", "Integrata stabilmente", "Business Model AI-driven"])
    ],
    'Gestione HR': [
        ("Welfare Aziendale", ["Assente", "Rimborsi spese minimi", "Convenzioni base", "Piattaforma Welfare attiva", "Benefit evoluti e personalizzati"]),
        ("Sistemi di Valutazione", ["Nessuno", "Basata su sensazioni", "Colloquio annuale", "MBO correlati a KPI", "Feedback continuo 360°"]),
        ("Retention e Turnover", ["Fuga di talenti frequente", "Turnover nella media", "Bonus sporadici", "Employer Branding attivo", "Azienda certificata 'Top Employer'"]),
        ("Clima Aziendale", ["Tensioni frequenti", "Ignorato sistematicamente", "Rilevato saltuariamente", "Indagine annuale strutturata", "Monitoraggio continuo benessere"]),
        ("Piani di Formazione", ["Solo obbligatoria", "Corsi tecnici rari", "Budget annuo definito", "Piani di crescita individuali", "Academy aziendale interna"]),
        ("Flessibilità/Smart Working", ["Presenza rigida", "Permessi rari", "Flessibilità oraria", "Smart working strutturato", "Lavoro per obiettivi/Anywhere"])
    ],
    'Finanza & Investimenti': [
        ("Pianificazione Finanziaria", ["Nessuna", "Saldo banca quotidiano", "Cash flow mensile", "Previsionale a 6 mesi", "Software tesoreria predittiva"]),
        ("Finanza Agevolata", ["Mai utilizzata", "Rara e casuale", "Utilizzo per bandi semplici", "Monitoraggio attivo bandi", "Pianificazione strategica bandi"]),
        ("Rating Bancario", ["Sconosciuto", "Vago/Informale", "Controllato annualmente", "Monitorato trimestralmente", "Ottimizzazione attiva merito"]),
        ("Analisi Marginalità", ["Solo utile a fine anno", "Stime per macro-prodotto", "Calcolo per singola commessa", "Analisi analitica real-time", "Analisi predittiva margini"]),
        ("Gestione Credito", ["Reattiva (si aspetta)", "Solleciti sporadici", "Procedura scritta definita", "Ufficio recupero crediti", "Assicurazione credito e automazione"]),
        ("Investimenti R&S", ["0% Fatturato", "Solo reattiva", "1-2% del fatturato", "5% del fatturato", ">5% con brevetti/IP"])
    ],
    'Sostenibilità (ESG)': [
        ("Cultura ESG", ["Sconosciuta", "Solo obblighi legge", "Iniziative isolate", "Integrazione piano industriale", "Rating ESG certificato"]),
        ("Impatto Ambientale", ["Nessuna misura", "Differenziata base", "Monitoraggio consumi", "Carbon Footprint calcolata", "Target Net Zero e ISO 14001"]),
        ("Inclusione e Diversità", ["Nessuna policy", "Sensibilità generica", "Donne in ruoli chiave", "Policy scritte e monitorate", "Certificazione Parità Genere"]),
        ("Etica e Trasparenza", ["Nessuna", "Leggi base", "Codice Etico adottato", "Bilancio di Sostenibilità", "Società Benefit / B-Corp"]),
        ("Governance", ["Padronale assoluta", "Famigliare semplice", "Consiglio di Amministrazione", "Presenza di Indipendenti", "Modello governance evoluto"]),
        ("Catena Fornitura ESG", ["Solo prezzo", "Vicinanza", "Richiesta autocertificazioni", "Audit ESG sui fornitori", "Solo fornitori certificati"])
    ],
    'Protezione Legale': [
        ("Modello 231", ["Assente", "In fase di studio", "Adottato versione base", "Aggiornato costantemente", "ODV attivo e indipendente"]),
        ("Privacy (GDPR)", ["Nomine base", "Documentazione obsoleta", "Conformità aggiornata", "Audit periodici", "DPO nominato e processi sicuri"]),
        ("Contrattualistica", ["Accordi verbali", "Modelli web generici", "Contratti standard revisionati", "Contratti ad hoc per cliente", "Legal Management strutturato"]),
        ("Proprietà Intellettuale", ["Nessuna tutela", "Marchio registrato", "Monitoraggio marchi", "Strategia brevettuale", "Asset immateriali a bilancio"]),
        ("Gestione Rischi", ["Emergenziale", "Avvocato al bisogno", "Assicurazione tutela legale", "Prevenzione contrattuale", "Consulenza legale proattiva"]),
        ("Asset Protection", ["Nessuna separazione", "Solo polizze base", "Holding o Fondo Patrimoniale", "Trust o vincoli mirati", "Pianificazione successoria legale"])
    ],
    'Sicurezza sul Lavoro': [
        ("Conformità DVR", ["Scaduto", "Base/Standard", "Aggiornato regolarmente", "Dinamico (Analisi rischi)", "Eccellenza e Benessere"]),
        ("Formazione Sicurezza", ["Incompleta", "Solo base obbligatoria", "Tutti formati in tempo", "Formazione comportamentale", "Cultura della sicurezza diffusa"]),
        ("Salute e Sorveglianza", ["Assente", "Solo visite obbligatorie", "Pianificata regolarmente", "Monitorata con KPI salute", "Programmi prevenzione extra"]),
        ("Gestione DPI/Attrezzi", ["Consegna informale", "Registro cartaceo", "Controllo periodico", "Gestione digitale/SaaS", "DPI innovativi e IoT"]),
        ("Manutenzioni Impianti", ["A guasto", "Registro scadenze", "Programmata", "Software manutenzione", "Manutenzione predittiva"]),
        ("Gestione Appalti", ["Nessun controllo", "Verifica base (DURC)", "Gestione DUVRI corretta", "Coordinamento attivo", "Audit in cantiere costanti"])
    ],
    'Standard & Qualità': [
        ("Certificazione ISO 9001", ["No", "In corso", "Solo formale", "Vissuta come strumento", "Motore di miglioramento"]),
        ("Gestione Processi", ["Nessuna mappatura", "Mappatura parziale", "Procedure scritte core", "Mappatura totale", "Ottimizzazione Lean/Six Sigma"]),
        ("Controllo Qualità", ["A fine processo", "Campionamento", "Sistemico ogni fase", "Controllo dati/sensori", "Zero difetti/Qualità predittiva"]),
        ("Soddisfazione Cliente", ["Solo reclami", "Sondaggio sporadico", "Indagine strutturata", "NPS monitorato", "Co-progettazione"]),
        ("Qualifica Fornitori", ["Solo prezzo", "Storici", "Albo fornitori base", "Rating fornitori", "Partnership e co-development"]),
        ("Gestione Non Conformità", ["Risolte e dimenticate", "Registro Excel", "Analisi cause radice", "Azioni correttive efficaci", "Prevenzione statistica"])
    ],
    'Sviluppo Competenze': [
        ("Analisi Gap Competenze", ["Mai fatta", "Basata su urgenze", "Su richiesta dipendenti", "Annuale strutturata", "Mappatura competenze futuro"]),
        ("Uso Fondi Formazione", ["Mai usati", "Raramente", "Saltuariamente", "Sempre per formazione core", "Ottimizzazione totale budget"]),
        ("Metodi Apprendimento", ["Solo aula", "Affiancamento informale", "E-learning base", "Mix (Blended/Mentoring)", "Social Learning/Academy"]),
        ("Leadership Skills", ["Nessun focus", "Solo per titolare", "Corso sporadico manager", "Percorso coaching strutturato", "Leadership diffusa"]),
        ("Piani di Carriera", ["Assenti", "Solo anzianità", "Crescita su opportunità", "Percorsi chiari definiti", "Meritocrazia trasparente"]),
        ("Mindset Innovativo", ["Resistenza al cambio", "Timore dell'errore", "Alcuni pionieri", "Apertura al test/fallimento", "Innovazione nel DNA"])
    ]
}

# --- 5. LOGICA DI CALCOLO E AI ---
def genera_consulenza_nexta(punteggi, info_azienda):
    # Identifica le 3 aree con punteggio più basso
    peggiori = sorted(punteggi.items(), key=lambda x: x[1])[:3]
    
    prompt = f"""
    Agisci come Senior Partner di NextaHub. Analizza l'azienda {info_azienda['azienda']} (Settore: {info_azienda['settore']}).
    Punteggi medi ottenuti (1-5): {punteggi}.
    Aree critiche: {peggiori}.
    Catalogo Servizi NextaHub: {SERVIZI_NEXTA}.
    
    Genera un report consulenziale professionale che:
    1. Analizzi il rischio di mercato per il settore {info_azienda['settore']} con questi gap.
    2. Proponga soluzioni specifiche dal catalogo NextaHub per le aree critiche.
    3. Definisca una roadmap di intervento a 6-12 mesi.
    Tono: Autorevole, Proattivo, Formattazione Markdown.
    """
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(prompt).text
    except:
        # Fallback se l'API non funziona o manca la chiave
        res = "## 🎯 Analisi Strategica Preliminare\n\n"
        for area, score in peggiori:
            res += f"### 🔴 Criticità: {area} (Rating: {score:.1f}/5)\n"
            res += f"- **Rilevazione:** Il punteggio è inferiore al benchmark di settore.\n"
            res += f"- **Soluzione Consigliata:** {SERVIZI_NEXTA.get(area)}\n\n"
        return res + "\n*Nota: Analisi generata tramite motore logico interno.*"

# --- 6. GESTIONE SESSIONE ---
if 'page' not in st.session_state: st.session_state.page = "Anagrafica"
if 'clienti' not in st.session_state: st.session_state.clienti = {}
if 'current_piva' not in st.session_state: st.session_state.current_piva = None

# --- 7. INTERFACCIA - SIDEBAR ---
with st.sidebar:
    st.image(LOGO_URL, width=200)
    st.markdown("### 🛠️ Suite Gestionale")
    if st.button("🏢 1. Anagrafica Cliente", use_container_width=True): st.session_state.page = "Anagrafica"
    if st.button("📝 2. Esegui Assessment", use_container_width=True): st.session_state.page = "Questionario"
    if st.button("📊 3. Report & Gap Analysis", use_container_width=True): st.session_state.page = "Valutazione"
    if st.button("📁 4. Archivio Storico", use_container_width=True): st.session_state.page = "Archivio"
    st.markdown("---")
    if st.session_state.current_piva:
        cl = st.session_state.clienti[st.session_state.current_piva]['info']
        st.success(f"📌 **In uso:** {cl['azienda']}")

# --- 8. PAGINA 1: ANAGRAFICA COMPLETA ---
if st.session_state.page == "Anagrafica":
    st.title("🏢 Setup Anagrafica Cliente")
    with st.form("form_anagrafica_estesa"):
        col1, col2 = st.columns(2)
        with col1:
            rag_soc = st.text_input("Ragione Sociale")
            p_iva = st.text_input("Partita IVA / Codice Univoco")
            indirizzo_via = st.text_input("Via/Piazza")
            indirizzo_civico = st.text_input("Civico")
            indirizzo_cap = st.text_input("CAP")
        with col2:
            indirizzo_comune = st.text_input("Comune/Paese")
            indirizzo_prov = st.text_input("Provincia (Sigla)")
            settore = st.selectbox("Settore Business", list(BENCHMARK_DATI.keys()))
            referente = st.text_input("Nome Referente Aziendale")
            dimensione = st.select_slider("Classe Dimensionale", options=["Micro", "Piccola", "Media", "Grande"])
        
      
if st.form_submit_button("Crea Fascicolo"):
    if rag_soc and p_iva:
        st.session_state.clienti[p_iva] = {
            "info": {
                "azienda": rag_soc,  # <--- Deve chiamarsi 'azienda'
                "piva": p_iva,
                "via": indirizzo_via,
                "civico": indirizzo_civico,
                "cap": indirizzo_cap,
                "comune": indirizzo_comune,
                "provincia": indirizzo_prov,
                "settore": settore,
                "referente": referente,
                "dimensione": dimensione
            },
            "assessments": []
        }
        st.session_state.current_piva = p_iva
        st.session_state.page = "Questionario"
        st.rerun()
            else:
                st.error("Ragione Sociale e P.IVA sono obbligatori.")

# --- 9. PAGINA 2: QUESTIONARIO 54 DOMANDE ---
elif st.session_state.page == "Questionario":
    piva = st.session_state.current_piva
    if not piva: 
        st.warning("Seleziona o crea un cliente in Anagrafica."); st.stop()
    
    st.title(f"📝 Assessment Strategico: {st.session_state.clienti[piva]['info']['azienda']}")
    st.info("Rispondi a tutte le 54 domande per generare l'analisi dei gap.")
    
    tabs = st.tabs(list(DOMANDE_MATRICE.keys()))
    temp_scores = {}

    for i, area in enumerate(DOMANDE_MATRICE.keys()):
        with tabs[i]:
            st.subheader(f"Analisi {area}")
            sc_area = []
            for j, (domanda, opzioni) in enumerate(DOMANDE_MATRICE[area]):
                st.markdown(f"**{j+1}. {domanda}**")
                val = st.radio(f"Scegli per {domanda}", options=[1, 2, 3, 4, 5], 
                              format_func=lambda x: f"{x}: {opzioni[x-1]}", 
                              key=f"q_{piva}_{area}_{j}", label_visibility="collapsed")
                sc_area.append(val)
            temp_scores[area] = sum(sc_area) / len(sc_area)
    
    if st.button("✅ Salva e Calcola Report AI", use_container_width=True):
        new_entry = {
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "punteggi": temp_scores,
            "analisi_ai": ""
        }
        st.session_state.clienti[piva]['assessments'].append(new_entry)
        st.session_state.page = "Valutazione"
        st.rerun()

# --- 10. PAGINA 3: REPORT & AGENTE AI ---
elif st.session_state.page == "Valutazione":
    st.title(f"📊 Report Strategico: {cl['info']['azienda']}")
    # Nuova riga per indirizzo
    st.caption(f"📍 Sede: {cl['info']['via']} {cl['info']['civico']}, {cl['info']['cap']} - {cl['info']['comune']} ({cl['info']['provincia']})")
    piva = st.session_state.current_piva
    if not piva or piva not in st.session_state.clienti:
        st.warning("Seleziona un cliente valido in Anagrafica.")
        st.stop()
        
    cl = st.session_state.clienti[piva]
    info = cl.get('info', {}) # Recupera il dizionario info in sicurezza
    
    # Visualizzazione sicura dei dati
    nome_azienda = info.get('azienda', 'Azienda non definita')
    st.title(f"📊 Report Strategico: {nome_azienda}")
    
    # Mostra l'indirizzo solo se i campi esistono
    if 'via' in info:
        st.caption(f"📍 Sede: {info.get('via')} {info.get('civico')}, {info.get('cap')} - {info.get('comune')} ({info.get('provincia')})")
    else:
        st.caption(f"📍 Settore: {info.get('settore', 'Non specificato')}")
    
    # Grafico Radar
    categories = list(ass['punteggi'].keys())
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=list(ass['punteggi'].values()), theta=categories, fill='toself', name='Situazione Attuale', line_color='#e63946'))
    bench_vals = [BENCHMARK_DATI[cl['info']['settore']][c] for c in categories]
    fig.add_trace(go.Scatterpolar(r=bench_vals, theta=categories, name='Benchmark Settore', line_color='gray', line_dash='dash'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), height=600)
    st.plotly_chart(fig, use_container_width=True)

    # Gap Analysis Numerica
    st.subheader("📋 Analisi Numerica dei Gap")
    gap_data = []
    for cat in categories:
        gap = ass['punteggi'][cat] - BENCHMARK_DATI[cl['info']['settore']][cat]
        gap_data.append({"Area": cat, "Score": f"{ass['punteggi'][cat]:.2f}", "Benchmark": f"{BENCHMARK_DATI[cl['info']['settore']][cat]:.2f}", "Gap": f"{gap:+.2f}"})
    st.table(pd.DataFrame(gap_data))

    # Agente AI
    st.markdown("---")
    st.subheader("🤖 Agente AI NextaHub")
    if not ass['analisi_ai']:
        if st.button("🪄 Elabora Consulenza con AI"):
            with st.spinner("L'AI sta analizzando i dati..."):
                ass['analisi_ai'] = genera_consulenza_nexta(ass['punteggi'], cl['info'])
                st.rerun()
    else:
        st.markdown(ass['analisi_ai'])

# --- 11. PAGINA 4: ARCHIVIO STORICO ---
elif st.session_state.page == "Archivio":
    st.title("📁 Archivio Storico Clienti")
    if not st.session_state.clienti:
        st.info("Nessun cliente registrato.")
    else:
        for p, dati in st.session_state.clienti.items():
            with st.expander(f"🏢 {dati['info']['azienda']} (PI: {p})"):
                st.write(f"**Settore:** {dati['info']['settore']} | **Referente:** {dati['info']['referente']}")
                if not dati['assessments']:
                    st.write("Nessuna analisi effettuata.")
                for i, a in enumerate(dati['assessments']):
                    col_t, col_b = st.columns([4, 1])
                    col_t.write(f"Analisi del {a['data']}")
                    if col_b.button("Apri", key=f"arch_{p}_{i}"):
                        st.session_state.current_piva = p
                        st.session_state.page = "Valutazione"
                        st.rerun()
