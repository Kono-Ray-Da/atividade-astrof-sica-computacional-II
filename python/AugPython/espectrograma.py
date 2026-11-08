
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.colors import LogNorm

# ==================================================
# CONFIGURAÇÕES
# ==================================================

arquivo = "Espectrograma_Medio.txt"

# Limites da escala de cores.
# None = escolha automática.
vmin_ch0 = 5
vmax_ch0 = 10000

vmin_ch1 = 5
vmax_ch1 = 10000

# Mapa de cores
colormap = "plasma"

# ==================================================
# LEITURA DOS DADOS
# ==================================================

dados = pd.read_csv(arquivo, sep=r"\s+")

# Organiza os dados em matrizes:
# linhas = frequências
# colunas = LST

espectro_ch0 = dados.pivot(
    index="Frequencia",
    columns="LST",
    values="Media_CH0"
)

espectro_ch1 = dados.pivot(
    index="Frequencia",
    columns="LST",
    values="Media_CH1"
)

# ==================================================
# FUNÇÃO PARA GERAR O ESPECTROGRAMA
# ==================================================

def plot_espectrograma(espectro, canal, vmin=10, vmax=None):

    lst = espectro.columns.values
    frequencia = espectro.index.values

    # Valores de potência
    potencia = espectro.values.astype(float)

    # Valores positivos para calcular o limite superior
    valores_validos = potencia[
        np.isfinite(potencia) & (potencia > 0)
    ]

    # Se vmax não for definido, utiliza o percentil 99
    if vmax is None:
        vmax = np.nanpercentile(valores_validos, 99)

    # Evita que a escala logarítmica receba limites inválidos
    if vmax <= vmin:
        raise ValueError("O vmax precisa ser maior que o vmin.")

    # Mascara valores nulos ou negativos
    potencia = np.ma.masked_less_equal(potencia, 0)

    fig, ax = plt.subplots(figsize=(12, 7))

    imagem = ax.pcolormesh(
        lst,
        frequencia,
        potencia,
        shading="auto",
        cmap="plasma",
        norm=LogNorm(vmin=vmin, vmax=vmax)
    )

    # Barra de cores
    barra = fig.colorbar(imagem, ax=ax)
    barra.set_label("Potência média", fontsize=13)

    # Eixos
    ax.set_xlabel("LST", fontsize=13)
    ax.set_ylabel("Frequência", fontsize=13)

    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(5))

    ax.set_xlim(0, 24)
    ax.set_ylim(30, 81)

    ax.tick_params(axis="both", labelsize=10)

    ax.set_title(f"Espectrograma - {canal}", fontsize=15)

    fig.tight_layout()

    nome_arquivo = f"Espectrograma_{canal}.png"

    fig.savefig(nome_arquivo, dpi=300, bbox_inches="tight")

    plt.show()

    print(f"Imagem salva: {nome_arquivo}")


# ==================================================
# ESPECTROGRAMA CH0
# ==================================================

plot_espectrograma(
    espectro_ch0,
    "CH0",
    vmin_ch0,
    vmax_ch0
)

# ==================================================
# ESPECTROGRAMA CH1
# ==================================================

plot_espectrograma(
    espectro_ch1,
    "CH1",
    vmin_ch1,
    vmax_ch1
)

