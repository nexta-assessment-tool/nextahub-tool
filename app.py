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
            # Configurazione IA con l'ultima versione del modello
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel(model_name='gemini-1.5-flash-latest')
            
            # PROMPT STRATEGICO BASATO SUI 20 ANNI DI ESPERIENZA NEXTA
            context = f"""
            Sei il Senior Advisor di NextaHub. Analizza l'azienda {nome_azienda} ({settore}, {regione}).
            
            OBIETTIVI DELL'ANALISI:
            1. TRADUZIONE DEI GAP: Trasforma ogni score basso in un servizio NextaHub (es. Protezione Legale bassa = Modello 231/GDPR).
            2. CROSS-SELLING: Spiega come la 'Formazione Finanziata' (Fondi Interpro o bandi Lombardia) possa finanziare Certificazioni ISO o Welfare.
            3. ESG & ENERGIA: Collega la sostenibilità al rating bancario e proponi l'Energy Manager Nexta per ridurre i costi.
            4. MODELLO COMMERCIALE: Consiglia esplicitamente se proporre un contratto:
               - ENTRY (Singolo intervento urgente)
               - ELITE (Canone mensile, consulente dedicato)
               - FLEX (Pacchetto ore/commesse a scalare).
            
            Tono: Autorevole, pratico, orientato alla vendita di valore.
            """
            
            input_prompt = f"Dati Diagnostici: {dict(zip(CATEGORIES, scores))}. Note Commerciale: {note_commerciale}"
            
            with st.spinner("L'AI di NextaHub sta generando il report..."):
                response = model.generate_content(context + "\n\n" + input_prompt)
                
                if response:
                    st.success("Analisi Completata!")
                    st.markdown(response.text)
                    st.download_button("Scarica Report", response.text, file_name=f"Report_Nexta_{nome_azienda}.txt")
                else:
                    st.error("Risposta vuota dall'IA. Riprova.")
                    
        except Exception as e:
            st.error(f"Errore tecnico: {str(e)}")
            st.info("Suggerimento: Controlla che la chiave API nei Secrets sia corretta e non abbia spazi.")
