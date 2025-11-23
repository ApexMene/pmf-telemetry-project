import plotly.graph_objects as go
import numpy as np  # noqa: F401


def plot_3d_track(df):
    X, Y, Z = df["X"].to_numpy(), df["Y"].to_numpy(), df["Z"].to_numpy()

    fig = go.Figure()

    # pista
    fig.add_trace(
        go.Scatter3d(
            x=X,
            y=Y,
            z=Z,
            mode="lines",
            line=dict(color=Z, colorscale="Plasma", width=6),
            hoverinfo="none",
        )
    )

    # # ombra
    # fig.add_trace(
    #     go.Scatter3d(
    #         x=X,
    #         y=Y,
    #         z=np.full_like(Z, Z.min() - 50),
    #         mode="lines",
    #         line=dict(
    #             color=Z,
    #             colorscale="Plasma",
    #             width=6,
    #             showscale=True,
    #             # colorbar=dict(
    #             #     title=dict(text="Elevation (m)", font=dict(color="white")),
    #             #     thickness=15,
    #             #     len=0.5,
    #             #     x=0.9,
    #             #     tickfont=dict(color="white"),
    #             # ),
    #         ),
    #         hoverinfo="skip",
    #     )
    # )

    # coordinate calibrate mugello -> Ci ho provato ma è troppo lungo e dispendioso come lavoro al momento.
    # Meglio pensare a feature effettive e non a questoi particolari al momento
    # corners = {
    #     "San Donato": {"x": 2150, "y": 5450},
    #     "Luco": {"x": 550, "y": 4050},
    #     "Arrabbiata 1": {"x": -2750, "y": -850},
    #     "Arrabbiata 2": {"x": -3350, "y": 550},
    #     "Correntaio": {"x": -5650, "y": -2250},
    #     "Bucine": {"x": -4750, "y": -6650},
    # }

    # for name, c in corners.items():
    #     idx = np.argmin((X - c["x"]) ** 2 + (Y - c["y"]) ** 2)
    #     rx, ry, rz = X[idx], Y[idx], Z[idx]
    #     # pin
    #     fig.add_trace(
    #         go.Scatter3d(
    #             x=[rx, rx],
    #             y=[ry, ry],
    #             z=[rz, rz + 200],
    #             mode="lines+text",
    #             text=["", f"<b>{name}</b>"],
    #             textfont=dict(color="white", size=10),
    #             line=dict(color="rgba(255,255,255,0.3)", width=1),
    #             showlegend=False,
    #         )
    #     )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0e1117",
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data",
            camera=dict(eye=dict(x=1.5, y=0.8, z=1)),
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        showlegend=False,
    )

    return fig
