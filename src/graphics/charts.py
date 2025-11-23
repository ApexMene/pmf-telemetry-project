import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import polars as pl
import numpy as np
from src.config.settings import config_pmf_object as config_pmf

REV_LIMIT_RPM = config_pmf.REV_LIMIT_RPM


def plot_correlation_matrix(df):
    """Genera la Heatmap di correlazione tra i sensori per Data Integrity check."""

    corr = df.select(["Speed", "RPM", "nGear", "Throttle", "Brake"]).corr()
    
    fig = px.imshow(
        corr.to_numpy(), 
        x=corr.columns, 
        y=corr.columns, 
        text_auto=".2f", 
        color_continuous_scale="RdBu_r", 
        aspect="auto", 
        template="plotly_dark",
        title="Sensor Correlation Matrix"
    )
    return fig

def plot_rpm_distribution(df):
    """Istogramma utilizzo motore con linea limitatore."""
    
    fig = px.histogram(
        df, 
        x="RPM", 
        nbins=100, 
        template="plotly_dark", 
        color_discrete_sequence=['#FFD700'],
        title="Engine RPM Distribution"
    )
    
    # Linea Limite Regolamento
    fig.add_vline(
        x=REV_LIMIT_RPM, 
        line_dash="dash", 
        line_color="red", 
        annotation_text=f"Rev Limit ({REV_LIMIT_RPM})"
    )
    return fig

def plot_gear_ratios(df):
    """Box plot per analizzare la spaziatura delle marce."""
    
    fig = px.box(
        df, 
        x="nGear", 
        y="Speed", 
        color="nGear", 
        template="plotly_dark",
        points="outliers",
        title="Gear Ratio Analysis"
    )
    fig.update_layout(showlegend=False, xaxis_title="Gear", yaxis_title="Speed (km/h)")
    return fig

def plot_engine_heatmap(df):
    """Heatmap RPM vs Throttle per calibrazione motore."""
    
    fig = px.density_heatmap(
        df, 
        x="RPM", 
        y="Throttle", 
        z="Speed", 
        histfunc="count", 
        nbinsx=30, nbinsy=20, 
        color_continuous_scale="Hot", 
        template="plotly_dark",
        title="Engine Calibration Map (RPM vs Throttle)"
    )
    return fig

def plot_telemetry_zoom(df):
    """Grafico di dettaglio (3 righe) per la staccata della San Donato."""
    # Filtro i primi 15 secondi (San Donato)
    df_zoom = df.filter(pl.col("Time_Sec") < 15).to_pandas()
    
    fig = make_subplots(
        rows=3, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.05,
        subplot_titles=("Velocità", "Freno (Input)", "Marcia"), 
        row_heights=[0.4, 0.2, 0.4]
    )
    
    # 1. Velocità
    fig.add_trace(go.Scatter(
        x=df_zoom["Time_Sec"], y=df_zoom["Speed"], 
        mode='lines+markers', marker=dict(color=df_zoom["Speed"], colorscale="Turbo"), 
        name="Speed"
    ), row=1, col=1)
    
    # 2. Freno
    fig.add_trace(go.Scatter(
        x=df_zoom["Time_Sec"], y=df_zoom["Brake"].astype(int), 
        mode='lines', fill='tozeroy', line=dict(color='#d50000'), 
        name="Brake"
    ), row=2, col=1)
                                 
    # 3. Marce
    fig.add_trace(go.Scatter(
        x=df_zoom["Time_Sec"], y=df_zoom["nGear"], 
        mode='lines+markers', line=dict(shape='hv', color='#ffea00'), 
        name="Gear"
    ), row=3, col=1)
    
    fig.update_layout(
        height=800, 
        template="plotly_dark", 
        hovermode="x unified",
        title="Deep Dive: San Donato Braking Zone"
    )
    
    return fig

