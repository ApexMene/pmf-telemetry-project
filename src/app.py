import streamlit as st
import time
import base64
from PIL import Image

from src.engine import loader, network
from src.graphics import maps, charts
from src.utils.images64 import get_base64_image

# CONFIGURAZIONE PAGINA
st.set_page_config(
    page_title="PMF Telemetry Suite",
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="expanded",
)

# css per pulizia e stile
st.markdown(
    """
<style>
    .block-container {padding-top: 1rem; padding-bottom: 3rem;}
    div.stButton > button { width: 100%; font-weight: bold; border: 1px solid #ff4b4b; border-radius: 6px; }
    /* Centra il titolo in sidebar */
    h1 { text-align: center; }
</style>
""",
    unsafe_allow_html=True,
)


# loghi e contatti
try:
    # logo PMF in cima
    col_L, col_C, col_R = st.sidebar.columns([1, 4, 1])
    with col_C:
        st.image("images/image.png", width=150)
except:  # noqa: E722
    st.sidebar.warning("logo PMF non trovato")

# SIDEBAR
st.sidebar.markdown(
    "<h1 style='font-size: 27px;'>POLIMI Motorcycle Factory Project</h1>",
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    "<p style='text-align: center; color: gray; font-size: 18px;'>Gianluca Meneghetti</p>",
    unsafe_allow_html=True,
)
# mail
st.sidebar.markdown(
    """
    <div style='text-align: center; margin-top: 5px; margin-bottom: 15px;'>
        <a href='mailto:gianluca.meneghetti@mail.polimi.it' style='color: #3399ff; font-size: 14px; text-decoration: none;'>
            gianluca.meneghetti@mail.polimi.it
        </a><br>
        <a href='mailto:gianluca.meneghetti@outlook.com' style='color: #3399ff; font-size: 14px; text-decoration: none;'>
            gianluca.meneghetti@outlook.com
        </a><br>
        <a href='https://www.linkedin.com/in/gianluca-meneghetti-3b520325b/' style='color: #3399ff; font-size: 14px; text-decoration: none;'>
            LinkedIn
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")

nav = st.sidebar.radio(
    "Menù:",
    [
        "0. Perchè di questo progetto",
        "1. Data offload",
        "2. Race analysis",
    ],
)

# logo Polimi in basso (Fixed)
img_b64 = get_base64_image("images/logoPolimi.webp")
if img_b64:
    st.sidebar.markdown(
        f"""
        <style>
            .sidebar-footer {{
                position: fixed; bottom: 20px; width: 18rem; text-align: center;
                padding: 10px; z-index: 99; pointer-events: none;
            }}
            .sidebar-footer img {{ width: 150px; opacity: 1; }}
        </style>
        <div class="sidebar-footer">
            <img src="data:image/webp;base64,{img_b64}">
        </div>
        """,
        unsafe_allow_html=True,
    )

# CARICAMENTO DATI
if "source_data" not in st.session_state:
    try:
        st.session_state["source_data"] = loader.load_dataset()
    except Exception as e:
        st.sidebar.error(f"Errore Dati: {e}")


# 0. PROJECT CONTEXT
if nav == "0. Perchè di questo progetto":
    st.title("PMF telemetry project - concept")

    c_text, c_vid = st.columns([0.65, 0.35], gap="medium")
    
    with c_text:
        st.markdown("### About me")
        st.markdown("""
        Mi chiamo **Gianluca Meneghetti**, classe 2003.
        
        Sono un **ML Engineer** operativo in Italtel da quasi due anni. 
        Nasco da un percorso tecnico-pratico (ITS Academy Angelo Rizzoli) e quest'anno ho deciso di alzare l'asticella, iniziando il percorso in **Ingegneria Informatica** (IOL) qui al Politecnico.
        
        I motori non sono solo un hobby, sono la mia benzina. 
        Inoltre quest'anno ho deciso di coronare la passione con una **Triumph 765 RS** che potete vedere qui a destra: è lei che mi dà le vere soddisfazioni, mettendo in discussione le leggi della fisica.
        """)
        
        
    with c_vid:
        try:
            st.video("images/profile.mp4", autoplay=True, loop=True, muted=True)
        except:
            st.info("video profilo non trovato (inserire images/profile.mp4)")

    st.markdown("---")
    
    st.markdown("""
        ### il progetto "redemption"
        nel test scritto ho avuto incertezze su argomenti chiave come **tcp vs udp** e **nas**.
        
        tuttavia, guardando i grafici di telemetria e la mole di dati che una moto da corsa genera, ho realizzato che la **data analysis** (la parte "visibile") non può esistere senza una solida **infrastruttura** di trasporto (la parte "nascosta").
        
        non mi piace lasciare le cose a metà. ho passato gli ultimi 3 giorni a studiare e a costruire questa suite per dimostrare di aver colmato le lacune, unendo l'ingegneria del dato alla passione per la pista.
        """)
    
    st.markdown("---")

    #  1. IL DATASET
    st.subheader("1. Il dato: perché f1 al mugello?")
    st.markdown("""
    mi servivano dati telemetrici veri (non random) per testare l'infrastruttura. i dati motogp non sono pubblici.
    ho scelto il **mugello 2020 (f1)** perché:
    1.  è una pista da moto (ho i riferimenti fisici corretti tipo staccata san donato).
    2.  i dati sono granulari e puliti.
    
    ho usato le api di **fastf1** per scaricare il giro veloce di leclerc.
    """)

    with st.expander("vedi codice estrazione dati"):
        st.code(
            """
import fastf1
import polars as pl
from pathlib import Path


# crea una cartella 'cache' per velocizzare le esecuzioni future)
fastf1.Cache.enable_cache("cache")

# Q are the qualyfin
session = fastf1.get_session(2020, "Tuscan", "Q")
session.load()


driver = "LEC"
lap = session.laps.pick_driver(driver).pick_fastest()
telemetry = lap.get_telemetry()

# inutile importaare colonna "DRS"
df = pl.DataFrame(
    telemetry[["Time", "Speed", "RPM", "nGear", "Throttle", "Brake", "X", "Y", "Z"]]
)

# scale dei dati con rpm maggiori per "simulare" di più le moto
df = df.with_columns(
    [
        (pl.col("Time").dt.total_milliseconds() / 1000).alias("Time_Sec"),
        (pl.col("RPM") * 1.1).alias("RPM"),
    ]
)

parquet_name = "telemetry_mugello_f1_2020.parquet"

output_dir = Path.cwd() / "data"
output_dir.mkdir(parents=True, exist_ok=True)

df.write_parquet(output_dir / "mugello_telemetry_2020_f1_LEC.parquet")

        """,
            language="python",
        )

    #  2. DATA CLEANING
    st.subheader("2. Adattamento al dominio (f1 -> moto)")
    st.markdown("""
    **problema:** guardando i dati nel notebook, ho visto che la f1 usa 8 marce e ha velocità in curva impossibili per una moto (troppo carico aerodinamico).
    
    **soluzione:** ho applicato un offset logico. ho ipotizzato che dove una f1 è in 8a, una moto è in 6a (top speed). ho traslato tutto il cambio di -2 marce e clippato i giri motore a 14.000 (limite regolamento motostudent).
    """)

    with st.expander("vedi preprocessing"):
        st.code(
            """
# src/engine/loader.py
# uso polars per performance (multithread)
df = df.with_columns([
    # taglio rpm per regolamento C.8.1.2 (14k)
    pl.col("RPM").clip(0, 14000),
    
    # shift marce: f1(8) -> moto(6)
    (pl.col("nGear") - 2).clip(1, 6).alias("nGear")
])
        """,
            language="python",
        )

    # 3. FISICA INVERSA
    st.subheader("3. fisica inversa: il 'friction circle'")
    st.markdown("""
    il dataset non aveva accelerometri (sensori G). un ingegnere di pista non può lavorare senza vedere le forze G per capire il limite della gomma.
    
    **la mia idea:** derivare le accelerazioni dalla cinematica del gps.
    *   long g = derivata della velocità nel tempo
    *   lat g = velocità * velocità angolare (cambio direzione)
    
    questo mi ha permesso di generare il **g-g diagram** che c'è nella sezione race analysis.
    """)

    #  4. INFRASTRUTTURA
    st.subheader("4. la risposta al test: reti e docker")
    st.markdown("""
    per rispondere alle domande del test che ho sbagliato:
    
    1.  **nas -> docker volumes:** non so configurare un nas fisico da zero, ma so creare un ambiente containerizzato dove i dati persistono (`./data:/app/data`) e sono accessibili a tutto il team indipendentemente dal pc che usano.
    2.  **tcp vs udp -> simulatore:** ho scritto un modulo che dimostra *praticamente* perché in telemetria differita (box) si usa il tcp.
    """)

    with st.expander("vedi simulatore rete `(src/engine/network.py)`"):
        st.code(
            """
def simulate_transfer(df, protocol, progress_bar, status_txt):
    total_chunks = 100
    chunk_size = df.height // total_chunks
    received = []
    
    # configurazine protocollo
    # meglio "in" che verificare uguale per robustezza
    if "TCP" in protocol:
        delay, loss_prob = 0.02, 0.0
    else: # UDP
        delay, loss_prob = 0.003, 0.2
        
    for i in range(total_chunks):
        time.sleep(delay)
        progress_bar.progress(i+1)
        status_txt.text(f"Trasmesso pacchetto {i+1}/{total_chunks} via {protocol}...")
        
        if random.random() > loss_prob:
            start = i * chunk_size
            
            # se ultimo giro, prendo fino alla fine
            if i == total_chunks - 1:
                chunk = df.slice(start, df.height - start) # prende il resto
            else:
                chunk = df.slice(start, chunk_size)
                
            received.append(chunk)
            
    if not received:
        return None, 0
    
    final_df = pl.concat(received)
    integrity = (final_df.height / df.height) * 100
    return final_df, integrity
        """,
            language="python",
        )

    st.markdown("---")
    st.info(
        "vai su **'1. data offload'** nel menu a sinistra per provare il simulatore."
    )


# 1. DATA OFFLOAD -> sumualzione di rete
elif nav == "1. Data offload":
    st.title("download dati telemetria")
    st.markdown("**track:** mugello (dati f1 adattati motoGP) | **driver:** leclerc")

    st.warning(
        "⚠️ **regolamento b.10.3.3**: telemetria live vietata. scarico consentito solo via cavo ai box."
    )

    col1, col2 = st.columns([1, 3])

    with col1:
        st.subheader("connessione")
        protocol = st.radio(
            "protocollo:",
            ["TCP (Cavo Box)", "UDP (Live Stream)"],
            label_visibility="collapsed",
        )

        if st.button("avvia scarico dati"):
            # 1. check
            if "source_data" not in st.session_state:
                st.error("⛔ errore critico: impossibile caricare il dataset.")
                st.stop()

            # 2. reset vista precedente
            if "df_view" in st.session_state:
                del st.session_state["df_view"]

            bar = st.progress(0)
            status = st.empty()

            # 3. chiamata al simulatore di rete
            df_res, integrity = network.simulate_transfer(
                st.session_state["source_data"],
                protocol,
                bar,
                status,
            )

            # 4. result
            if integrity < 100:
                st.error(f"❌ file corrotto ({integrity:.1f}%)")
                st.markdown(
                    "packet loss rilevato. udp non adatto per log ingegneristici."
                )
            else:
                st.success("✅ download ok (100%)")
                st.session_state["df_view"] = df_res
                time.sleep(0.5)
                st.rerun()

    with col2:
        if "df_view" in st.session_state:
            st.subheader("visualizzazione del tracciato")
            st.plotly_chart(
                maps.plot_3d_track(st.session_state["df_view"]),
                use_container_width=True,
            )
        else:
            st.info("in attesa di connessione con la ecu...")


# 2. RACE ANALYSIS -> grafici
elif nav == "2. Race analysis":
    if "df_view" not in st.session_state:
        st.markdown("***")
        st.error("⛔ nessun dato")
        st.markdown(
            "devi prima scaricare il log via tcp nella sezione **data offload**."
        )
        st.stop()

    df = st.session_state["df_view"]

    st.title("debriefing tecnico")

    # tabs tematiche
    tab0, tab1, tab2, tab3, tab4 = st.tabs(
        ["0. velocità e marce", "1. integrità", "2. motore", "3. dinamica", "4. zoom"]
    )

    with tab0:
        st.markdown("#### velocità e marce nel circuito")
        st.caption("grafico andamento velocità fastlap")
        st.plotly_chart(charts.plot_track_map(df), use_container_width=True)
        
    with tab1:
        st.markdown("#### coerenza sensori")
        st.caption("verifica correlazioni.")
        st.plotly_chart(charts.plot_correlation_matrix(df), use_container_width=True)

    with tab2:
        st.markdown("#### stress test motore")
        c1, c2 = st.columns(2)
        c1.plotly_chart(charts.plot_rpm_distribution(df), use_container_width=True)
        c2.plotly_chart(charts.plot_gear_ratios(df), use_container_width=True)

    with tab3:
        st.markdown("#### performance & fisica")
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(charts.plot_engine_heatmap(df), use_container_width=True)
        with c2:
            st.plotly_chart(charts.g_force_chart(df), use_container_width=True)
            st.info(
                "ℹ️ **friction circle:** accelerazioni derivate matematicamente dal gps."
            )

    with tab4:
        st.markdown("#### deep dive: staccata san donato")
        st.markdown("analisi ritardo input pilota vs risposta meccanica.")
        st.plotly_chart(charts.plot_telemetry_zoom(df), use_container_width=True)
