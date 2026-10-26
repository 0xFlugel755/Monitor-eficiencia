"""Módulo de paradas: soma minutos por causa e monta o Pareto."""

import pandas as pd


def pareto_paradas(paradas: pd.DataFrame, estacao: str | None = None) -> pd.DataFrame:
    """Minutos parados por causa, do maior para o menor, com % acumulado.

    O Pareto mostra que poucas causas costumam explicar a maior parte das perdas.
    """
    base = paradas if estacao is None else paradas[paradas["estacao"] == estacao]
    por_causa = (
        base.groupby("causa", as_index=False)["minutos_parados"].sum()
        .sort_values("minutos_parados", ascending=False)
        .reset_index(drop=True)
    )
    total = por_causa["minutos_parados"].sum()
    por_causa["percentual"] = (por_causa["minutos_parados"] / total * 100).round(1) if total else 0.0
    por_causa["acumulado"] = por_causa["percentual"].cumsum().round(1)
    return por_causa


def top_causas(paradas: pd.DataFrame, n: int = 3) -> pd.DataFrame:
    """As n maiores causas de parada."""
    return pareto_paradas(paradas).head(n)


def causa_principal_da_estacao(paradas: pd.DataFrame, estacao: str) -> str | None:
    """Maior causa de parada de uma estação (usada no diagnóstico causa-efeito)."""
    pareto = pareto_paradas(paradas, estacao)
    return None if pareto.empty else str(pareto.loc[0, "causa"])
