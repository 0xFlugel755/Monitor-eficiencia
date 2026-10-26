"""Estilo "Dark Industrial Tech" do dashboard (baseado no guia de estilização)."""

import plotly.graph_objects as go
import streamlit as st
from streamlit_option_menu import option_menu

from src import config


def injetar_css() -> None:
    """CSS global: fundo escuro, fonte Inter, sem rodapé/menu padrão do Streamlit."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

        html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
        .stApp {{ background-color: {config.COR_FUNDO}; color: {config.COR_TEXTO}; }}

        /* Esconde menu e rodapé padrão, mas mantém o botão da barra lateral */
        #MainMenu, footer {{ visibility: hidden; }}
        header[data-testid="stHeader"] {{ background: transparent; }}

        .block-container {{ padding: 1.5rem 2rem 2rem 2rem; max-width: 100%; }}

        section[data-testid="stSidebar"] {{
            background-color: {config.COR_CARTAO};
            border-right: 1px solid {config.COR_BORDA};
        }}

        h4.titulo-secao {{
            font-size: 13px; color: {config.COR_TEXTO_SUAVE};
            margin: 8px 0; text-transform: uppercase; letter-spacing: 0.05em;
        }}

        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: {config.COR_FUNDO}; }}
        ::-webkit-scrollbar-thumb {{ background: {config.COR_BORDA}; border-radius: 3px; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def titulo_secao(texto: str) -> None:
    st.markdown(f"<h4 class='titulo-secao'>{texto}</h4>", unsafe_allow_html=True)


def cartao_kpi(titulo: str, valor: str, meta: str, cor: str = config.COR_DESTAQUE) -> None:
    """Cartão de KPI com borda lateral colorida conforme o status."""
    st.markdown(
        f"""
        <div style="background-color:{config.COR_CARTAO}; border:1px solid {config.COR_BORDA};
                    border-left:4px solid {cor}; border-radius:6px; padding:16px; margin-bottom:12px;
                    box-shadow:0 4px 6px -1px rgba(0,0,0,0.3);">
            <div style="font-size:11px; font-weight:600; color:{config.COR_TEXTO_SUAVE};
                        text-transform:uppercase; letter-spacing:0.05em;">{titulo}</div>
            <div style="font-size:28px; font-weight:700; color:#F9FAFB; margin:4px 0;">{valor}</div>
            <div style="font-size:11px; color:#6B7280;">
                <span style="color:{cor}; font-weight:600; margin-right:4px;">Meta:</span>{meta}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def cor_por_meta(valor: float, meta: float) -> str:
    """Verde se atingiu a meta, âmbar se está perto (até 5 pontos abaixo), vermelho se longe."""
    if valor >= meta:
        return config.COR_OK
    if valor >= meta - 5:
        return config.COR_ATENCAO
    return config.COR_CRITICO


def menu_lateral() -> str:
    with st.sidebar:
        st.markdown(
            f"<h3 style='color:{config.COR_TEXTO}; font-size:16px; margin-bottom:16px;'>PAINEL DE CONTROLE</h3>",
            unsafe_allow_html=True,
        )
        return option_menu(
            menu_title=None,
            options=["Visão Geral", "Paradas", "Qualidade", "Manutenção", "Dados"],
            icons=["speedometer2", "pause-circle", "check2-circle", "wrench", "table"],
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": config.COR_TEXTO_SUAVE, "font-size": "14px"},
                "nav-link": {"font-size": "13px", "text-align": "left", "margin": "2px",
                             "color": "#D1D5DB", "border-radius": "4px"},
                "nav-link-selected": {"background-color": config.COR_BORDA, "color": "#38BDF8",
                                      "font-weight": "600", "border-left": f"3px solid {config.COR_DESTAQUE}"},
            },
        )


def aplicar_tema(fig: go.Figure, altura: int = 300) -> go.Figure:
    """Fundo transparente, grades discretas e fonte clara para todos os gráficos."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=altura,
        margin=dict(l=10, r=10, t=30, b=10),
        font=dict(family="Inter", color=config.COR_TEXTO_SUAVE),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(showgrid=False, color="#6B7280")
    fig.update_yaxes(gridcolor=config.COR_BORDA, color="#6B7280")
    return fig


def gauge_eficiencia(valor: float, meta: float) -> go.Figure:
    """Velocímetro da eficiência global contra a meta."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=valor,
        title={"text": "Eficiência Global (%)", "font": {"size": 14, "color": config.COR_TEXTO_SUAVE}},
        delta={"reference": meta, "increasing": {"color": config.COR_OK}, "decreasing": {"color": config.COR_CRITICO}},
        number={"font": {"size": 36, "color": "#F9FAFB"}, "suffix": "%"},
        gauge={
            "axis": {"range": [None, 100], "tickcolor": "#374151", "tickfont": {"color": "#6B7280"}},
            "bar": {"color": config.COR_DESTAQUE, "thickness": 0.25},
            "bgcolor": config.COR_CARTAO,
            "bordercolor": config.COR_BORDA,
            "steps": [
                {"range": [0, meta - 15], "color": "rgba(239, 68, 68, 0.15)"},
                {"range": [meta - 15, meta], "color": "rgba(245, 158, 11, 0.15)"},
                {"range": [meta, 100], "color": "rgba(16, 185, 129, 0.15)"},
            ],
            "threshold": {"line": {"color": config.COR_ATENCAO, "width": 3}, "thickness": 0.8, "value": meta},
        },
    ))
    return aplicar_tema(fig, altura=240)
