
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# 1. CONFIGURAÇÕES MANUAIS
# ============================================================

ARQUIVO = "Perfil_Espectral.txt"

# Intervalo de frequência
FREQ_MIN = None
FREQ_MAX = None

# Canais que serão exibidos
MOSTRAR_CH0 = True
MOSTRAR_CH1 = True

# Mostrar dispersão entre antenas?
MOSTRAR_DESVIO = True

# Aparência do gráfico
TAMANHO_FIGURA = (12, 6)
ESPESSURA_LINHA = 2
TRANSPARENCIA_DESVIO = 0.18

# Unidades (preencha se souber)
UNIDADE_FREQUENCIA = ""
UNIDADE_POTENCIA = ""

# Salvar imagem
SALVAR_IMAGEM = True
ARQUIVO_SAIDA = "Perfil_Espectral_Medio_Todas_Antenas.png"
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
        f"Erro: arquivo '{ARQUIVO}' não encontrado."
    )


# Converter colunas numéricas
colunas_numericas = [
    "Antena",
    "Frequencia",
    "Media_CH0",
    "Desvio_CH0",
    "Media_CH1",
    "Desvio_CH1"
]

for coluna in colunas_numericas:
    dados[coluna] = pd.to_numeric(
        dados[coluna],
        errors="coerce"
    )


# ============================================================
# 3. SELEÇÃO DO INTERVALO DE FREQUÊNCIA
# ============================================================

if FREQ_MIN is not None:
    dados = dados[dados["Frequencia"] >= FREQ_MIN]

if FREQ_MAX is not None:
    dados = dados[dados["Frequencia"] <= FREQ_MAX]

if dados.empty:
    raise SystemExit(
        "Não existem dados no intervalo de frequência escolhido."
    )


# ============================================================
# 4. MÉDIA E DESVIO PADRÃO ENTRE ANTENAS
# ============================================================

perfil = dados.groupby("Frequencia").agg(
    Media_CH0=("Media_CH0", "mean"),
    Desvio_CH0=("Media_CH0", "std"),
    N_CH0=("Media_CH0", "count"),

    Media_CH1=("Media_CH1", "mean"),
    Desvio_CH1=("Media_CH1", "std"),
    N_CH1=("Media_CH1", "count")
).reset_index()

perfil = perfil.sort_values("Frequencia")

# ============================================================
# 5. CONSTRUÇÃO DO GRÁFICO
# ============================================================

fig, ax = plt.subplots(figsize=TAMANHO_FIGURA)

frequencia = perfil["Frequencia"]


# -------------------------
# Canal CH0
# -------------------------

if MOSTRAR_CH0:

    media0 = perfil["Media_CH0"]
    desvio0 = perfil["Desvio_CH0"]

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

    media1 = perfil["Media_CH1"]
    desvio1 = perfil["Desvio_CH1"]

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
    "Perfil Espectral Médio - Todas as Antenas",
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
# 7. SALVAR IMAGEM
# ============================================================

if SALVAR_IMAGEM:

    plt.savefig(
        ARQUIVO_SAIDA,
        dpi=DPI,
        bbox_inches="tight"
    )

    print(
        "Imagem salva em:",
        Path(ARQUIVO_SAIDA).resolve()
    )


# ============================================================
# 8. EXIBIR RESULTADOS
# ============================================================

print("\nNúmero de antenas utilizadas por frequência:")
print(
    perfil[["Frequencia", "N_CH0", "N_CH1"]].to_string(index=False)
)

plt.show()

