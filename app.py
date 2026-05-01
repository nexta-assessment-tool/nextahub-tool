import streamlit as st
import plotly.graph_objects as go
import google.generativeai as genai

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="NextaHub - Business Assessment Tool", layout="wide")

# --- DATABASE BENCHMARK (Settori) ---
BENCHMARKS = {
    "Manifatturiero": [3.5, 3.8, 3.2, 3.0, 3.5, 4.0, 4.2, 3.5, 3.0],
    "IT & Software": [4.5, 4.8, 4.0, 3.5, 3.0, 4.5, 4.0, 3.8, 4.2],
    "Edilizia & Costruzioni": [2.5, 2.8, 3.0, 3.5, 2.5, 3.8, 4.5, 4.2, 2.5],
    "Agri-Food": [3.0, 3.2, 3.5, 3.8, 4.0, 3.5, 4.0, 3.2, 3.0],
    "Sanità & Pharma": [4.0, 4.2, 4.5, 3.5, 3.8, 4.8, 4.8, 4.5, 4.0],
    "Retail & GDO": [3.8, 4.0, 3.5, 3.2, 3.5, 3.5, 3.8, 3.0, 3.5]
}

CATEGORIES = [
    'Strategia & Controllo', 'Digitalizzazione', 'Gestione HR', 
    'Finanza & Investimenti', 'Sostenibilità (ESG)', 'Protezione Legale', 
    'Sicurezza sul Lavoro', 'Standard & Qualità', 'Sviluppo Competenze'
]

# --- SIDEBAR: ANAGRAFICA E DIAGNOSTICA ---
st.sidebar.image("https://www.nextahub.it/wp-content/uploads/2023/05/logo-nextahub.png", width=200)
st.sidebar.title("Check-up Aziendale")

with st.sidebar.expander("Anagrafica Cliente", expanded=True):
    nome_azienda = st.sidebar.text_input("Ragione Sociale")
    settore = st.sidebar.selectbox("Settore di appartenenza", list(BENCHMARKS.keys()))
    regione = st.sidebar.selectbox("Sede Operativa", ["Lombardia", "Altra Regione"])

st.sidebar.subheader("Valutazione Gap (1=Critico, 5=Eccellente)")
scores = []
for cat in CATEGORIES:
    score = st.sidebar.slider(f"{cat}", 1.0, 5.0, 3.0, 0.5)
    scores.append(score)

note_commerciale = st.sidebar.text_area("Note del commerciale (obiettivi, clima, criticità)")

# --- LOGICA GRAFICA ---
st.title(f"Analisi Strategica: {nome_azienda if nome_azienda else 'Nuovo Cliente'}")

fig = go.Figure()
fig.add_trace(go.Scatterpolar(
    r=BENCHMARKS[settore],
    theta=CATEGORIES,
    fill='toself',
    name='Benchmark Settore',
    line_color='gray',
    opacity=0.5
))
fig.add_trace(go.Scatterpolar(
    r=scores,
    theta=CATEGORIES,
    fill='toself',
    name='Profilo Azienda',
    line_color='#1f77b4'
))
fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
    showlegend=True,
    height=600
)
st.plotly_chart(fig, use_container_width=True)

# --- LOGICA AI GENERATIVA ---
if st.button("Genera Analisi Strategica NextaHub"):
    if not nome_azienda:
        st.error("Per favore, inserisci la Ragione Sociale dell'azienda.")
    elif "GEMINI_API_KEY" not in st.secrets:
        st.error("Chiave API non trovata! Inseriscila nei Secrets di Streamlit come GEMINI_API_KEY.")
    else:
        try:
            # Configurazione IA
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # PROMPT STRATEGICO (Il tuo metodo di vendita)
            context = f"""
            Sei il Senior Advisor di NextaHub con 20 anni di esperienza nella consulenza aziendale.
            Analizza l'azienda {nome_azienda} ({settore}, {regione}).
            
            LOGICA DI ANALISI:
            1. TRATTA GLI OBBLIGHI COME TALI: Se 'Protezione Legale' o 'Sicurezza' hanno score bassi, evidenzia le responsabilità civili/penali (GDPR, 231, 81/08).
            2. LEVA ESG: Collega l'ESG a Certificazioni ISO, Welfare (Social) e Bilancio di Sostenibilità.
            3. EFFICIENZA ENERGETICA: Se i costi sono alti, proponi l'Ingegnere Ambientale/Energy Manager di Nexta.
            4. CROSS-SELLING FINANZIATO: Spiega come la Formazione Finanziata (es. Fondi Interpro o Bandi Lombardia) possa finanziare consulenze tecniche.
            5. MODALITÀ DI ACQUISTO: Suggerisci esplicitamente se il cliente è adatto a:
               - ENTRY (singola commessa)
               - ELITE (canone mensile con tecnico/commerciale dedicato)
               - FLEX (pacchetto prepagato a scalare).

            FORMATO: Report professionale con punti chiave e Roadmap d'azione.
            """
            
            input_prompt = f"Dati Diagnostici: {dict(zip(CATEGORIES, scores))}. Note: {note_commerciale}"
            
            with st.spinner("L'intelligenza artificiale NextaHub sta elaborando la strategia..."):
                response = model.generate_content(context + "\n\n" + input_prompt)
                st.success("Analisi Completata con Successo!")
                st.markdown(response.text)
                
                st.download_button("Scarica Testo Report", response.text, file_name=f"Report_{nome_azienda}.txt")
                
        except Exception as e:
            st.error(f"Errore tecnico durante la generazione: {str(e)}")
