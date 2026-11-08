import os

import numpy as np
import matplotlib.pyplot as plt
import re

# ==================================================
# CONFIGURAÇÕES
# ==================================================

arquivos = {
    5: "resultado_5.txt",
    10: "resultado_10.txt",
    15: "resultado_15.txt"
}

cores = {
    5: "blue",
    10: "orange",
    15: "red"
}

# Número de pontos utilizados para desenhar cada círculo
n_pontos = 300


# ==================================================
# LEITURA DOS ARQUIVOS
# ==================================================

def ler_fontes(nome_arquivo):

    fontes = []

    with open(nome_arquivo, "r") as arquivo:

        for linha in arquivo:

            linha = linha.strip()

            if not linha:
                continue

            # Formato com campos identificados:
            # Ranking: 1 l: 12.0366 b: -28.6362 ...

            if "l:" in linha and "b:" in linha:

                valores_l = re.search(
                    r"l:\s*([-+]?\d*\.?\d+)",
                    linha
                )

                valores_b = re.search(
                    r"b:\s*([-+]?\d*\.?\d+)",
                    linha
                )

                if valores_l and valores_b:

                    l = float(valores_l.group(1))
                    b = float(valores_b.group(1))

                    fontes.append((l, b))

            # Formato separado por espaços ou tabulações:
            # Ranking l b S_j Identificacao_da_fonte

            else:

                valores = linha.split()

                if len(valores) < 3:
                    continue

                try:
                    ranking = int(valores[0])
                    l = float(valores[1])
                    b = float(valores[2])

                    fontes.append((l, b))

                except ValueError:
                    continue

    return fontes


# ==================================================
# CÁLCULO DOS CÍRCULOS NA ESFERA CELESTE
# ==================================================

def calcular_circulo(l0, b0, raio, n_pontos=300):

    l0 = np.radians(l0)
    b0 = np.radians(b0)
    raio = np.radians(raio)

    angulos = np.linspace(0, 2*np.pi, n_pontos)

    latitudes = np.arcsin(
        np.sin(b0) * np.cos(raio)
        + np.cos(b0) * np.sin(raio) * np.cos(angulos)
    )

    longitudes = l0 + np.arctan2(
        np.sin(angulos) * np.sin(raio) * np.cos(b0),
        np.cos(raio) - np.sin(b0) * np.sin(latitudes)
    )

    longitudes = np.degrees(longitudes) % 360
    latitudes = np.degrees(latitudes)

    return longitudes, latitudes


# ==================================================
# CONVERSÃO PARA A PROJEÇÃO MOLLWEIDE
# ==================================================

def converter_longitude(l):

    return ((-l + 180) % 360) - 180


# ==================================================
# CONSTRUÇÃO DOS MAPAS
# ==================================================

for janela, nome_arquivo in arquivos.items():

    fontes = ler_fontes(nome_arquivo)

    fig = plt.figure(figsize=(13, 7))
    ax = fig.add_subplot(111, projection="mollweide")

    cor = cores[janela]

    # ----------------------------------------------
    # DESENHAR OS CÍRCULOS DAS FONTES
    # ----------------------------------------------

    for i, (l0, b0) in enumerate(fontes):

        l_circulo, b_circulo = calcular_circulo(
            l0,
            b0,
            janela,
            n_pontos
        )

        x = np.radians(converter_longitude(l_circulo))
        y = np.radians(b_circulo)

        # Interromper linhas que cruzam a descontinuidade
        # da projeção Mollweide
        saltos = np.where(np.abs(np.diff(x)) > np.pi)[0] + 1

        x = np.insert(x, saltos, np.nan)
        y = np.insert(y, saltos, np.nan)

        ax.plot(
            x,
            y,
            color=cor,
            linewidth=1.2,
            alpha=0.8,
            label=f"Janela angular: {janela}°" if i == 0 else None
        )

    # ----------------------------------------------
    # MARCAR AS POSIÇÕES DAS FONTES
    # ----------------------------------------------

    longitudes_fontes = np.array([fonte[0] for fonte in fontes])
    latitudes_fontes = np.array([fonte[1] for fonte in fontes])

    x_fontes = np.radians(converter_longitude(longitudes_fontes))
    y_fontes = np.radians(latitudes_fontes)

    ax.scatter(
        x_fontes,
        y_fontes,
        color="black",
        s=25,
        marker="o",
        label="Fontes astrofísicas",
        zorder=5
    )

    # ----------------------------------------------
    # CONFIGURAÇÕES DO MAPA
    # ----------------------------------------------

    ticks_graus = np.arange(-180, 181, 30)
    ticks_rad = np.radians(ticks_graus)

    rotulos = [
        str(int((-t) % 360))
        for t in ticks_graus
    ]

    ax.set_xticks(ticks_rad)
    ax.set_xticklabels(rotulos)

    ax.set_xlabel("Longitude galáctica (°)", fontsize=12)
    ax.set_ylabel("Latitude galáctica (°)", fontsize=12)

    ax.set_title(
        f"Fontes astrofísicas e janelas angulares de {janela}°",
        fontsize=15,
        pad=20
    )

    ax.grid(True, linestyle="--", alpha=0.5)

    ax.legend(loc="upper right", fontsize=10)

    plt.tight_layout()

        # ----------------------------------------------
    # SALVAR MAPA
    # ----------------------------------------------

    plt.tight_layout()

    nome_saida = f"Mapa_Janela_Angular_{janela}.png"

    caminho_saida = os.path.abspath(nome_saida)

    fig.savefig(
        caminho_saida,
        dpi=300,
        bbox_inches="tight"
    )

    print(f"Mapa salvo com sucesso: {caminho_saida}")

    plt.show()
    plt.close(fig)
