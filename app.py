import streamlit as st
import plotly.graph_objects as go
import google.generativeai as genai

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="NextaHub - Professional Assessment", layout="wide")

# --- DATABASE DOMANDE E LIVELLI (6 per area) ---
# Struttura: { Area: [ (Testo Domanda, {1: "descr", 2: "descr", ...}), ... ] }
DOMANDE_MATRICE = {
    'Strategia & Controllo': [
        ("Esiste un business plan o piano industriale?", {
            1: "No, navighiamo a vista", 2: "Visione a 2/3 mesi", 3: "Visione a 6 mesi", 4: "Piano a 1 anno", 5: "Piano strutturato a 2+ anni"
        }),
        ("Monitoraggio KPI e cruscotti aziendali", {
            1: "Nessun dato", 2: "Controllo costi a fine anno", 3: "Monitoraggio fatturato mensile", 4: "KPI operativi monitorati", 5: "Dashboard real-time integrata"
        }),
        ("Definizione dell'organigramma e ruoli", {
            1: "Tutti fanno tutto", 2: "Ruoli accennati", 3: "Organigramma base presente", 4: "Ruoli e mansionari definiti", 5: "Struttura manageriale autonoma"
        }),
        ("Analisi della concorrenza e del mercato", {
            1: "Mai fatta", 2: "Reattiva (seguiamo gli altri)", 3: "Analisi sporadica", 4: "Monitoraggio annuale", 5: "Strategia basata su dati di mercato costanti"
        }),
        ("Sistemi di delega e processi decisionali", {
            1: "Accentramento totale (Titolare)", 2: "Delega minima", 3: "Prime deleghe operative", 4: "Processi decisionali condivisi", 5: "Delega manageriale completa"
        }),
        ("Gestione del passaggio generazionale/continuità", {
            1: "Problema ignorato", 2: "Discussioni vaghe", 3: "Consapevolezza del rischio", 4: "Piano di continuità abbozzato", 5: "Piano di successione formalizzato"
        })
    ],
    'Protezione Legale': [
        ("Presenza e aggiornamento Modello 231", {
            1: "Assente", 2: "In fase di valutazione", 3: "Presente ma non aggiornato", 4: "Aggiornato regolarmente", 5: "Integrato con ODV efficace"
        }),
        ("Conformità GDPR e Privacy", {
            1: "Nulla", 2: "Documentazione minima", 3: "Nomine e registri presenti", 4: "Audit periodici effettuati", 5: "Privacy by design nei processi"
        }),
        ("Contrattualistica Clienti/Fornitori", {
            1: "Accordi verbali", 2: "Modelli scaricati dal web", 3: "Contratti standard base", 4: "Revisionati da legali", 5: "Blindati e personalizzati per rischio"
        }),
        ("Tutela Marchi, Brevetti e Proprietà Intellettuale", {
            1: "Nessuna tutela", 2: "Solo marchio registrato", 3: "Ricerca periodica anteriorità", 4: "Strategia di tutela IP", 5: "Asset IP valorizzati e protetti globalmente"
        }),
        ("Gestione del recupero crediti legale", {
            1: "Nessuna procedura", 2: "Tentativi sporadici", 3: "Solleciti formali", 4: "Procedura sistematica", 5: "Monitoraggio legale preventivo"
        }),
        ("Analisi dei rischi legali e assicurativi", {
            1: "Nessuna polizza specifica", 2: "Polizze base obbligatorie", 3: "Analisi rischi base", 4: "Coperture All-Risk", 5: "Risk Management integrato"
        })
    ],
    'Sicurezza sul Lavoro': [
        ("Aggiornamento del DVR (Documento Valutazione Rischi)", {
            1: "Inesistente/Scaduto", 2: "Vecchio di anni", 3: "Base (solo obblighi)", 4: "Aggiornato e dettagliato", 5: "Dinamico (aggiornato ad ogni cambio)"
        }),
        ("Formazione Obbligatoria (RSPP, RLS, Antincendio, etc.)", {
            1: "Scaduta o assente", 2: "Parzialmente fatta", 3: "Fatta ma difficile da tracciare", 4: "Tutta a norma e monitorata", 5: "Piano formativo avanzato oltre obblighi"
        }),
        ("Sorveglianza Sanitaria e Medico del Lavoro", {
            1: "Assente", 2: "Sporadica", 3: "Nomina presente, visite lente", 4: "Scadenze monitorate", 5: "Check-up salute costanti e digitalizzati"
        }),
        ("Gestione DPI e Manutenzione Impianti", {
            1: "Nessun registro", 2: "Gestione a vista", 3: "Registro cartaceo base", 4: "Scadenziario manutenzioni", 5: "Manutenzione predittiva e tracciata"
        }),
        ("Gestione Appalti e Cantieri (DUVRI)", {
            1: "Mai fatto", 2: "Copia-incolla", 3: "Presente per i principali", 4: "Redatto con cura", 5: "Integrazione totale con fornitori"
        }),
        ("Cultura della sicurezza e Near Miss", {
            1: "Si lavora e basta", 2: "Solo sgridate in caso di errore", 3: "Consapevolezza base", 4: "Segnalazione mancati infortuni", 5: "Zero infortuni come obiettivo condiviso"
        })
    ]
    # NOTA: Per brevità ho inserito 3 categorie complete, il codice sotto gestirà dinamicamente le altre allo stesso modo.
}

