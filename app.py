import streamlit as st
import plotly.graph_objects as go
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="NextaHub - CRM & Assessment", layout="wide")

# --- INIZIALIZZAZIONE STORICO ---
if 'storico_analisi' not in st.session_state:
    st.session_state['storico_analisi'] = []

# --- DATABASE DOMANDE (Le stesse 54 del blocco precedente) ---
# [Per brevità qui mantengo la struttura, assicurati di usare il database completo del messaggio precedente]
DOMANDE_MATRICE = {
    'Strategia & Controllo': [
        ("Esiste un business plan o piano industriale?", {1: "No, navighiamo a vista", 2: "Visione a 2/3 mesi", 3: "Visione a 6 mesi", 4: "Piano a 1 anno", 5: "Piano strutturato a 2+ anni"}),
        ("Monitoraggio KPI e cruscotti aziendali", {1: "Nessun dato", 2: "Controllo costi a fine anno", 3: "Monitoraggio fatturato mensile", 4: "KPI operativi monitorati", 5: "Dashboard real-time integrata"}),
        # ... aggiungi le altre 4 domande qui ...
    ],
    # ... Aggiungi tutte le altre aree (Protezione Legale, Sicurezza, etc.) ...
}

st.title("🚀 NextaHub Business Suite")
st.subheader("Anagrafica, Assessment e Roadmap Strategica")

# --- STEP 1: ANAGRAFICA CLIENTE ---
st.markdown("### 1️⃣ Anagrafica Potenziale Cliente")
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        azienda = st.text_input("Ragione Sociale")
        piva = st.text_input("Partita IVA")
    with col2:
        sede = st.text_input("Indirizzo Sede")
        regione = st.selectbox("Regione Operativa", ["Lombardia", "Piemonte", "Veneto", "Emilia-Romagna", "Lazio", "Campania", "Altro"])
    
    settore = st.selectbox("Settore di appartenenza", ["Manifatturiero", "IT & Software", "Edilizia", "Agri-Food", "Retail", "Servizi"])

st.markdown("---")

# --- STEP 2: ASSESSMENT (DOMANDE DIVISE PER SETTORE) ---
st.markdown("### 2️⃣ Questionario di Valutazione (Matrice di Maturità)")
st.info("Rispondi a tutte le domande per sbloccare il diagramma a radar e l'analisi AI.")

final_scores = {}
# Creiamo le schede (tabs) per non affollare la pagina
tabs = st.tabs(list(DOMANDE_MATRICE.keys()))

for i, area in enumerate(DOMANDE_MATRICE.keys()):
    with tabs[i]:
        st.subheader(f"Valutazione: {area}")
        punteggi_area = []
        for j, (testo, opzioni) in enumerate(DOMANDE_MATRICE[area]):
            scelta = st.select_slider(
                testo,
                options=[1, 2, 3, 4, 5],
                format_func=lambda x: f"{x}: {opzioni[x]}",
                key=f"q_{area}_{j}"
            )
            punteggi_area.append(scelta)
        final_scores[area] = sum(punteggi_area) / len(punteggi_area)

st.markdown("---")

# --- STEP 3: RISULTATI E SALVATAGGIO ---
st.markdown("### 3️⃣ Elaborazione e Risultati")

if st.button("🏁 Finalizza Assessment e Genera Radar"):
    if not azienda or not piva:
        st.error("⚠️ Inserisci almeno Ragione Sociale e P.IVA per procedere.")
    else:
        # Visualizzazione Radar
        st.success(f"Analisi per {azienda} completata!")
        
        categories = list(final_scores.keys())
        values = list(final_scores.values())
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=azienda,
            line_color='#e63946'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            showlegend=True,
            title=f"Radar Map: {azienda}"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Salvataggio nello storico locale (sessione)
        analisi_attuale = {
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "azienda": azienda,
            "piva": piva,
            "settore": settore,
            "punteggi": final_scores
        }
        st.session_state['storico_analisi'].append(analisi_attuale)

        # Chiamata all'AI
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            selected_model = next((m for m in available_models if "1.5-flash" in m), available_models[0])
            model = genai.GenerativeModel(selected_model)
            
            prompt = f"Analizza {azienda} ({settore}). PIVA: {piva}. Score: {final_scores}. Genera roadmap 24 mesi e consiglia pacchetto ELITE, FLEX o ENTRY."
            
            with st.spinner("L'AI sta scrivendo il report..."):
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.download_button("Scarica Report Finale", response.text, file_name=f"Report_{azienda}.txt")
        except Exception as e:
            st.error(f"Errore AI: {e}")

st.markdown("---")

# --- STORICO DELLE ANALISI ---
st.markdown("### 📜 Storico Analisi Effettuate")
if st.session_state['storico_analisi']:
    df_storico = pd.DataFrame(st.session_state['storico_analisi'])
    st.table(df_storico[["data", "azienda", "piva", "settore"]])
else:
    st.write("Nessuna analisi salvata in questa sessione.")
