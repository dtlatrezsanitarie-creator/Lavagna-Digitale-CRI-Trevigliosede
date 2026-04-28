import streamlit as st
import pandas as pd
import os
import requests

# --- CONFIGURAZIONE ---
cartella_script = os.path.dirname(os.path.abspath(__file__))
# Usiamo lo stesso nome file della sede di Castel Rozzone
DB_PATH = os.path.join(cartella_script, 'Lista articoli.XLSX')
# URL AGGIORNATO PER TREVIGLIO (Quello che mi hai inviato prima)
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSd_5OZf6eRhPukufmAwqEYiKpOMUIAMgpX-nG2UJNDP9HLVNQ/formResponse"

st.set_page_config(page_title="CRI Treviglio - Scarico", layout="wide")
st.title("🚑 Lavagna Digitale - CRI Treviglio")

@st.cache_data
def carica_dati():
    if os.path.exists(DB_PATH):
        try:
            # Saltiamo la prima riga perché il tuo Excel ha l'intestazione con la data
            df = pd.read_excel(DB_PATH, skiprows=1)
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except: return None
    return None

df_prodotti = carica_dati()

if df_prodotti is not None:
    cerca = st.text_input("COSA HAI PRESO?", "").strip().lower()
    
    if cerca:
        # Filtro sulla colonna Descrizione
        risultati = df_prodotti[df_prodotti['Descrizione'].astype(str).str.contains(cerca, case=False, na=False)]
        
        if not risultati.empty:
            for _, row in risultati.head(10).iterrows():
                nome_articolo = str(row['Descrizione'])
                codice_mambu = str(row['Barcode'])
                
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f"### {nome_articolo}")
                        st.caption(f"Codice: {codice_mambu}")
                    with col2:
                        qta = st.number_input("Pezzi", min_value=1, value=1, key=f"q_{codice_mambu}")
                    with col3:
                        st.write(" ")
                        if st.button("SCARICA ✅", key=f"btn_{codice_mambu}", use_container_width=True):
                            
                            # ID CAMPI (Verificati per il modulo di Treviglio)
                            payload = {
                                "entry.1921919747": nome_articolo,   # ARTICOLO
                                "entry.1949015185": codice_mambu,    # CODICE
                                "entry.1928057596": str(qta)         # QUANTITA
                            }
                            
                            try:
                                # Invio al Google Form di Treviglio
                                r = requests.post(FORM_URL, data=payload)
                                if r.status_code == 200:
                                    st.balloons()
                                    st.success(f"REGISTRATO: {qta} {nome_articolo}")
                                else:
                                    st.error("Errore di ricezione da parte di Google.")
                            except:
                                st.error("Errore di connessione.")
        else:
            st.warning("Nessun articolo trovato.")
else:
    st.error("File Excel non trovato! Assicurati che il file caricato si chiami 'Lista articoli.XLSX'")
