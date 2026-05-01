import streamlit as st
import plotly.graph_objects as go
import google.generativeai as genai
from datetime import datetime
import json

# --- 1. CONFIGURAZIONE PAGINA E API ---
st.set_page_config(page_title="NextaHub Strategic Suite v3.0", layout="wide")

def setup_gemini():
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("⚠️ Configura 'GEMINI_API_KEY' nei Secrets di Streamlit.")
        st.stop()
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

setup_gemini()
LOGO_URL = "https://nextahub.it/wp-content/uploads/2026/02/Nexta_Logo_Def_PiccoloHUB.png"

# --- 2. DATABASE E COSTANTI ---
if 'db_clienti' not in st.session_state:
    st.session_state.db_clienti = {}
if 'page' not in st.session_state:
    st.session_state.page = "Anagrafica"
if 'current_piva' not in st.session_state:
    st.session_state.current_piva = None

SETTORI = ["Agroalimentare", "Moda e Tessile", "Arredo e Design", "Meccanica e Automazione", "Metallurgia", "Automotive", "Chimico e Farmaceutico", "Energia e Utilities", "Costruzioni ed Edilizia", "Elettronica", "Gomma e Materie Plastiche", "Carta e Stampa", "ICT e Digitale", "Logistica e Trasporti", "Turismo e Ristorazione", "Bancario e Assicurativo", "Sanità"]
REGIONI = ["Abruzzo", "Basilicata", "Calabria", "Campania", "Emilia-Romagna", "Friuli-Venezia Giulia", "Lazio", "Liguria", "Lombardia", "Marche", "Molise", "Piemonte", "Puglia", "Sardegna", "Sicilia", "Toscana", "Trentino-Alto Adige", "Umbria", "Valle d'Aosta", "Veneto"]

