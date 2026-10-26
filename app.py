"""Dashboard Streamlit do Monitor de Eficiência (dados fictícios).

Executar com:  streamlit run app.py
"""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src import config
from src.dados import carregar_planilha, filtrar_periodo
from src.eficiencia import eficiencia_diaria, eficiencia_global, eficiencia_por
from src.estilo import (aplicar_tema, cartao_kpi, cor_por_meta, gauge_eficiencia,
                        injetar_css, menu_lateral, titulo_secao)
from src.manutencao import ATRASADA, EM_DIA, VENCENDO, status_manutencao
from src.paradas import pareto_paradas
from src.qualidade import indicadores_qualidade
from src.resumo import diagnostico

PLANILHA_PADRAO = Path("dados/planilha_exemplo.xlsx")

st.set_page_config(page_title="Monitor de Eficiência", page_icon="⚡", layout="wide")
injetar_css()
pagina = menu_lateral()

# ---------- Barra lateral: origem dos dados e filtros ----------
with st.sidebar:
    st.markdown("---")
    enviado = st.file_uploader("Usar minha planilha (.xlsx)", type=["xlsx"])
    meta_ef = st.slider("Meta de eficiência (%)", 70, 100, int(config.META_EFICIENCIA))
    limite_ref = st.slider("Limite de refugo (%)", 0.5, 5.0, float(config.LIMITE_REFUGO), 0.5)

fonte = enviado if enviado is not None else PLANILHA_PADRAO
try:
    dados_completos = carregar_planilha(fonte)
except (FileNotFoundError, ValueError) as erro:
    st.error(f"Não foi possível carregar a planilha: {erro}")
    st.stop()

data_min = dados_completos["producao"]["data"].min().date()
data_max = dados_completos["producao"]["data"].max().date()
with st.sidebar:
    periodo = st.date_input("Período", (data_min, data_max), min_value=data_min, max_value=data_max)
if len(periodo) != 2:  # o usuário ainda está escolhendo a segunda data
    st.stop()

dados = filtrar_periodo(dados_completos, *periodo)
producao, paradas = dados["producao"], dados["paradas"]
if producao.empty:
    st.warning("Não há dados de produção neste período.")
    st.stop()

# ---------- Cabeçalho ----------
st.markdown(
    "<h1 style='font-size:22px; font-weight:700; margin:0;'>MONITOR DE EFICIÊNCIA – POWERTRAIN</h1>"
    f"<p style='color:#6B7280; font-size:12px; margin-top:2px;'>Montagem de motores · "
    f"dados fictícios · {periodo[0]:%d/%m/%Y} a {periodo[1]:%d/%m/%Y}</p>",
    unsafe_allow_html=True,
)

ef_global = eficiencia_global(producao)
ef_estacao = eficiencia_por(producao, "estacao")
qualidade = indicadores_qualidade(producao, limite_ref)
manutencao = status_manutencao(dados["manutencao"])

# ======================= VISÃO GERAL =======================
if pagina == "Visão Geral":
    refugo_global = round(producao["refugo"].sum() / producao["produzido"].sum() * 100, 2)
    ftt_global = round((producao["produzido"].sum() - producao["retrabalho"].sum())
                       / producao["produzido"].sum() * 100, 2)
    atrasadas = int((manutencao["status"] == ATRASADA).sum())

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        cartao_kpi("Eficiência global", f"{ef_global}%", f"≥ {meta_ef}%", cor_por_meta(ef_global, meta_ef))
    with c2:
        cor = config.COR_OK if refugo_global <= limite_ref else config.COR_CRITICO
        cartao_kpi("Refugo", f"{refugo_global}%", f"≤ {limite_ref}%", cor)
    with c3:
        cartao_kpi("FTT (passou de primeira)", f"{ftt_global}%", "quanto maior, melhor", config.COR_DESTAQUE)
    with c4:
        cor = config.COR_OK if atrasadas == 0 else config.COR_CRITICO
        cartao_kpi("Manutenções atrasadas", str(atrasadas), "0", cor)

    col_a, col_b = st.columns([1, 2])
    with col_a:
        titulo_secao("Eficiência contra a meta")
        st.plotly_chart(gauge_eficiencia(ef_global, meta_ef), width="stretch")
    with col_b:
        titulo_secao("Eficiência por estação")
        fig = go.Figure(go.Bar(
            x=ef_estacao["estacao"], y=ef_estacao["eficiencia"],
            marker_color=[cor_por_meta(v, meta_ef) for v in ef_estacao["eficiencia"]],
            text=ef_estacao["eficiencia"].astype(str) + "%", textposition="outside",
        ))
        fig.add_hline(y=meta_ef, line_dash="dash", line_color=config.COR_ATENCAO)
        fig.update_yaxes(range=[0, 110])
        st.plotly_chart(aplicar_tema(fig, 240), width="stretch")

    titulo_secao("Eficiência dia a dia")
    diaria = eficiencia_diaria(producao)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=diaria["data"], y=[meta_ef] * len(diaria), name="Meta",
                             line=dict(color=config.COR_ATENCAO, width=2, dash="dash")))
    fig.add_trace(go.Scatter(x=diaria["data"], y=diaria["eficiencia"], name="Eficiência",
                             line=dict(color=config.COR_DESTAQUE, width=3),
                             fill="tonexty", fillcolor="rgba(14, 165, 233, 0.05)"))
    st.plotly_chart(aplicar_tema(fig, 260), width="stretch")

    titulo_secao("Diagnóstico: por que a eficiência cai?")
    for frase in diagnostico(dados):
        st.markdown(f"- {frase}")

