import streamlit as st
import plotly.graph_objects as go
import google.generativeai as genai

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="NextaHub - Business Assessment Tool", layout="wide")

# --- DATABASE BENCHMARK ---
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

# --- SIDEBAR ---
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

note_commerciale = st.sidebar.text_area("Note del commerciale")

# --- GRAFICA RADAR ---
st.title(f"Analisi Strategica: {nome_azienda if nome_azienda else 'Nuovo Cliente'}")
fig = go.Figure()
fig.add_trace(go.Scatterpolar(r=BENCHMARKS[settore], theta=CATEGORIES, fill='toself', name='Benchmark', line_color='gray', opacity=0.5))
fig.add_trace(go.Scatterpolar(r=scores, theta=CATEGORIES, fill='toself', name='Profilo Azienda', line_color='#1f77b4'))
fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=True, height=600)
st.plotly_chart(fig, use_container_width=True)

# --- LOGICA AI CON AUTO-DETECTION ---
if st.button("Genera Analisi Strategica NextaHub"):
    if not nome_azienda:
        st.error("Inserisci la Ragione Sociale.")
    elif "GEMINI_API_KEY" not in st.secrets:
        st.error("Chiave API mancante nei Secrets!")
    else:
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            
            # Cerca il primo modello disponibile che supporti la generazione di contenuti
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            if not available_models:
                st.error("Nessun modello disponibile trovato per questa API Key.")
            else:
                # Seleziona il modello 1.5 flash se presente, altrimenti il primo della lista
                selected_model = next((m for m in available_models if "1.5-flash" in m), available_models[0])
                model = genai.GenerativeModel(selected_model)
                
                context = f"""
                Sei il Senior Advisor di NextaHub con 20 anni di esperienza. Analizza {nome_azienda} ({settore}, {regione}).
                Focus: Rischi sanzioni (81/08, GDPR), Finanza Agevolata, ESG e Formazione Finanziata.
                Proponi: ENTRY, ELITE o FLEX.
                """
                input_prompt = f"Punteggi: {dict(zip(CATEGORIES, scores))}. Note: {note_commerciale}"
                
                with st.spinner(f"Generazione con {selected_model}..."):
                    response = model.generate_content(context + "\n\n" + input_prompt)
                    st.success("Analisi Completata!")
                    st.markdown(response.text)
                    st.download_button("Scarica Report", response.text, file_name=f"Report_{nome_azienda}.txt")
                    
        except Exception as e:
            st.error(f"Errore di connessione a Google: {str(e)}")
            st.info("Se vedi ancora 404, scrivi 'LISTA' qui in chat così ti spiego come sbloccare i modelli dal tuo pannello Google.")