# --- 3. MATRICE COMPLETA 54 DOMANDE ---
DOMANDE_MATRICE = {
    'Strategia & Controllo': [
        ("Piano Strategico", ["Nessuna visione formalizzata", "Obiettivi comunicati solo verbalmente", "Budget economico annuale definito", "Piano industriale triennale strutturato", "Pianificazione dinamica con analisi di scenario (What-if)"], None),
        ("Monitoraggio KPI", ["Nessun indicatore monitorato", "Analisi saltuaria del solo bilancio civilistico", "Monitoraggio tramite file Excel aggiornati manualmente", "Dashboard di controllo integrate per area aziendale", "Sistemi di Business Intelligence in real-time"], None),
        ("Organigramma e Ruoli", ["Struttura accentrata nel titolare", "Ruoli e responsabilità poco chiari", "Organigramma definito ma poco applicato", "Sistema di deleghe operative e responsabilità chiare", "Manager autonomi con obiettivi di area (Business Unit)"], None),
        ("Analisi Competitor", ["Nessun monitoraggio della concorrenza", "Analisi informale basata su rumors di mercato", "Analisi annuale dei bilanci dei competitor", "Monitoraggio costante di prezzi e quote di mercato", "Analisi data-driven con benchmark di settore continui"], None),
        ("Sistema di Delega", ["Il titolare supervisiona ogni minima decisione", "Deleghe limitate a compiti meramente esecutivi", "Capi area con autonomia operativa limitata", "Responsabilità piena su budget e risorse di funzione", "Direzione autonoma con poteri di firma e spesa"], None),
        ("Passaggio Generazionale", ["Argomento non affrontato (Tabù)", "Discussioni informali senza pianificazione", "Individuazione dei successori e inizio formazione", "Piano di affiancamento strutturato con tutoraggio", "Patti di famiglia o governance duale già definiti"], None)
    ],
    'Digitalizzazione': [
        ("Infrastruttura IT", ["Hardware obsoleto e rischi di fermo macchina", "Postazioni base con software non aggiornati", "Server locale per gestione dati e backup", "Architettura in cloud ibrido protetta", "Infrastruttura Full Cloud scalabile e ridondata"], None),
        ("ERP/Gestionale", ["Solo software di fatturazione elettronica", "Gestione contabile e amministrativa base", "Software settoriale non collegato ad altre aree", "Sistema integrato (ERP) tra acquisti, magazzino e vendite", "Ecosistema interconnesso tramite API con CRM e logistica"], None),
        ("Processi Paperless", ["Gestione quasi totalmente cartacea", "Digitalizzazione limitata ai soli documenti fiscali", "Sistema misto con parziale archiviazione digitale", "Processi documentali nativi digitali", "Workflow approvativi automatici senza carta"], None),
        ("Cybersecurity", ["Nessuna protezione se non antivirus base", "Backup saltuari su dischi esterni", "Presenza di Firewall e policy password", "Audit periodici e Disaster Recovery plan", "Monitoraggio proattivo SOC 24/7 e cyber-insurance"], None),
        ("Marketing Digitale", ["Nessuna presenza online", "Sito web vetrina non aggiornato", "Presenza attiva sui social media principali", "Strategie di ADS e SEO per acquisizione traffico", "Sistema di Lead Generation integrato al CRM"], None),
        ("Innovazione AI", ["Nessuna conoscenza delle potenzialità AI", "Utilizzo sporadico di strumenti AI generativa (es. Chat)", "Sperimentazione di AI in singole aree pilota", "Processi aziendali con AI integrata internamente", "Modello di business AI-driven con automazione avanzata"], ["ICT e Digitale", "Elettronica", "Meccanica"])
    ],
    'Gestione HR': [
        ("Welfare Aziendale", ["Nessun piano di welfare", "Solo rimborsi spese e indennità base", "Convenzioni locali per i dipendenti", "Piattaforma welfare con ampia scelta di servizi", "Piano di benefit evoluto e personalizzato (flexible benefits)"], None),
        ("Valutazione Performance", ["Nessun sistema di valutazione", "Valutazione basata su sensazioni del titolare", "Colloquio di valutazione annuale qualitativo", "Sistema di MBO collegato a KPI quantitativi", "Valutazione continua con feedback a 360 gradi"], None),
        ("Retention e Talent", ["Alto turnover (i dipendenti se ne vanno)", "Turnover nella media di settore", "Politiche di bonus legati all'anzianità", "Strategia di Employer Branding strutturata", "Certificazione Top Employer e bassissimo turnover"], None),
        ("Clima Aziendale", ["Presenza di forti tensioni interne", "Il clima non viene monitorato", "Ascolto saltuario dei dipendenti", "Indagine sul clima aziendale periodica e strutturata", "Monitoraggio continuo del benessere lavorativo"], None),
        ("Formazione", ["Solo corsi obbligatori per legge (sicurezza)", "Formazione tecnica sporadica su richiesta", "Budget annuale dedicato alla formazione", "Piani di crescita professionale personalizzati", "Academy aziendale interna per lo sviluppo dei talenti"], None),
        ("Flessibilità e Smart Working", ["Presenza obbligatoria in ufficio 5/5", "Concessione dello smart working solo in emergenza", "Regolamento per flessibilità oraria e smart working", "Smart working strutturato come leva di produttività", "Lavoro agile basato su obiettivi (Work from anywhere)"], None)
    ],
    'Finanza & Investimenti': [
        ("Analisi Cash Flow", ["Nessun controllo dei flussi di cassa", "Monitoraggio basato solo sul saldo banca", "Rendiconto finanziario consuntivo mensile", "Previsionale di tesoreria a 6 mesi", "Gestione della liquidità con software di tesoreria predittiva"], None),
        ("Finanza Agevolata", ["Mai richiesti contributi o agevolazioni", "Richiesta casuale di bandi molto semplici", "Utilizzo regolare di crediti d'imposta base", "Monitoraggio sistematico di bandi regionali e nazionali", "Utilizzo strategico della finanza agevolata per investimenti"], None),
        ("Rating Bancario", ["Sconosciuto o mai monitorato", "Conoscenza vaga dei criteri di rating", "Analisi annuale della Centrale Rischi", "Monitoraggio trimestrale degli indicatori bancari", "Strategia attiva di ottimizzazione del merito creditizio"], None),
        ("Analisi Marginalità", ["Si conosce l'utile solo a fine anno", "Stime approssimative dei margini sui prodotti", "Calcolo della marginalità per singola commessa", "Contabilità analitica evoluta per centri di costo", "Modelli di marginalità predittiva e analisi dei gap"], None),
        ("Gestione del Credito", ["Reattiva (si sollecita quando manca cassa)", "Solleciti telefonici saltuari ai clienti", "Policy di recupero crediti scritta e formalizzata", "Ufficio recupero crediti dedicato e procedure rigorose", "Assicurazione del credito e cessione pro-soluto"], None),
        ("Investimenti R&S", ["Nessun investimento in innovazione", "Investimenti reattivi solo per guasti o emergenze", "Investimento del 1-2% del fatturato in R&S", "Investimento del 5% del fatturato in innovazione", "Leader di mercato con oltre il 5% investito stabilmente"], None)
    ],
    'Sostenibilità (ESG)': [
        ("Cultura ESG", ["Nessuna iniziativa di sostenibilità", "Iniziative limitate agli obblighi di legge", "Azioni di sostenibilità isolate e non coordinate", "Piano di sostenibilità integrato nel piano industriale", "Rating ESG certificato da ente terzo"], None),
        ("Impatto Ambientale", ["Nessuna attenzione all'impatto ambientale", "Raccolta differenziata e risparmio energetico base", "Monitoraggio dei consumi e delle emissioni", "Calcolo della Carbon Footprint aziendale", "Strategia Net Zero e compensazione certificata"], None),
        ("Inclusione e Diversità", ["Nessuna policy specifica", "Generica sensibilità ai temi sociali", "Presenza di donne in ruoli di leadership", "Policy formale contro le discriminazioni", "Certificazione per la parità di genere"], None),
        ("Etica e Trasparenza", ["Nessun codice etico", "Rispetto formale delle leggi vigenti", "Codice Etico adottato e comunicato", "Redazione annuale del Bilancio di Sostenibilità", "Trasformazione giuridica in Società Benefit"], None),
        ("Governance Sostenibile", ["Modello padronale puro", "Consiglio di famiglia senza membri esterni", "CdA con presenza di consiglieri esperti", "Presenza di consiglieri indipendenti", "Governance evoluta con comitati endo-consiliari"], None),
        ("Monitoraggio Fornitori", ["Scelta dei fornitori solo in base al prezzo", "Valutazione basata sulla vicinanza geografica", "Richiesta di autocertificazioni ESG ai fornitori", "Audit periodici sulla filiera di fornitura", "Qualifica fornitori solo con certificazioni ESG"], None)
    ],
    'Protezione Legale': [
        ("Modello 231", ["Modello 231 assente", "Fase di studio o analisi preliminare", "Modello adottato ma statico", "Modello aggiornato regolarmente alle norme", "Presenza di ODV attivo e flussi informativi costanti"], ["Costruzioni ed Edilizia", "Sanità", "Energia e Utilities"]),
        ("Privacy e GDPR", ["Documentazione base non aggiornata", "Informativa presente ma non conforme", "Piena conformità ai registri del trattamento", "Audit periodici sulla protezione dei dati", "Presenza di un DPO (Data Protection Officer)"], None),
        ("Contrattualistica", ["Accordi prevalentemente verbali o via mail", "Uso di moduli standard scaricati dal web", "Contratti standard redatti da legali esterni", "Contratti ad hoc per ogni tipologia di cliente/fornitore", "Sistema di Legal Contract Management digitale"], None),
        ("Marchi e Proprietà Intellettuale", ["Nessuna tutela della proprietà intellettuale", "Registrazione del solo marchio aziendale", "Monitoraggio periodico contro contraffazioni", "Strategia di valorizzazione dei beni immateriali", "Gestione attiva di brevetti e segreti industriali"], None),
        ("Gestione dei Rischi", ["Intervento legale solo in fase di emergenza", "Rapporto saltuario con avvocato di fiducia", "Tutela legale assicurativa attiva", "Sistema di prevenzione dei rischi contrattuali", "Gestione proattiva e mappatura dei rischi legali"], None),
        ("Asset Protection", ["Nessuna distinzione tra patrimonio aziendale e privato", "Polizze assicurative a tutela del patrimonio", "Costituzione di holding per segregazione asset", "Utilizzo di strumenti avanzati come Trust o Fondi", "Pianificazione successoria e tutela patrimoniale completa"], None)
    ],
    'Sicurezza sul Lavoro': [
        ("Documento Valutazione Rischi", ["Documento scaduto o non presente", "DVR standard generico", "DVR aggiornato e conforme alla realtà aziendale", "DVR dinamico aggiornato ad ogni variazione", "Modello di eccellenza oltre i requisiti minimi"], None),
        ("Formazione Sicurezza", ["Formazione incompleta o non tracciata", "Formazione effettuata solo per obbligo", "Piena regolarità dei corsi e dei rinnovi", "Formazione comportamentale per riduzione infortuni", "Diffusione di una cultura della sicurezza partecipata"], None),
        ("Sorveglianza Sanitaria", ["Nessuna visita medica effettuata", "Visite mediche minime obbligatorie effettuate", "Pianificazione rigorosa delle scadenze sanitarie", "Monitoraggio di KPI sulla salute dei lavoratori", "Programmi di prevenzione e promozione della salute"], None),
        ("Gestione DPI", ["DPI consegnati senza registro", "Registro cartaceo di consegna DPI", "Controllo sistematico dell'uso dei DPI", "Gestione digitale delle scadenze DPI", "Utilizzo di DPI intelligenti (IoT) per la sicurezza"], None),
        ("Manutenzione Impianti", ["Intervento effettuato solo dopo il guasto", "Registro delle manutenzioni obbligatorie", "Pianificazione manutentiva programmata", "Utilizzo di software CMMS per la manutenzione", "Manutenzione predittiva basata su sensori"], None),
        ("Gestione Appalti (DUVRI)", ["Nessun controllo sulle ditte esterne", "Verifica del solo DURC dei fornitori", "Redazione del DUVRI per ogni interferenza", "Coordinamento attivo e riunioni di sicurezza", "Audit periodici sulla sicurezza dei fornitori in sito"], None)
    ],
    'Standard & Qualità': [
        ("Certificazione ISO 9001", ["Nessun sistema qualità", "Certificazione in fase di ottenimento", "Certificazione vissuta come adempimento formale", "Sistema Qualità usato come strumento gestionale", "La Qualità è il motore del miglioramento continuo"], None),
        ("Mappatura Processi", ["Nessuna evidenza dei processi aziendali", "Mappatura parziale solo di alcune aree", "Procedure scritte per le attività principali", "Mappatura completa con indicatori di processo", "Approccio Lean per l'eliminazione degli sprechi"], None),
        ("Controllo Qualità", ["Controllo finale a vista sui prodotti", "Controllo a campione durante la produzione", "Controllo sistemico con procedure definite", "Monitoraggio tramite sensori e automazione", "Obiettivo 'Zero Difetti' con controllo statistico"], None),
        ("Customer Satisfaction", ["Gestione dei soli reclami in arrivo", "Sondaggio di soddisfazione saltuario", "Indagine annuale strutturata sui clienti", "Monitoraggio del Net Promoter Score (NPS)", "Co-progettazione dei prodotti con i clienti"], None),
        ("Marcatura CE", ["Prodotti non marcati o non conformi", "Documentazione tecnica minima presente", "Certificazione completa da laboratori accreditati", "Controllo rigoroso della filiera dei componenti", "Audit esterni periodici sulla conformità prodotto"], ["Meccanica", "Elettronica", "Costruzioni ed Edilizia"]),
        ("Gestione Non Conformità", ["Risoluzione immediata senza tracciamento", "Registrazione su file Excel delle anomalie", "Analisi delle cause radice (Root Cause Analysis)", "Attuazione sistematica di azioni correttive", "Analisi dei dati per prevenire future non conformità"], None)
    ],
    'Sviluppo Competenze': [
        ("Gap Analysis", ["Mai analizzate le competenze necessarie", "Si interviene solo sulle urgenze operative", "Analisi dei bisogni formativi su richiesta", "Mappatura annuale delle competenze richieste", "Gap analysis sistematica tra ruoli e competenze"], None),
        ("Fondi Interprofessionali", ["Nessun utilizzo di fondi per la formazione", "Utilizzo raro di finanziamenti esterni", "Utilizzo saltuario per corsi specifici", "Formazione sempre finanziata tramite fondi", "Ottimizzazione totale del conto formazione"], None),
        ("Metodi di Apprendimento", ["Solo formazione frontale in aula", "Affiancamento pratico senza metodo", "Utilizzo di piattaforme E-learning", "Mix di aula, pratica e formazione digitale", "Academy aziendale con percorsi di self-learning"], None),
        ("Sviluppo Leadership", ["Nessuna delega di leadership", "Solo il titolare prende decisioni chiave", "Manager formati alla gestione dei team", "Coaching individuale per le figure chiave", "Leadership diffusa a tutti i livelli aziendali"], None),
        ("Piani di Carriera", ["Nessun percorso di crescita previsto", "Progressioni basate solo sull'anzianità", "Criteri di crescita professionale definiti", "Percorsi di carriera chiari e documentati", "Meritocrazia basata su risultati misurabili"], None),
        ("Mindset e Innovazione", ["Forte resistenza a ogni cambiamento", "Timore verso le nuove tecnologie", "Presenza di pionieri dell'innovazione interni", "Cultura aziendale aperta al cambiamento", "L'innovazione è nel DNA di ogni collaboratore"], None)
    ],
    'Mercato & Vendite': [
        ("Concentrazione Fatturato", ["Oltre il 50% del fatturato generato da un solo cliente", "Primi 3 clienti pesano per oltre il 70%", "Fatturato distribuito su 10-20 clienti principali", "Portafoglio clienti frazionato e bilanciato", "Mercato di massa o database clienti estremamente vasto"], None),
        ("Presenza Internazionale", ["Solo mercato locale/provinciale", "Mercato nazionale", "Export reattivo (ordini passivi dall'estero)", "Presenza stabile in mercati esteri con rete vendita", "Multinazionale con sedi o partnership globali"], None),
        ("Processo di Vendita", ["Passaparola e attesa del cliente", "Vendita reattiva su richiesta preventivi", "Rete commerciale attiva ma senza CRM", "Processo di vendita strutturato (Funnel) e monitorato", "Sales automation e gestione predittiva dei lead"], None),
        ("Posizionamento Prezzo", ["Guerra dei prezzi (il cliente sceglie il più economico)", "Prezzi allineati alla media della concorrenza", "Prezzo basato sul costo più margine fisso", "Premium price basato sul valore riconosciuto", "Leader di mercato con potere di fissazione del prezzo"], None),
        ("Canali di Acquisizione", ["Singolo canale (es. solo agenti)", "Due canali (es. agenti + fiera)", "Mix di canali offline (fiere, rete, segnalatori)", "Strategia multicanale (Offline + Online)", "Approccio Omnichannel integrato"], None),
        ("Fedeltà del Cliente", ["Il cliente acquista una sola volta (Spot)", "Bassa fedeltà, alta sensibilità al prezzo", "Acquisti ricorrenti ma non contrattualizzati", "Contratti di fornitura pluriennali o abbonamenti", "Clienti 'Ambassador' coinvolti nello sviluppo prodotto"], None)
    ]
}

