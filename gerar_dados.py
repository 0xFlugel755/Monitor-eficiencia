"""Gera a planilha de exemplo (dados 100% FICTÍCIOS) em dados/planilha_exemplo.xlsx.

Os números foram montados para contar uma história de causa e efeito:
a usinagem tem a menor eficiência, a principal causa é parada por manutenção
e a máquina CNC-01 está com a preventiva atrasada.
"""

from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

SAIDA = Path("dados/planilha_exemplo.xlsx")
DIAS = 30
TURNOS = ["Manhã", "Tarde", "Noite"]

# estação: (meta por turno, eficiência média, refugo médio %, retrabalho médio %)
ESTACOES = {
    "Usinagem": (120, 0.82, 0.035, 0.010),
    "Montagem do motor": (100, 0.93, 0.015, 0.030),
    "Teste final": (100, 0.96, 0.008, 0.020),
    "Retrabalho": (30, 0.90, 0.010, 0.000),
}

# peso de cada causa de parada por estação (usinagem para mais por manutenção)
CAUSAS = ["Falta de material", "Manutenção", "Setup", "Qualidade"]
PESO_CAUSAS = {
    "Usinagem": [0.15, 0.55, 0.20, 0.10],
    "Montagem do motor": [0.40, 0.15, 0.30, 0.15],
    "Teste final": [0.20, 0.15, 0.20, 0.45],
    "Retrabalho": [0.30, 0.10, 0.20, 0.40],
}


def gerar(semente: int = 42) -> None:
    rng = np.random.default_rng(semente)
    hoje = date.today()
    datas = [hoje - timedelta(days=d) for d in range(DIAS, 0, -1)]

    producao, paradas = [], []
    for dia in datas:
        for turno in TURNOS:
            for estacao, (meta, efic, refugo, retrab) in ESTACOES.items():
                produzido = int(round(meta * rng.normal(efic, 0.04)))
                produzido = max(produzido, 0)
                producao.append(
                    [dia, turno, estacao, meta, produzido,
                     rng.binomial(produzido, refugo), rng.binomial(produzido, retrab)]
                )
                # a menor eficiência gera mais paradas: ~ (1 - eficiência) do turno de 480 min
                if rng.random() < 0.55:
                    minutos = int(rng.uniform(10, 60) * (1.6 if estacao == "Usinagem" else 1.0))
                    causa = rng.choice(CAUSAS, p=PESO_CAUSAS[estacao])
                    paradas.append([dia, turno, estacao, minutos, causa])

    # máquina: (estação, dias desde a última manutenção, intervalo planejado)
    maquinas = [
        ("CNC-01", "Usinagem", 100, 90),            # atrasada
        ("CNC-02", "Usinagem", 83, 90),             # vencendo
        ("MONT-01", "Montagem do motor", 30, 90),   # em dia
        ("MONT-02", "Montagem do motor", 45, 120),  # em dia
        ("TESTE-01", "Teste final", 54, 60),        # vencendo
        ("DINAMO-01", "Teste final", 20, 90),       # em dia
        ("RETR-01", "Retrabalho", 15, 60),          # em dia
    ]
    manutencao = [[m, e, hoje - timedelta(days=dias), intervalo] for m, e, dias, intervalo in maquinas]

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(SAIDA, engine="openpyxl") as escritor:
        pd.DataFrame(producao, columns=["data", "turno", "estação", "meta", "produzido", "refugo", "retrabalho"]
                     ).to_excel(escritor, sheet_name="Produção", index=False)
        pd.DataFrame(paradas, columns=["data", "turno", "estação", "minutos parados", "causa"]
                     ).to_excel(escritor, sheet_name="Paradas", index=False)
        pd.DataFrame(manutencao, columns=["máquina", "estação", "última manutenção", "intervalo em dias"]
                     ).to_excel(escritor, sheet_name="Manutenção", index=False)

    print(f"Planilha de exemplo criada em: {SAIDA}")


if __name__ == "__main__":
    gerar()
