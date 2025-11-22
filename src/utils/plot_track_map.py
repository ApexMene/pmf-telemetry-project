import plotly.express as px

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