# --- 4. MOTORE DI CONSULENZA AI NEXTAHUB ---
def analizza_con_gemini(dati_cliente, punteggi):
    try:
        validi = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        scelto = next((x for x in ["models/gemini-1.5-flash", "models/gemini-1.5-pro", "models/gemini-pro"] if x in validi), validi[0])
        model = genai.GenerativeModel(scelto)
        
        prompt = f"""
        Agisci come Senior Partner e Consultant di NextaHub. Il tuo obiettivo è convertire questa analisi in un mandato di consulenza.
        
        CLIENTE: {dati_cliente['azienda']} | SETTORE: {dati_cliente['settore']} | REGIONE: {dati_cliente['regione']}
        CONSULENTE NEXTA: {dati_cliente['commerciale']}

        SCORE RILEVATI (scala 1-5): {json.dumps(punteggi, indent=2)}
        
        STRUTTURA DEL REPORT:
        1. TABELLA COMPARATIVA SCORE VS BENCHMARK (Regione: {dati_cliente['regione']}).
        2. ANALISI DEI GAP E SOLUZIONI NEXTAHUB: Dividi i gap per URGENZA. Per ogni gap spiega il rischio di inazione e il beneficio del servizio NextaHub consigliato.
        3. ROADMAP DI TRASFORMAZIONE (12-24 MESI).
        4. RESOCONTO CONCLUSIVO E SERVIZI PRIORITARI: Identifica max 3 servizi. Uno deve essere di FINANZA AGEVOLATA/FORMAZIONE FINANZIATA per spiegare come finanziare gli altri due.
        
        FIRMA: "Analisi a cura di: {dati_cliente['commerciale']} - Senior Consultant NextaHub"
        """
        return model.generate_content(prompt).text
    except Exception as e:
        return f"❌ Errore AI: {str(e)}"

