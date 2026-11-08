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

            valores = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", linha)

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

# Criação do mapa
fig = plt.figure(figsize=(12, 7))
ax = fig.add_subplot(111, projection="mollweide")

for faixa, ids in faixas_exclusivas.items():

    longitudes = []
    latitudes = []

    for aug_id in ids:

        # Recupera as coordenadas do evento
        if aug_id in eventos[faixa]:
            l, b, energia = eventos[faixa][aug_id]

        elif faixa == "10–20":
            l, b, energia = eventos["10–20"][aug_id]

        longitudes.append(l)
        latitudes.append(b)

    longitudes = np.array(longitudes)
    latitudes = np.array(latitudes)

    # Conversão para radianos e inversão do eixo galáctico
    x = np.radians(((180 - longitudes + 180) % 360) - 180)
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

# Configurações do mapa
ax.set_title("Distribuição Galáctica dos Raios Cósmicos por Energia", pad=20)
ax.set_xlabel("Longitude Galáctica")
ax.set_ylabel("Latitude Galáctica")
ax.grid(True)

ax.legend(loc="upper right", fontsize=9)

plt.tight_layout()

# Salvar imagem
plt.savefig("Mapa_Eventos_por_Energia.png", dpi=300, bbox_inches="tight")

plt.show()

