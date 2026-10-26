"""Resumo único no terminal + diagnóstico de causa e efeito."""

import pandas as pd

from src import config
from src.eficiencia import eficiencia_global, eficiencia_por
from src.manutencao import ATRASADA, status_manutencao
from src.paradas import causa_principal_da_estacao, top_causas
from src.qualidade import estacoes_com_refugo_alto


def diagnostico(dados: dict[str, pd.DataFrame], hoje=None) -> list[str]:
    """Frases de causa e efeito: por que a pior estação está abaixo da meta."""
    ef = eficiencia_por(dados["producao"], "estacao")
    if ef.empty:
        return []

    pior = ef.iloc[0]
    frases = [f"A estação com menor eficiência é {pior['estacao']} ({pior['eficiencia']}%)."]

    causa = causa_principal_da_estacao(dados["paradas"], pior["estacao"])
    if causa:
        frases.append(f"A principal causa de parada nela é: {causa}.")

    manut = status_manutencao(dados["manutencao"], hoje)
    atrasadas = manut[(manut["estacao"] == pior["estacao"]) & (manut["status"] == ATRASADA)]
    if causa == "Manutenção" and not atrasadas.empty:
        maquinas = ", ".join(atrasadas["maquina"])
        frases.append(
            f"Há manutenção atrasada ({maquinas}). Ação sugerida: cumprir o plano de manutenção preventiva."
        )
    return frases


def montar_resumo(dados: dict[str, pd.DataFrame], hoje=None) -> str:
    """Texto com os 4 blocos do monitor + diagnóstico."""
    linhas = ["=" * 60, "MONITOR DE EFICIÊNCIA – POWERTRAIN (dados fictícios)", "=" * 60]

    # 1) Eficiência por estação
    linhas.append(f"\n1) EFICIÊNCIA POR ESTAÇÃO (meta {config.META_EFICIENCIA:.0f}%)")
    for _, r in eficiencia_por(dados["producao"]).iterrows():
        marca = "OK " if r["eficiencia"] >= config.META_EFICIENCIA else "ABAIXO"
        linhas.append(f"   {r['estacao']:<20} {r['eficiencia']:>5.1f}%  [{marca}]")
    linhas.append(f"   {'Global':<20} {eficiencia_global(dados['producao']):>5.1f}%")

    # 2) Top 3 causas de parada
    linhas.append("\n2) AS 3 MAIORES CAUSAS DE PARADA")
    for _, r in top_causas(dados["paradas"]).iterrows():
        linhas.append(f"   {r['causa']:<20} {r['minutos_parados']:>6.0f} min ({r['percentual']}%)")

    # 3) Refugo acima do limite
    linhas.append(f"\n3) REFUGO ACIMA DO LIMITE ({config.LIMITE_REFUGO}%)")
    alto = estacoes_com_refugo_alto(dados["producao"])
    if alto.empty:
        linhas.append("   Nenhuma estação acima do limite.")
    for _, r in alto.iterrows():
        linhas.append(f"   {r['estacao']:<20} refugo {r['refugo_pct']:.2f}%  | FTT {r['ftt_pct']:.2f}%")

    # 4) Manutenção atrasada
    linhas.append("\n4) MÁQUINAS COM MANUTENÇÃO ATRASADA")
    manut = status_manutencao(dados["manutencao"], hoje)
    atrasadas = manut[manut["status"] == ATRASADA]
    if atrasadas.empty:
        linhas.append("   Nenhuma máquina atrasada.")
    for _, r in atrasadas.iterrows():
        linhas.append(f"   {r['maquina']:<12} ({r['estacao']}) atrasada há {abs(r['dias_restantes'])} dias")

    # Diagnóstico
    linhas.append("\nDIAGNÓSTICO (causa e efeito)")
    for frase in diagnostico(dados, hoje):
        linhas.append(f"   - {frase}")

    return "\n".join(linhas)
