import numpy as np
import matplotlib.pyplot as plt
import re

# Arquivos de entrada
arquivos = {
    "10–20": "Eventos_com_Energia_Maior_Que_10.txt",
    "20–40": "Eventos_com_Energia_Maior_Que_20.txt",
    "40–60": "Eventos_com_Energia_Maior_Que_40.txt",
    "≥ 60": "Eventos_com_Energia_Maior_Que_60.txt"
}

# Cores de cada faixa de energia
cores = {
    "10–20": "blue",
    "20–40": "orange",
    "40–60": "green",
    "≥ 60": "red"
}

# Leitura dos arquivos
eventos = {}

for faixa, arquivo in arquivos.items():

    eventos[faixa] = {}

    with open(arquivo, "r") as entrada:

        for linha in entrada:

            if linha.startswith("#") or not linha.strip():
                continue

            valores = re.findall(
                r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?",
                linha
            )

            if len(valores) < 4:
                continue

            aug_id = int(float(valores[0]))
            l = float(valores[1])
            b = float(valores[2])
            energia = float(valores[3])

            eventos[faixa][aug_id] = (l, b, energia)


# Separação das faixas de energia sem duplicar eventos
ids_10 = set(eventos["10–20"].keys())
ids_20 = set(eventos["20–40"].keys())
ids_40 = set(eventos["40–60"].keys())
ids_60 = set(eventos["≥ 60"].keys())

faixas_exclusivas = {
    "10–20": ids_10 - ids_20,
    "20–40": ids_20 - ids_40,
    "40–60": ids_40 - ids_60,
    "≥ 60": ids_60
}


# Função para criar um mapa
def criar_mapa(faixas, nome_arquivo, titulo):

    fig = plt.figure(figsize=(12, 7))
    ax = fig.add_subplot(111, projection="mollweide")

    for faixa, ids in faixas.items():

        longitudes = []
        latitudes = []

        for aug_id in ids:

            l, b, energia = eventos[faixa][aug_id]

            longitudes.append(l)
            latitudes.append(b)

        longitudes = np.array(longitudes)
        latitudes = np.array(latitudes)

        longitudes = np.array(longitudes)
        latitudes = np.array(latitudes)

        # Manter apenas coordenadas válidas
        validos = (
            np.isfinite(longitudes) &
            np.isfinite(latitudes) &
            (latitudes >= -90) &
            (latitudes <= 90)
        )

        longitudes = longitudes[validos]
        latitudes = latitudes[validos]

        # Conversão para radianos e inversão do eixo galáctico
        x = np.radians(longitudes - 180)
        y = np.radians(latitudes)


        ax.scatter(
            x,
            y,
            s=5,
            color=cores[faixa],
            label=f"{faixa} ({len(ids)} eventos)",
            alpha=0.7,
            rasterized=True
        )

    ax.set_title(titulo, pad=20)
    ax.set_xlabel("Longitude Galáctica")
    ax.set_ylabel("Latitude Galáctica")
    ax.grid(True)
    ax.legend(loc="upper right", fontsize=9)

    plt.tight_layout()
    plt.savefig(nome_arquivo, dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()


# Gerar um mapa para cada faixa de energia
for faixa in faixas_exclusivas:

    criar_mapa(
        {faixa: faixas_exclusivas[faixa]},
        f"Mapa_Eventos_{faixa.replace('–', '_').replace('≥', 'maior_igual')}.png",
        f"Distribuição Galáctica dos Raios Cósmicos: {faixa}"
    )


# Gerar o mapa com todas as faixas de energia
criar_mapa(
    faixas_exclusivas,
    "Mapa_Eventos_Todas_Energias.png",
    "Distribuição Galáctica dos Raios Cósmicos por Faixa de Energia"
)
