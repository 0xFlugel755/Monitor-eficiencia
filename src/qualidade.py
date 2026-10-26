"""Módulo de qualidade: refugo, retrabalho e FTT (First Time Through)."""

import pandas as pd

from src import config


def indicadores_qualidade(producao: pd.DataFrame, limite_refugo: float = config.LIMITE_REFUGO) -> pd.DataFrame:
    """Calcula refugo %, retrabalho %, FTT % e o alerta por estação.

    - Refugo %     = peças descartadas ÷ produzido × 100
    - Retrabalho % = motores que voltaram ÷ produzido × 100
    - FTT %        = (produzido − retrabalho) ÷ produzido × 100  (passou de primeira)
    """
    q = producao.groupby("estacao", as_index=False)[["produzido", "refugo", "retrabalho"]].sum()
    produzido = q["produzido"].where(q["produzido"] > 0)  # evita divisão por zero
    q["refugo_pct"] = (q["refugo"] / produzido * 100).round(2)
    q["retrabalho_pct"] = (q["retrabalho"] / produzido * 100).round(2)
    q["ftt_pct"] = ((q["produzido"] - q["retrabalho"]) / produzido * 100).round(2)
    q["alerta"] = q["refugo_pct"] > limite_refugo
    return q.sort_values("refugo_pct", ascending=False).reset_index(drop=True)


def estacoes_com_refugo_alto(producao: pd.DataFrame, limite_refugo: float = config.LIMITE_REFUGO) -> pd.DataFrame:
    """Só as estações que estouraram o limite de refugo."""
    q = indicadores_qualidade(producao, limite_refugo)
    return q[q["alerta"]].reset_index(drop=True)
