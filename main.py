"""Versão terminal do monitor: lê a planilha e imprime o resumo.

Uso:
    python main.py                          # usa dados/planilha_exemplo.xlsx
    python main.py caminho/da/planilha.xlsx # usa a sua planilha
"""

import sys

from src.dados import carregar_planilha
from src.resumo import montar_resumo


def main() -> None:
    caminho = sys.argv[1] if len(sys.argv) > 1 else "dados/planilha_exemplo.xlsx"
    dados = carregar_planilha(caminho)
    print(montar_resumo(dados))


if __name__ == "__main__":
    main()
