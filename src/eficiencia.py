"""Módulo núcleo: eficiência = produzido ÷ meta × 100."""

import pandas as pd


def eficiencia_por(producao: pd.DataFrame, agrupar_por: str = "estacao") -> pd.DataFrame:
    """Calcula a eficiência agrupando por estação, turno ou data."""
    agrupado = producao.groupby(agrupar_por, as_index=False)[["meta", "produzido"]].sum()
    # evita divisão por zero se a meta somar 0
    agrupado["eficiencia"] = (agrupado["produzido"] / agrupado["meta"].where(agrupado["meta"] > 0) * 100).round(1)
    return agrupado.sort_values("eficiencia").reset_index(drop=True)


def eficiencia_global(producao: pd.DataFrame) -> float:
    """Eficiência de todas as estações juntas."""
    meta = producao["meta"].sum()
    if meta == 0:
        return 0.0
    return round(producao["produzido"].sum() / meta * 100, 1)


def eficiencia_diaria(producao: pd.DataFrame) -> pd.DataFrame:
    """Eficiência dia a dia (para o gráfico de linha)."""
    return eficiencia_por(producao, "data").sort_values("data").reset_index(drop=True)