# ======================= PARADAS =======================
elif pagina == "Paradas":
    opcoes = ["Todas as estações"] + sorted(producao["estacao"].unique())
    escolha = st.selectbox("Estação", opcoes)
    pareto = pareto_paradas(paradas, None if escolha == opcoes[0] else escolha)

    titulo_secao("Pareto de paradas (minutos por causa)")
    if pareto.empty:
        st.info("Sem paradas registradas para esta seleção.")
    else:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=pareto["causa"], y=pareto["minutos_parados"], name="Minutos",
                             marker_color=config.COR_DESTAQUE))
        fig.add_trace(go.Scatter(x=pareto["causa"], y=pareto["acumulado"], name="% acumulado",
                                 yaxis="y2", line=dict(color=config.COR_ATENCAO, width=2), mode="lines+markers"))
        fig.update_layout(yaxis2=dict(overlaying="y", side="right", range=[0, 105], showgrid=False,
                                      color="#6B7280"))
        st.plotly_chart(aplicar_tema(fig, 340), width="stretch")
        st.dataframe(pareto.rename(columns={"causa": "Causa", "minutos_parados": "Minutos",
                                            "percentual": "%", "acumulado": "% acumulado"}),
                     hide_index=True, width="stretch")

# ======================= QUALIDADE =======================
elif pagina == "Qualidade":
    titulo_secao("Refugo, retrabalho e FTT por estação")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=qualidade["estacao"], y=qualidade["refugo_pct"], name="Refugo %",
                         marker_color=[config.COR_CRITICO if a else config.COR_OK for a in qualidade["alerta"]]))
    fig.add_trace(go.Bar(x=qualidade["estacao"], y=qualidade["retrabalho_pct"], name="Retrabalho %",
                         marker_color=config.COR_ATENCAO))
    fig.add_hline(y=limite_ref, line_dash="dash", line_color=config.COR_CRITICO,
                  annotation_text=f"limite de refugo {limite_ref}%")
    fig.update_layout(barmode="group")
    st.plotly_chart(aplicar_tema(fig, 320), width="stretch")

    for _, linha in qualidade[qualidade["alerta"]].iterrows():
        st.error(f"ALERTA: {linha['estacao']} está com {linha['refugo_pct']}% de refugo "
                 f"(limite {limite_ref}%).")
    if not qualidade["alerta"].any():
        st.success("Nenhuma estação acima do limite de refugo.")

    st.dataframe(qualidade.drop(columns="alerta").rename(columns={
        "estacao": "Estação", "produzido": "Produzido", "refugo": "Refugo", "retrabalho": "Retrabalho",
        "refugo_pct": "Refugo %", "retrabalho_pct": "Retrabalho %", "ftt_pct": "FTT %"}),
        hide_index=True, width="stretch")

# ======================= MANUTENÇÃO =======================
elif pagina == "Manutenção":
    titulo_secao("Status das máquinas")
    cores = {EM_DIA: config.COR_OK, VENCENDO: config.COR_ATENCAO, ATRASADA: config.COR_CRITICO}
    colunas = st.columns(3)
    for coluna, status in zip(colunas, [EM_DIA, VENCENDO, ATRASADA]):
        with coluna:
            cartao_kpi(status, str(int((manutencao["status"] == status).sum())), "máquinas", cores[status])

    tabela = manutencao.copy()
    tabela["ultima_manutencao"] = tabela["ultima_manutencao"].dt.strftime("%d/%m/%Y")
    tabela["proxima_manutencao"] = tabela["proxima_manutencao"].dt.strftime("%d/%m/%Y")
    tabela = tabela.rename(columns={
        "maquina": "Máquina", "estacao": "Estação", "ultima_manutencao": "Última",
        "intervalo_dias": "Intervalo (dias)", "proxima_manutencao": "Próxima",
        "dias_restantes": "Dias restantes", "status": "Status"})

    def pintar(valor: str) -> str:
        return f"color: {cores.get(valor, 'inherit')}; font-weight: 600"

    st.dataframe(tabela.style.map(pintar, subset=["Status"]), hide_index=True, width="stretch")

# ======================= DADOS =======================
else:
    titulo_secao("Dados carregados (período filtrado)")
    aba = st.radio("Aba", ["Produção", "Paradas", "Manutenção"], horizontal=True)
    tabela = {"Produção": producao, "Paradas": paradas, "Manutenção": dados["manutencao"]}[aba]
    st.dataframe(tabela, hide_index=True, width="stretch")
    st.caption("Todos os dados do projeto são fictícios, criados para fins de estudo.")