# --- 5. LOGICA NAVIGAZIONE ---
with st.sidebar:
    st.image(LOGO_URL, width=180)
    st.markdown("---")
    if st.button("🏢 1. Nuova Anagrafica"): st.session_state.page = "Anagrafica"
    if st.button("📝 2. Assessment Corrente"): st.session_state.page = "Questionario"
    if st.button("📊 3. Report & AI"): st.session_state.page = "Valutazione"
    if st.button("🗄️ 4. Archivio Valutazioni"): st.session_state.page = "Archivio"

# --- PAGINA 1: ANAGRAFICA COMPLETA ---
if st.session_state.page == "Anagrafica":
    st.title("🏢 Anagrafica Cliente Completa")
    st.subheader("Dati Identificativi e Dimensionali")
    
    with st.form("form_anag_completa"):
        # Sezione 1: Dati Aziendali
        c1, c2 = st.columns(2)
        with c1:
            rs = st.text_input("Ragione Sociale *")
            pi = st.text_input("Partita IVA / Codice Fiscale *")
            settore = st.selectbox("Settore Business *", SETTORI)
            regione = st.selectbox("Regione *", REGIONI)
            comune = st.text_input("Comune Sede Legale *")
            indirizzo = st.text_input("Indirizzo e n. civico")
        with c2:
            pec = st.text_input("PEC Aziendale")
            sito = st.text_input("Sito Web")
            dipendenti = st.number_input("Numero Dipendenti (Media annua)", min_value=0, step=1)
            fatturato = st.selectbox("Fatturato Annuo", ["< 2M€", "2M€ - 10M€", "10M€ - 50M€", "> 50M€"])
            ateco = st.text_input("Codice ATECO (se noto)")

        st.divider()
        
        # Sezione 2: Contatti e Referenti
        c3, c4 = st.columns(2)
        with c3:
            st.markdown("**Legale Rappresentante**")
            legale_nom = st.text_input("Nome e Cognome LR")
            legale_mail = st.text_input("Email LR")
        with c4:
            st.markdown("**Referente Interno (Contatto Operativo)**")
            rif_az = st.text_input("Nome e Cognome Referente")
            rif_tel = st.text_input("Telefono/Cellulare Referente")

        st.divider()
        
        # Sezione 3: Dati NextaHub
        st.markdown("**Area Commerciale NextaHub**")
        comm = st.text_input("Senior Consultant / Riferimento Commerciale Nexta *")
        note_comm = st.text_area("Note preliminari sul cliente")

        if st.form_submit_button("➡️ Salva e Inizia Assessment"):
            if rs and pi and settore and comm:
                st.session_state.current_piva = pi
                # Salvataggio nel database con tutti i nuovi campi
                st.session_state.db_clienti[pi] = {
                    "info": {
                        "azienda": rs, 
                        "piva": pi, 
                        "settore": settore, 
                        "regione": regione, 
                        "comune": comune,
                        "indirizzo": indirizzo,
                        "pec": pec,
                        "ateco": ateco,
                        "dipendenti": dipendenti,
                        "fatturato": fatturato,
                        "commerciale": comm, 
                        "contatto_nome": rif_az,
                        "contatto_tel": rif_tel,
                        "legale_rappresentante": legale_nom,
                        "note": note_comm
                    },
                    "storia": []
                }
                st.session_state.page = "Questionario"
                st.rerun()
            else:
                st.error("Per favore, compila tutti i campi contrassegnati con l'asterisco (*)")

