
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# 1. CONFIGURAÇÕES MANUAIS
# ============================================================

# Nome do arquivo de entrada
ARQUIVO = "Perfil_Espectral.txt"

# Identificação da antena que deseja analisar
ID_ANTENA = 11

# Intervalo de frequência
# Use None para não limitar o intervalo
FREQ_MIN = None
FREQ_MAX = None

# Canais que serão exibidos
MOSTRAR_CH0 = True
MOSTRAR_CH1 = True

# Exibir barras/faixas de desvio padrão?
MOSTRAR_DESVIO = True

# Aparência do gráfico
TAMANHO_FIGURA = (11, 6)
ESPESSURA_LINHA = 1.8
TRANSPARENCIA_DESVIO = 0.18

# Título e unidades
UNIDADE_FREQUENCIA = ""  # Ex.: "MHz", se essa for a unidade dos dados
UNIDADE_POTENCIA = ""    # Preencha se souber a unidade da potência

# Salvar imagem?
SALVAR_IMAGEM = True

# Nome da imagem gerada
ARQUIVO_SAIDA = f"Perfil_Espectral_Antena_{ID_ANTENA}.png"

# Resolução da imagem
DPI = 300


# ============================================================
# 2. LEITURA DOS DADOS
# ============================================================

try:
    dados = pd.read_csv(
        ARQUIVO,
        sep=r"\s+",
        na_values=["NA", "NaN", "nan"]
    )

except FileNotFoundError:
    raise SystemExit(
        f"Erro: o arquivo '{ARQUIVO}' não foi encontrado."
    )


# Verificar se as colunas necessárias existem
colunas = [
    "Antena",
    "Frequencia",
    "Media_CH0",
    "Desvio_CH0",
    "Media_CH1",
    "Desvio_CH1"
]

for coluna in colunas:
    if coluna not in dados.columns:
        raise SystemExit(
            f"Erro: a coluna '{coluna}' não foi encontrada."
        )


# ============================================================
# 3. SELEÇÃO DA ANTENA
# ============================================================

dados_antena = dados[dados["Antena"] == ID_ANTENA].copy()

if dados_antena.empty:
    antenas_disponiveis = sorted(dados["Antena"].unique())

    raise SystemExit(
        f"Antena {ID_ANTENA} não encontrada.\n"
        f"Antenas disponíveis: {antenas_disponiveis}"
    )


# Ordenar os dados pela frequência
dados_antena = dados_antena.sort_values("Frequencia")


# ============================================================
# 4. SELEÇÃO DO INTERVALO DE FREQUÊNCIA
# ============================================================

if FREQ_MIN is not None:
    dados_antena = dados_antena[
        dados_antena["Frequencia"] >= FREQ_MIN
    ]

if FREQ_MAX is not None:
    dados_antena = dados_antena[
        dados_antena["Frequencia"] <= FREQ_MAX
    ]

if dados_antena.empty:
    raise SystemExit(
        "Não existem dados para a antena no intervalo escolhido."
    )


# ============================================================
# 5. CONSTRUÇÃO DO GRÁFICO
# ============================================================

fig, ax = plt.subplots(figsize=TAMANHO_FIGURA)

frequencia = dados_antena["Frequencia"]

# -------------------------
# Canal CH0
# -------------------------

if MOSTRAR_CH0:

    media0 = dados_antena["Media_CH0"]
    desvio0 = dados_antena["Desvio_CH0"]

    ax.plot(
        frequencia,
        media0,
        label="CH0",
        linewidth=ESPESSURA_LINHA
    )

    if MOSTRAR_DESVIO:
        ax.fill_between(
            frequencia,
            media0 - desvio0,
            media0 + desvio0,
            alpha=TRANSPARENCIA_DESVIO
        )


# -------------------------
# Canal CH1
# -------------------------

if MOSTRAR_CH1:

    media1 = dados_antena["Media_CH1"]
    desvio1 = dados_antena["Desvio_CH1"]

    ax.plot(
        frequencia,
        media1,
        label="CH1",
        linewidth=ESPESSURA_LINHA
    )

    if MOSTRAR_DESVIO:
        ax.fill_between(
            frequencia,
            media1 - desvio1,
            media1 + desvio1,
            alpha=TRANSPARENCIA_DESVIO
        )


# ============================================================
# 6. FORMATAÇÃO
# ============================================================

ax.set_title(
    f"Perfil Espectral - Antena {ID_ANTENA}",
    fontsize=15
)

if UNIDADE_FREQUENCIA:
    ax.set_xlabel(
        f"Frequência ({UNIDADE_FREQUENCIA})",
        fontsize=12
    )
else:
    ax.set_xlabel("Frequência", fontsize=12)

if UNIDADE_POTENCIA:
    ax.set_ylabel(
        f"Potência média ({UNIDADE_POTENCIA})",
        fontsize=12
    )
else:
    ax.set_ylabel("Potência média", fontsize=12)

ax.grid(True, linestyle="--", alpha=0.4)
ax.legend(fontsize=11)

plt.tight_layout()


# ============================================================
# 7. SALVAR A IMAGEM
# ============================================================

if SALVAR_IMAGEM:

    plt.savefig(
        ARQUIVO_SAIDA,
        dpi=DPI,
        bbox_inches="tight"
    )

    print(f"Imagem salva em: {Path(ARQUIVO_SAIDA).resolve()}")


# ============================================================
# 8. EXIBIR O GRÁFICO
# ============================================================

plt.show()