def g_force_chart(df):
    # non avendo gli accelerometri, uso la cinematica:
    # Longitudinale = derivata della velocità
    # Laterale = Velocità * Velocità di rotazione (cambio di direzione)

    df_physics = df.with_columns([
        (pl.col("Speed") / 3.6).alias("v_ms"), # km/h -> m/s
        pl.col("Time_Sec").diff().fill_null(0.2).alias("dt"), # Delta Tempo
        pl.col("X").diff().fill_null(0).alias("dx"),
        pl.col("Y").diff().fill_null(0).alias("dy")
    ])

    # calcolo Long G (Accelerazione/Frenata)
    # a = delta_v / delta_t / 9.81
    df_physics = df_physics.with_columns(
        (pl.col("v_ms").diff().fill_null(0) / pl.col("dt") / 9.81).alias("Long_G_Raw")
    )

    dx = df_physics["dx"].to_numpy()
    dy = df_physics["dy"].to_numpy()
    heading = np.arctan2(dy, dx) 

    heading_smooth = np.unwrap(heading)

    df_physics = df_physics.with_columns(pl.Series("heading", heading_smooth))

    df_physics = df_physics.with_columns(
        ((pl.col("v_ms") * pl.col("heading").diff().fill_null(0) / pl.col("dt")) / 9.81).alias("Lat_G_Raw")
    )

    df_physics = df_physics.with_columns([
        pl.col("Long_G_Raw").rolling_mean(window_size=8).fill_null(0).alias("Long_G"),
        pl.col("Lat_G_Raw").rolling_mean(window_size=8).fill_null(0).alias("Lat_G")
    ])

    plot_data = df_physics.to_pandas()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=plot_data["Lat_G"],
        y=plot_data["Long_G"],
        mode='markers',
        marker=dict(
            size=4,
            color=plot_data["Speed"], 
            colorscale='Turbo',
            showscale=True,
            colorbar=dict(title="Speed (km/h)")
        ),
        text=plot_data["Time_Sec"], 
        hoverinfo='text+x+y',
        name='G-Force'
    ))

    for r in [1.0, 2.0, 3.0, 4.0, 5.0]:
        fig.add_shape(type="circle",
            xref="x", yref="y",
            x0=-r, y0=-r, x1=r, y1=r,
            line_color="white", line_dash="dot", opacity=0.2
        )

    fig.update_layout(
        title="G-G diagram",
        xaxis_title="Lateral G (Cornering)",
        yaxis_title="Longitudinal G (Braking/Accel)",
        template="plotly_dark",
        width=700, height=700,
        yaxis=dict(
            scaleanchor="x", 
            scaleratio=1,
            range=[-5.5, 5.5] # range F1 -> ovviamente le moto lo hanno inferiore (si odvrebbe attestare max 1.2, 1.5)
        ),
        xaxis=dict(range=[-5.5, 5.5]),
        annotations=[
            dict(x=0, y=5, text="ACCELERAZIONE", showarrow=False, font=dict(color="gray")),
            dict(x=0, y=-5, text="FRENATA (San Donato)", showarrow=False, font=dict(color="red")),
            dict(x=-5, y=0, text="CURVA SX", showarrow=False, font=dict(color="gray")),
            dict(x=5, y=0, text="CURVA DX", showarrow=False, font=dict(color="gray"))
        ]
    )

    return fig

def plot_track_map(df, color_by="Speed", title="Track map"):
    fig = px.scatter(
        df,
        x="X",
        y="Y",
        color=color_by, # colora in base alla velocita
        title=title,
        color_continuous_scale="Turbo",  # rosso: veloce, blu:lento)
        width=800,
        height=800,
        hover_data=["RPM", "nGear", "Time_Sec"] # sono dati extraa qundo si passa col mouse sopra
    )
    
    fig.update_traces(marker=dict(size=3))

    fig.update_xaxes(visible=False) # toglie assi dal plot
    fig.update_yaxes(visible=False)

    fig.update_layout(
        template="plotly_dark",           
        plot_bgcolor="rgba(0,0,0,0)",     
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(
            scaleanchor="x", 
            scaleratio=1  # scaleratio=1 così forza 1 metro su X a essere uguale a 1 metro su Y.
        )
    )

    return fig