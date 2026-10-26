# Monitor de Eficiência

Monitor em **Python** que acompanha a eficiência da montagem de motores e **explica por que ela cai**, olhando paradas, refugo e manutenção no mesmo lugar. Funciona de duas formas: um **resumo no terminal** e um **dashboard web** (Streamlit), ambos lendo uma planilha Excel.

> **Todos os dados são fictícios.** O projeto é inspirado em indicadores comuns da indústria e não representa o sistema de nenhuma empresa. Não usa Power BI.

---

## Por que este projeto foi criado

- **Aprender Python na prática**, com um problema real: ler planilhas, calcular indicadores e organizar um programa em módulos.
- **Entender como a eficiência de uma linha é acompanhada** na indústria (Powertrain = parte do veículo que gera e transmite potência: motor, câmbio e componentes).
- **Mostrar causa e efeito.** Muitos painéis só mostram que a eficiência caiu. Este mostra o porquê: *a usinagem teve a menor eficiência → a principal causa de parada foi manutenção → a máquina estava com a preventiva atrasada → a primeira ação é cumprir o plano de manutenção.*
- **Evitar ferramentas pagas ou fechadas** (como o Power BI): tudo é código aberto, gratuito e roda em qualquer computador.

---

## Stacks utilizadas

| Tecnologia | Para que serve no projeto |
| --- | --- |
| **Python 3.10+** | Linguagem principal |
| **pandas** | Ler a planilha, agrupar e calcular os indicadores |
| **openpyxl** | Permite ao pandas ler e gravar arquivos `.xlsx` |
| **NumPy** | Gerar os dados fictícios com números aleatórios controlados |
| **Streamlit** | Transformar o código Python em um dashboard web, sem precisar de HTML/JavaScript |
| **Plotly** | Gráficos interativos (barras, linhas, Pareto, velocímetro) |
| **streamlit-option-menu** | Menu lateral com ícones |
| **CSS (injetado)** | Visual "Dark Industrial Tech", baseado no guia de estilização |

---

## Estrutura do projeto

```
monitor-eficiencia/
├── app.py               # Dashboard Streamlit (interface web)
├── main.py              # Versão terminal (imprime o resumo)
├── gerar_dados.py       # Cria a planilha de exemplo com dados fictícios
├── requirements.txt     # Bibliotecas que precisam ser instaladas
├── dados/
│   └── planilha_exemplo.xlsx   # (criada pelo gerar_dados.py)
└── src/
    ├── config.py        # Metas, limites, nomes de colunas e cores
    ├── dados.py         # Leitura e validação da planilha
    ├── eficiencia.py    # Módulo núcleo: produzido ÷ meta × 100
    ├── paradas.py       # Pareto das causas de parada
    ├── qualidade.py     # Refugo, retrabalho e FTT
    ├── manutencao.py    # Em dia / vencendo / atrasada
    ├── resumo.py        # Resumo do terminal e diagnóstico causa-efeito
    └── estilo.py        # Tema escuro, cartões de KPI e gráficos
```

### Os quatro módulos

| Módulo | O que faz | Resultado que mostra |
| --- | --- | --- |
| Eficiência (núcleo) | Compara produzido com a meta por estação e turno | % de eficiência |
| Paradas | Soma os minutos parados por causa | Pareto das principais causas |
| Qualidade | Calcula refugo e retrabalho | % de refugo e alerta acima do limite |
| Manutenção | Compara a última manutenção com o intervalo planejado | Em dia, vencendo ou atrasada |

### Indicadores

| Indicador | Como calcula |
| --- | --- |
| Eficiência | produzido ÷ meta × 100 |
| Refugo | peças descartadas ÷ produzido × 100 |
| Retrabalho | motores que voltaram após o teste ÷ produzido × 100 |
| FTT (First Time Through) | % que passou de primeira, sem retrabalho |
| Tempo parado | soma dos minutos parados, agrupada por causa |
| Manutenção | próxima = última + intervalo; atrasada se já passou, vencendo se faltam ≤ 7 dias |

---

## Passo a passo para executar

### 1) O que baixar e instalar