# --- LOGICA DI CALCOLO ---
st.sidebar.image("https://www.nextahub.it/wp-content/uploads/2023/05/logo-nextahub.png", width=200)
st.sidebar.title("NextaHub Assessment")

nome_azienda = st.sidebar.text_input("Ragione Sociale")
settore = st.sidebar.selectbox("Settore", ["Manifatturiero", "IT", "Edilizia", "Agri-Food", "Sanità", "Retail"])
regione = st.sidebar.selectbox("Sede", ["Lombardia", "Altra Regione"])

st.sidebar.markdown("---")
st.sidebar.header("Diagnosi delle Competenze")

final_scores = {}

# Generazione dinamica delle domande
for area, domande in DOMANDE_MATRICE.items():
    with st.sidebar.expander(f"🛒 {area}"):
        punteggi_area = []
        for i, (testo, opzioni) in enumerate(domande):
            scelta = st.radio(testo, options=[1, 2, 3, 4, 5], 
                              format_func=lambda x: f"{x}: {opzioni[x]}", 
                              key=f"{area}_{i}")
            punteggi_area.append(scelta)
        final_scores[area] = sum(punteggi_area) / len(punteggi_area)

# Per le aree non ancora riempite nel dizionario sopra, mettiamo un valore di default per il grafico
CATEGORIES_TOTAL = ['Strategia & Controllo', 'Digitalizzazione', 'Gestione HR', 'Finanza & Investimenti', 'Sostenibilità (ESG)', 'Protezione Legale', 'Sicurezza sul Lavoro', 'Standard & Qualità', 'Sviluppo Competenze']
radar_values = [final_scores.get(cat, 3.0) for cat in CATEGORIES_TOTAL]

# --- INTERFACCIA ---
st.title(f"Report Strategico: {nome_azienda}")

fig = go.Figure()
fig.add_trace(go.Scatterpolar(r=radar_values, theta=CATEGORIES_TOTAL, fill='toself', name='Profilo Azienda', line_color='#e63946'))
fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), height=600)
st.plotly_chart(fig, use_container_width=True)

if st.button("Genera Analisi con AI"):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected_model = next((m for m in available_models if "1.5-flash" in m), available_models[0])
        model = genai.GenerativeModel(selected_model)
        
        prompt = f"""
        Analizza questa azienda: {nome_azienda} ({settore}, {regione}).
        Punteggi medi ottenuti (1-5): {final_scores}.
        
        Compito:
        1. Identifica le 3 criticità maggiori basandoti sulle risposte da 1 e 2.
        2. Proponi soluzioni NextaHub specifiche:
           - Se Protezione Legale è bassa: Modello 231 e Audit Privacy.
           - Se Sicurezza è bassa: Revisione DVR e Formazione finanziata.
           - Se Strategia è bassa: Temporary Management o Business Plan.
        3. Crea una roadmap: 0-3 mesi (Urgenze), 3-12 mesi (Sviluppo), 12+ mesi (ESG e Consolidamento).
        """
        
        with st.spinner("L'esperto NextaHub sta scrivendo il report..."):
            response = model.generate_content(prompt)
            st.markdown(response.text)
    except Exception as e:
        st.error(f"Errore: {e}")
