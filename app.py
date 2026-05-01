import streamlit as st
import plotly.graph_objects as go
import google.generativeai as genai

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="NextaHub - Business Assessment Tool", layout="wide")

# --- DATABASE DOMANDE PER CATEGORIA ---
CHECKLISTS = {
    'Strategia & Controllo': [
        "Esiste un business plan aggiornato?",
        "Vengono monitorati KPI mensili?",
        "C'è un sistema di controllo di gestione?"
    ],
    'Digitalizzazione': [
        "L'azienda usa un ERP/CRM integrato?",
        "I processi sono paperless?",
        "Esiste una strategia di cybersecurity?"
    ],
    'Gestione HR': [
        "Esiste un piano di welfare aziendale?",
        "C'è una bassa rotazione del personale?",
        "Vengono fatte valutazioni delle performance?"
    ],
    'Finanza & Investimenti': [
        "L'azienda usa bandi o finanza agevolata?",
        "Il rating bancario è monitorato?",
        "Esiste una pianificazione dei flussi di cassa?"
    ],
    'Sostenibilità (ESG)': [
        "Esiste un bilancio di sostenibilità?",
        "L'azienda ha certificazioni ambientali?",
        "Esistono politiche di parità di genere?"
    ],
    'Protezione Legale': [
        "Il Modello 231 è presente e aggiornato?",
        "La contrattualistica clienti/fornitori è blindata?",
        "Il GDPR è pienamente conforme?"
    ],
    'Sicurezza sul Lavoro': [
        "Il DVR è aggiornato all'ultimo anno?",
        "Tutta la formazione obbligatoria è a norma?",
        "Sono stati fatti audit sulla sicurezza negli ultimi 12 mesi?"
    ],
    'Standard & Qualità': [
        "L'azienda è certificata ISO 9001?",
        "Esiste un manuale delle procedure operative?",
        "Vengono gestite le non conformità in modo sistematico?"
    ],
    'Sviluppo Competenze': [
        "Esiste un piano formativo annuale?",
        "Si utilizzano Fondi Interprofessionali?",
        "C'è formazione specifica su soft skills o digitale?"
    ]
}

BENCHMARKS = {
    "Manifatturiero": [3.5, 3.8, 3.2, 3.0, 3.5, 4.0, 4.2, 3.5, 3.0],
    "IT & Software": [4.5, 4.8, 4.0, 3.5, 3.0, 4.5, 4.0, 3.8, 4.2],
    "Edilizia & Costruzioni": [2.5, 2.8, 3.0, 3.5, 2.5, 3.8, 4.5, 4.2, 2.5],
    "Agri-Food": [3.0, 3.2, 3.5, 3.8, 4.0, 3.5, 4.0, 3.2, 3.0],
    "Sanità & Pharma": [4.0, 4.2, 4.5, 3.5, 3.8, 4.8, 4.8, 4.5, 4.0],
    "Retail & GDO": [3.8, 4.0, 3.5, 3.2, 3.5, 3.5, 3.8, 3.0, 3.5]
}

# --- SIDEBAR ---
st.sidebar.image("https://www.nextahub.it/wp-content/uploads/2023/05/logo-nextahub.png", width=200)
st.sidebar.title("Check-up Scientifico")

nome_azienda = st.sidebar.text_input("Ragione Sociale")
settore = st.sidebar.selectbox("Settore", list(BENCHMARKS.keys()))
regione = st.sidebar.selectbox("Sede", ["Lombardia", "Altra Regione"])

st.sidebar.markdown("---")
st.sidebar.subheader("Questionario Diagnostico")

# Calcolo degli score basato sulle risposte
final_scores = []
for cat, questions in CHECKLISTS.items():
    with st.sidebar.expander(f"{cat}"):
        count = 0
        for q in questions:
            if st.checkbox(q, key=f"{cat}_{q}"):
                count += 1
        # Trasformiamo il conteggio (0-3) in uno score (1-5)
        calculated_score = 1.0 + (count * 1.33) 
        final_scores.append(round(calculated_score, 1))

note_commerciale = st.sidebar.text_area("Note aggiuntive")

# --- MAIN PAGE ---
st.title(f"Analisi Strategica: {nome_azienda if nome_azienda else 'Nuovo Cliente'}")

# Grafico
fig = go.Figure()
fig.add_trace(go.Scatterpolar(r=BENCHMARKS[settore], theta=list(CHECKLISTS.keys()), fill='toself', name='Benchmark', line_color='gray', opacity=0.4))
fig.add_trace(go.Scatterpolar(r=final_scores, theta=list(CHECKLISTS.keys()), fill='toself', name='Situazione Attuale', line_color='#e63946'))
fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), height=600)
st.plotly_chart(fig, use_container_width=True)

# --- LOGICA AI ---
if st.button("Genera Roadmap e Offerta NextaHub"):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected_model = next((m for m in available_models if "1.5-flash" in m), available_models[0])
        model = genai.GenerativeModel(selected_model)
        
        context = f"""
        Sei il Senior Advisor NextaHub. In base alle risposte negative del questionario, genera una Roadmap.
        REGOLE:
        1. Se lo score in 'Sicurezza' o 'Protezione Legale' è basso, imponi Adeguamento 81/08 o Modello 231 in FASE 1.
        2. Se 'Sviluppo Competenze' è basso, proponi Bando Formazione Continua o Fondi Interprofessionali.
        3. Se 'Qualità' è basso, scrivi: "Attivazione percorso ISO 9001".
        4. Fissa la valutazione ESG a 12 mesi se le urgenze sono alte.
        5. Modello consigliato: ELITE se >3 aree critiche, FLEX se 1-2 aree, ENTRY se solo urgenza legale.
        """
        
        dati = f"Azienda: {nome_azienda}. Score: {dict(zip(CHECKLISTS.keys(), final_scores))}. Note: {note_commerciale}"
        
        with st.spinner("L'IA sta analizzando le tue risposte..."):
            response = model.generate_content(context + "\n\n" + dati)
            st.markdown(response.text)
            st.download_button("Scarica Report Professionale", response.text, file_name=f"Roadmap_{nome_azienda}.txt")
    except Exception as e:
        st.error(f"Errore: {e}")
