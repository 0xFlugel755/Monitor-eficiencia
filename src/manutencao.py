"""Módulo de manutenção: compara a última manutenção com o intervalo planejado."""

import pandas as pd

from src import config

EM_DIA = "Em dia"
VENCENDO = "Vencendo"
ATRASADA = "Atrasada"


def status_manutencao(
    manutencao: pd.DataFrame,
    hoje=None,
    dias_alerta: int = config.DIAS_ALERTA_MANUTENCAO,
) -> pd.DataFrame:
    """Classifica cada máquina em Em dia, Vencendo ou Atrasada.

    próxima manutenção = última manutenção + intervalo (em dias)
    dias restantes     = próxima manutenção − hoje
    """
    hoje = pd.Timestamp(hoje) if hoje is not None else pd.Timestamp.today().normalize()
    m = manutencao.copy()
    m["proxima_manutencao"] = m["ultima_manutencao"] + pd.to_timedelta(m["intervalo_dias"], unit="D")
    m["dias_restantes"] = (m["proxima_manutencao"] - hoje).dt.days

    def classificar(dias: int) -> str:
        if dias < 0:
            return ATRASADA
        if dias <= dias_alerta:
            return VENCENDO
        return EM_DIA

    m["status"] = m["dias_restantes"].apply(classificar)
    return m.sort_values("dias_restantes").reset_index(drop=True)


def maquinas_atrasadas(manutencao: pd.DataFrame, hoje=None) -> pd.DataFrame:
    """Só as máquinas com manutenção atrasada."""
    s = status_manutencao(manutencao, hoje)
    return s[s["status"] == ATRASADA].reset_index(drop=True)
