"""Configurações do monitor: metas, limites e cores.

Mexa aqui para ajustar as regras sem mexer na lógica dos módulos.
"""

# --- Metas e limites (valores fictícios, ajuste como quiser) ---
META_EFICIENCIA = 90.0      # % de eficiência considerada boa
LIMITE_REFUGO = 2.0         # % de refugo acima da qual dispara alerta
DIAS_ALERTA_MANUTENCAO = 7  # faltando até X dias, a manutenção é "vencendo"

# --- Nomes padronizados das colunas (depois da normalização) ---
COLUNAS_PRODUCAO = ["data", "turno", "estacao", "meta", "produzido", "refugo", "retrabalho"]
COLUNAS_PARADAS = ["data", "turno", "estacao", "minutos_parados", "causa"]
COLUNAS_MANUTENCAO = ["maquina", "estacao", "ultima_manutencao", "intervalo_dias"]

# --- Apelidos aceitos para colunas (nome da planilha -> nome padronizado) ---
APELIDOS_COLUNAS = {"intervalo_em_dias": "intervalo_dias"}

# --- Nomes das abas esperadas no Excel (também aceita sem acento/maiúsculas) ---
ABA_PRODUCAO = "producao"
ABA_PARADAS = "paradas"
ABA_MANUTENCAO = "manutencao"

# --- Paleta "Dark Industrial Tech" (do guia de estilização) ---
COR_FUNDO = "#0B0F19"
COR_CARTAO = "#111827"
COR_BORDA = "#1F2937"
COR_DESTAQUE = "#0EA5E9"
COR_CRITICO = "#EF4444"
COR_ATENCAO = "#F59E0B"
COR_OK = "#10B981"
COR_TEXTO = "#F3F4F6"
COR_TEXTO_SUAVE = "#9CA3AF"
