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

st.sidebar.subheader("Valutazione Gap (1=Pessimo, 5=Eccellente)")
scores = []
for cat in CATEGORIES:
    score = st.sidebar.slider(f"{cat}", 1.0, 5.0, 3.0, 0.5)
    scores.append(score)

note_commerciale = st.sidebar.text_area("Note del commerciale (es. obiettivi, clima, criticità)")

# --- LOGICA GRAFICA ---
st.title(f"Analisi Strategica: {nome_azienda}")
st.write(f"Confronto tra il profilo di **{nome_azienda}** e il benchmark medio del settore **{settore}**.")

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
    if not nome_azienda or nome_azienda == "Ragione Sociale":
        st.error("Inserisci il nome dell'azienda!")
    else:
        try:
            if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Chiave non trovata nei Secrets. Assicurati di averla inserita come GEMINI_API_KEY")
    st.stop()
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # IL "CERVELLO" DI NEXTAHUB (Basato sulla tua esperienza)
            context = f"""
            Sei il Senior Fractional Manager di NextaHub con 20 anni di esperienza. 
            L'azienda cliente si chiama {nome_azienda}, opera nel settore {settore} ed è in {regione}.
            
            IL TUO OBIETTIVO:
            Analizza i gap tra i punteggi dell'azienda e il benchmark. Traduci i punteggi bassi in soluzioni NextaHub.
            
            LOGICA DEI SERVIZI (LA TUA CASSETTA DEGLI ATTREZZI):
            1. Se 'Sviluppo Competenze' o 'Gestione HR' sono bassi: Proponi Formazione Specialistica e Finanziata (Fondi Interpro. e se Lombardia 'Formare per Assumere').
            2. Se 'Finanza' è basso: Spingi su Finanza Agevolata, Bandi e Crediti d'Imposta.
            3. Se 'Protezione Legale' o 'Sicurezza' sono bassi: Trattali come OBBLIGHI urgenti (GDPR, 231, 81/08, RSPP, Whistleblowing).
            4. Se 'ESG' è basso: Proponi Assessment ESG, Bilancio Sostenibilità, Energy Manager e Welfare.
            5. Se 'Standard/Qualità' è basso: Proponi ISO e SOA (SOA solo se Edilizia/Impianti).
            6. Se 'Digitalizzazione' è basso: Proponi Software, AI dedicata e Perizie 4.0/5.0.

            STRATEGIA COMMERCIALE:
            - Spiega come la 'Formazione Finanziata' può coprire i costi di altri servizi (es. ISO o Welfare).
            - Suggerisci una delle 3 modalità di acquisto:
                * ENTRY: Per un solo bisogno specifico.
                * ELITE: Canone mensile per un presidio costante (Fractional Manager).
                * FLEX: Pacchetto prepagato a scalare per molti investimenti.
            
            Tono: Professionale, autorevole, orientato alla protezione dell'imprenditore.
            """
            
            input_data = f"Dati diagnosi: {dict(zip(CATEGORIES, scores))}. Note: {note_commerciale}"
            
            with st.spinner("L'AI di NextaHub sta elaborando la strategia..."):
                response = model.generate_content(context + "\n\n" + input_data)
                
            st.success("Analisi Completata")
            st.markdown(response.text)
            
            # Footer per il PDF
            st.download_button("Scarica Report (Copia Testo)", response.text, file_name=f"Analisi_{nome_azienda}.txt")
            
        except Exception as e:
            st.error("Errore: Verifica che la API Key sia corretta nei Secrets di Streamlit.")