# PAGINA 2: QUESTIONARIO (54 DOMANDE)
elif st.session_state.page == "Questionario":
    pi = st.session_state.get('current_piva')
    if not pi: st.warning("Seleziona o crea un cliente"); st.stop()
    cl = st.session_state.db_clienti[pi]
    st.title(f"📝 Assessment: {cl['info']['azienda']}")
    
    tabs = st.tabs(list(DOMANDE_MATRICE.keys()))
    temp_scores = {}
    
    for i, area in enumerate(DOMANDE_MATRICE.keys()):
        with tabs[i]:
            scores = []
            for j, (dom, opt, lim) in enumerate(DOMANDE_MATRICE[area]):
                if lim is None or cl['info']['settore'] in lim:
                    s = st.radio(f"**{dom}**", [1,2,3,4,5], format_func=lambda x: f"{x}: {opt[x-1]}", key=f"{pi}_{area}_{j}_{len(cl['storia'])}")
                    scores.append(s)
            temp_scores[area] = sum(scores)/len(scores) if scores else 3.0
            
    if st.button("📊 Genera Report"):
        cl['storia'].append({
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "punteggi": temp_scores,
            "report": ""
        })
        st.session_state.page = "Valutazione"
        st.rerun()

# PAGINA 3: VALUTAZIONE (LOGO CENTRATO + GRAFICI COLORATI)
elif st.session_state.page == "Valutazione":
    pi = st.session_state.get('current_piva')
    if not pi or not st.session_state.db_clienti[pi]['storia']: st.warning("Dati mancanti"); st.stop()
    
    cl = st.session_state.db_clienti[pi]
    ass = cl['storia'][-1]
    
    # 1. Logo Centrato
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2: st.image(LOGO_URL, use_container_width=True)
    
    st.markdown(f"<h1 style='text-align: center;'>Analisi Strategica: {cl['info']['azienda']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'><b>Data:</b> {ass['data']} | <b>Analista:</b> {cl['info']['commerciale']}</p>", unsafe_allow_html=True)

    # 2. Grafici (Radar e Barre Colorate)
    bench_val = {"Strategia & Controllo": 3.5, "Digitalizzazione": 3.2, "Gestione HR": 3.4, "Finanza & Investimenti": 3.0, "Sostenibilità (ESG)": 3.1, "Protezione Legale": 3.8, "Sicurezza sul Lavoro": 4.2, "Standard & Qualità": 3.9, "Sviluppo Competenze": 3.3, "Mercato & Vendite": 3.0}
    
    c1, c2 = st.columns(2)
    categories = list(ass['punteggi'].keys())
    values = list(ass['punteggi'].values())
    
    with c1:
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', name='Azienda', line_color='#E63946'))
        fig_radar.add_trace(go.Scatterpolar(r=[bench_val[k] for k in categories], theta=categories, name='Benchmark', line_color='#1D3557'))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=True)
        st.plotly_chart(fig_radar, use_container_width=True)

    with c2:
        diffs = [ass['punteggi'][cat] - bench_val[cat] for cat in categories]
        colors = []
        for d in diffs:
            if d >= 0: colors.append('#2D6A4F') # Verde
            elif d > -0.5: colors.append('#FFD60A') # Giallo
            elif d > -1.5: colors.append('#FB8500') # Arancio
            else: colors.append('#AE2012') # Rosso
        
        fig_bar = go.Figure(go.Bar(x=diffs, y=categories, orientation='h', marker_color=colors))
        fig_bar.update_layout(xaxis_title="Gap vs Benchmark", yaxis_autorange="reversed")
        st.plotly_chart(fig_bar, use_container_width=True)

    if st.button("🚀 Genera Analisi Strategica AI"):
        with st.spinner("L'AI NextaHub sta elaborando..."):
            ass['report'] = analizza_con_gemini(cl['info'], ass['punteggi'])
            st.rerun()
            
    if ass['report']:
        st.markdown("---")
        st.markdown(ass['report'])
        st.markdown(f"\n\n**Analisi a cura di:** {cl['info']['commerciale']} - Senior Consultant NextaHub")

