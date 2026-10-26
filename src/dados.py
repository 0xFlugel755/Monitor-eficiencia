"""Leitura e validação da planilha Excel (3 abas)."""

import unicodedata
from pathlib import Path

import pandas as pd

from src import config


def _normalizar(texto: str) -> str:
    """Tira acento, põe minúsculo e troca espaço por underline.

    Exemplo: 'Última Manutenção' -> 'ultima_manutencao'.
    Assim a planilha funciona mesmo se o nome das colunas variar um pouco.
    """
    sem_acento = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return sem_acento.strip().lower().replace(" ", "_")


def _achar_aba(abas: list[str], nome_esperado: str) -> str:
    """Encontra a aba pelo nome, ignorando acento e maiúsculas."""
    for aba in abas:
        if _normalizar(aba) == nome_esperado:
            return aba
    raise ValueError(
        f"Não encontrei a aba '{nome_esperado}'. Abas na planilha: {abas}"
    )


def _ler_aba(arquivo, aba: str, colunas: list[str]) -> pd.DataFrame:
    df = pd.read_excel(arquivo, sheet_name=aba)
    df.columns = [config.APELIDOS_COLUNAS.get(_normalizar(c), _normalizar(c)) for c in df.columns]
    faltando = [c for c in colunas if c not in df.columns]
    if faltando:
        raise ValueError(f"Na aba '{aba}' faltam as colunas: {faltando}")
    return df[colunas].dropna(how="all")


def carregar_planilha(arquivo) -> dict[str, pd.DataFrame]:
    """Lê as 3 abas e devolve um dicionário de DataFrames.

    `arquivo` pode ser um caminho (str/Path) ou um arquivo enviado pelo Streamlit.
    """
    if isinstance(arquivo, (str, Path)) and not Path(arquivo).exists():
        raise FileNotFoundError(
            f"Planilha não encontrada: {arquivo}\n"
            "Rode 'python gerar_dados.py' para criar a planilha de exemplo."
        )

    abas = pd.ExcelFile(arquivo).sheet_names

    producao = _ler_aba(arquivo, _achar_aba(abas, config.ABA_PRODUCAO), config.COLUNAS_PRODUCAO)
    paradas = _ler_aba(arquivo, _achar_aba(abas, config.ABA_PARADAS), config.COLUNAS_PARADAS)
    manutencao = _ler_aba(arquivo, _achar_aba(abas, config.ABA_MANUTENCAO), config.COLUNAS_MANUTENCAO)

    # Converte tipos: datas viram datetime e números viram numérico
    producao["data"] = pd.to_datetime(producao["data"])
    paradas["data"] = pd.to_datetime(paradas["data"])
    manutencao["ultima_manutencao"] = pd.to_datetime(manutencao["ultima_manutencao"])

    for coluna in ["meta", "produzido", "refugo", "retrabalho"]:
        producao[coluna] = pd.to_numeric(producao[coluna], errors="coerce").fillna(0)
    paradas["minutos_parados"] = pd.to_numeric(paradas["minutos_parados"], errors="coerce").fillna(0)
    manutencao["intervalo_dias"] = pd.to_numeric(manutencao["intervalo_dias"], errors="coerce")

    return {"producao": producao, "paradas": paradas, "manutencao": manutencao}


def filtrar_periodo(dados: dict[str, pd.DataFrame], inicio, fim) -> dict[str, pd.DataFrame]:
    """Recorta produção e paradas por período (a manutenção não depende de período)."""
    inicio, fim = pd.Timestamp(inicio), pd.Timestamp(fim)
    return {
        "producao": dados["producao"].query("@inicio <= data <= @fim"),
        "paradas": dados["paradas"].query("@inicio <= data <= @fim"),
        "manutencao": dados["manutencao"],
    }