1. **Python 3.10 ou mais novo** – baixe em <https://www.python.org/downloads/>. No Windows, marque a opção **"Add Python to PATH"** durante a instalação.
2. **Um editor de código** (opcional, mas recomendado) – por exemplo o [VS Code](https://code.visualstudio.com/).
3. **Este projeto** – baixe a pasta `monitor-eficiencia` (ou o `.zip`) e extraia onde preferir.

Para conferir se o Python está instalado, abra o terminal e rode:

```bash
python --version
```

> No Linux/macOS pode ser necessário usar `python3` no lugar de `python`.

### 2) Abrir o terminal dentro da pasta do projeto

```bash
cd caminho/para/monitor-eficiencia
```

No VS Code: *File → Open Folder* e depois *Terminal → New Terminal*.

### 3) Criar um ambiente virtual (recomendado)

Ele mantém as bibliotecas do projeto isoladas do resto do computador.

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (Prompt de Comando):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Quando ativar, aparece `(.venv)` no começo da linha do terminal.

> Se o PowerShell bloquear o script, rode uma vez: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

### 4) Instalar as bibliotecas

```bash
pip install -r requirements.txt
```

### 5) Gerar a planilha de exemplo (dados fictícios)

```bash
python gerar_dados.py
```

Isso cria `dados/planilha_exemplo.xlsx` com três abas (Produção, Paradas e Manutenção), com 30 dias de dados terminando ontem.

### 6) Rodar

**Opção A – Resumo no terminal**

```bash
python main.py
```

## DISPLAY DO MONITOR
<img width="1918" height="966" alt="Screenshot From 2026-10-25 22-30-37" src="https://github.com/user-attachments/assets/e66199eb-bab7-4ce5-9e88-3280ef1a8e9f" />

Mostra os quatro blocos (eficiência por estação, 3 maiores causas de parada, refugo acima do limite e máquinas com manutenção atrasada) e o diagnóstico de causa e efeito.

**Opção B – Dashboard web**

```bash
streamlit run app.py
```

O navegador abre sozinho em `http://localhost:8501`. Para encerrar, volte ao terminal e aperte `Ctrl + C`.

No dashboard você pode:
- navegar entre **Visão Geral, Paradas, Qualidade, Manutenção e Dados**;
- filtrar o **período** e ajustar a **meta de eficiência** e o **limite de refugo** na barra lateral;
- **enviar a sua própria planilha** `.xlsx` pelo botão da barra lateral.

---

## Usando a sua própria planilha

Um único arquivo Excel com **três abas**. Acentos e maiúsculas nos nomes não importam.

| Aba | Colunas |
| --- | --- |
| Produção | data, turno, estação, meta, produzido, refugo, retrabalho |
| Paradas | data, turno, estação, minutos parados, causa |
| Manutenção | máquina, estação, última manutenção, intervalo em dias |

Causas de parada usadas nos dados fictícios: falta de material, manutenção, setup e qualidade (você pode usar outras).

Para rodar no terminal com a sua planilha:

```bash
python main.py caminho/da/sua_planilha.xlsx
```

No dashboard, use o botão **"Usar minha planilha"** na barra lateral.

---

## Personalizando

Tudo que é regra de negócio está em `src/config.py`:

- `META_EFICIENCIA` – meta de eficiência (padrão 90%)
- `LIMITE_REFUGO` – refugo acima disso dispara alerta (padrão 2%)
- `DIAS_ALERTA_MANUTENCAO` – quantos dias antes a manutenção vira "vencendo" (padrão 7)
- cores do tema escuro

---

## Problemas comuns

| Problema | Solução |
| --- | --- |
| `python` não é reconhecido | Reinstale o Python marcando "Add Python to PATH" ou use `py` (Windows) / `python3` (Linux/macOS) |
| `ModuleNotFoundError` | O ambiente virtual não está ativo ou faltou o `pip install -r requirements.txt` |
| `Planilha não encontrada` | Rode `python gerar_dados.py` antes |
| `Na aba ... faltam as colunas` | Confira se os nomes das colunas da sua planilha batem com a tabela acima |
| Porta 8501 ocupada | `streamlit run app.py --server.port 8502` |

---

## Melhorias futuras

- Alertas automáticos (e-mail ou mensagem) quando o refugo passar do limite
- OEE completo (disponibilidade × desempenho × qualidade)
- Leitura de dados em tempo real (sensores ou banco de dados)
- Exportar o resumo em PDF

---

## Aviso

Projeto de estudo. Os dados são fictícios e os indicadores são inspirados em práticas comuns da indústria, sem relação com o sistema de qualquer empresa específica.