# PAGINA 4: ARCHIVIO (Ripesca, Ricarica e Confronta)
elif st.session_state.page == "Archivio":
    st.title("🗄️ Archivio & Gestione CRM NextaHub")
    
    if not st.session_state.db_clienti:
        st.info("Nessun cliente in archivio. Inizia creando una nuova anagrafica.")
    else:
        for piva, dati in st.session_state.db_clienti.items():
            # Il titolo dell'expander mostra il nome azienda e la P.IVA
            with st.expander(f"🏢 {dati['info']['azienda']} - P.IVA: {piva}"):
                
                # Layout a colonne per le azioni rapide
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                
                # 1. Tasto per visualizzare i dati anagrafici (il tuo "CRM portatile")
                if col_btn1.button(f"📋 Dati Anagrafici", key=f"anag_{piva}"):
                    st.success(f"Scheda Anagrafica di {dati['info']['azienda']}")
                    # Visualizzazione pulita dei dati
                    info = dati['info']
                    st.write(f"**Legale Rappresentante:** {info.get('legale', 'N/D')}")
                    st.write(f"**PEC:** {info.get('pec', 'N/D')}")
                    st.write(f"**Settore:** {info.get('settore', 'N/D')} (ATECO: {info.get('ateco', 'N/D')})")
                    st.write(f"**Dimensioni:** {info.get('fatturato', 'N/D')} | {info.get('dipendenti', 0)} dipendenti")
                    st.write(f"**Contatto:** {info.get('tel', 'N/D')} | {info.get('mail', 'N/D')}")
                    st.write(f"**Analista Nexta:** {info.get('commerciale', 'N/D')}")
                
                # 2. Tasto per rilanciare un nuovo assessment per lo stesso cliente
                if col_btn2.button(f"➕ Nuova Analisi", key=f"new_an_{piva}"):
                    st.session_state.current_piva = piva
                    st.session_state.page = "Questionario"
                    st.rerun()
                
                # 3. Tasto per eliminare l'intero record (con cautela)
                if col_btn3.button(f"🗑️ Elimina Record", key=f"del_{piva}"):
                    del st.session_state.db_clienti[piva]
                    st.rerun()

                st.markdown("---")
                st.subheader("Storico Assessment Strategici")
                
                # Elenca tutte le sessioni fatte per questo cliente
                if not dati['storia']:
                    st.write("Nessuna analisi ancora completata.")
                else:
                    for idx, sessione in enumerate(dati['storia']):
                        c1, c2 = st.columns([4, 1])
                        c1.write(f"📅 **Sessione del {sessione['data']}**")
                        if c2.button(f"Apri Report", key=f"view_{piva}_{idx}"):
                            # Carichiamo la sessione scelta come "ultima" per visualizzarla in Pagina 3
                            selected = dati['storia'].pop(idx)
                            dati['storia'].append(selected)
                            st.session_state.current_piva = piva
                            st.session_state.page = "Valutazione"
                            st.rerun()
