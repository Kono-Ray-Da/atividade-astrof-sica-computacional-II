
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# CONFIGURAÇÕES
# ============================================================

ARQUIVO_ANOMALIAS = "Antenas_Atipicas.txt"
ARQUIVO_POSICOES = "Posicoes_Antenas.txt"

PASTA_SAIDA = Path("Graficos_Anomalias")
PASTA_SAIDA.mkdir(exist_ok=True)

# Mostrar ou não as antenas com amostra pequena no mapa
MOSTRAR_AMOSTRA_PEQUENA = True

# ============================================================
# 1. LEITURA DOS ARQUIVOS
# ============================================================

anomalias = pd.read_csv(
    ARQUIVO_ANOMALIAS,
    sep=r"\s+",
    comment="#"
)

posicoes = pd.read_csv(
    ARQUIVO_POSICOES,
    sep=r"\s+",
    comment="#"
)

# Junta as informações de anomalias com as coordenadas
dados = pd.merge(
    anomalias,
    posicoes,
    on="ID",
    how="left"
)

# Verifica se todas as antenas possuem coordenadas
sem_posicao = dados["Easting"].isna().sum()

if sem_posicao > 0:
    print(f"Atenção: {sem_posicao} antenas não possuem posição.")

print("\nQuantidade de antenas por classificação:")
print(dados["Classificacao"].value_counts())

# ============================================================
# 2. QUANTIDADE DE ANTENAS POR CLASSIFICAÇÃO
# ============================================================

ordem = ["NORMAL", "ATENCAO", "ATIPICA", "AMOSTRA_PEQUENA"]

contagem = (
    dados["Classificacao"]
    .value_counts()
    .reindex(ordem, fill_value=0)
)

plt.figure(figsize=(9, 6))

barras = plt.bar(
    contagem.index,
    contagem.values
)

plt.title("Quantidade de antenas por classificação")
plt.xlabel("Classificação")
plt.ylabel("Número de antenas")
plt.grid(axis="y", alpha=0.3)

for barra in barras:
    altura = barra.get_height()
    plt.text(
        barra.get_x() + barra.get_width() / 2,
        altura,
        f"{int(altura)}",
        ha="center",
        va="bottom"
    )

plt.tight_layout()
plt.savefig(
    PASTA_SAIDA / "01_Quantidade_Classificacoes.png",
    dpi=300
)
plt.show()

# ============================================================
# 3. MAPA ESPACIAL DAS ANOMALIAS
# ============================================================

cores = {
    "NORMAL": "gray",
    "ATENCAO": "orange",
    "ATIPICA": "red",
    "AMOSTRA_PEQUENA": "blue"
}

marcadores = {
    "NORMAL": ".",
    "ATENCAO": "o",
    "ATIPICA": "*",
    "AMOSTRA_PEQUENA": "s"
}

plt.figure(figsize=(11, 9))

for classificacao in ordem:

    if classificacao == "AMOSTRA_PEQUENA" and not MOSTRAR_AMOSTRA_PEQUENA:
        continue

    subconjunto = dados[
        (dados["Classificacao"] == classificacao)
        & dados["Easting"].notna()
        & dados["Northing"].notna()
    ]

    if len(subconjunto) == 0:
        continue

    plt.scatter(
        subconjunto["Easting"] / 1000,
        subconjunto["Northing"] / 1000,
        c=cores[classificacao],
        marker=marcadores[classificacao],
        label=classificacao,
        s=35 if classificacao != "NORMAL" else 12,
        alpha=0.8
    )

plt.title("Distribuição espacial das classificações das antenas")
plt.xlabel("Easting (km)")
plt.ylabel("Northing (km)")
plt.legend()
plt.grid(alpha=0.3)
plt.axis("equal")
plt.tight_layout()

plt.savefig(
    PASTA_SAIDA / "02_Mapa_Espacial_Anomalias.png",
    dpi=300
)
plt.show()

# ============================================================
# 4. DISTRIBUIÇÃO DOS ESCORES-Z
# ============================================================

variaveis = [
    ("Z_Media_CH0", "Média CH0"),
    ("Z_Desvio_CH0", "Desvio-padrão CH0"),
    ("Z_Media_CH1", "Média CH1"),
    ("Z_Desvio_CH1", "Desvio-padrão CH1")
]

fig, eixos = plt.subplots(2, 2, figsize=(13, 9))
eixos = eixos.flatten()

for i, (coluna, titulo) in enumerate(variaveis):

    ax = eixos[i]

    for classificacao in ordem:

        subconjunto = dados[
            dados["Classificacao"] == classificacao
        ][coluna].dropna()

        if len(subconjunto) == 0:
            continue

        ax.hist(
            subconjunto,
            bins=30,
            alpha=0.55,
            label=classificacao
        )

    ax.axvline(2, color="orange", linestyle="--", alpha=0.8)
    ax.axvline(-2, color="orange", linestyle="--", alpha=0.8)
    ax.axvline(3, color="red", linestyle=":", alpha=0.8)
    ax.axvline(-3, color="red", linestyle=":", alpha=0.8)
    ax.axvline(0, color="black", linewidth=1)

    ax.set_title(titulo)
    ax.set_xlabel("Escore-z")
    ax.set_ylabel("Número de antenas")
    ax.grid(alpha=0.2)

eixos[0].legend(fontsize=8)

fig.suptitle("Distribuição dos escores-z por grandeza", fontsize=15)
plt.tight_layout()

plt.savefig(
    PASTA_SAIDA / "03_Distribuicao_EscoresZ.png",
    dpi=300
)
plt.show()

# ============================================================
# 5. MAPA DE CALOR DOS ESCORES-Z
# ============================================================

colunas_z = [
    "Z_Media_CH0",
    "Z_Desvio_CH0",
    "Z_Media_CH1",
    "Z_Desvio_CH1"
]

# Considera somente antenas classificadas como ATENCAO ou ATIPICA
selecionadas = dados[
    dados["Classificacao"].isin(["ATENCAO", "ATIPICA"])
].copy()

# Ordena pela maior magnitude de escore-z
selecionadas["Maior_abs_Z"] = (
    selecionadas[colunas_z].abs().max(axis=1)
)

selecionadas = selecionadas.sort_values(
    "Maior_abs_Z",
    ascending=False
)

if len(selecionadas) > 0:

    matriz = selecionadas.set_index("ID")[colunas_z]

    altura = max(5, len(matriz) * 0.25)

    fig, ax = plt.subplots(figsize=(10, altura))

    imagem = ax.imshow(
        matriz,
        aspect="auto",
        cmap="coolwarm",
        vmin=-3,
        vmax=3
    )

    ax.set_xticks(range(len(colunas_z)))
    ax.set_xticklabels(
        ["Média CH0", "Desvio CH0", "Média CH1", "Desvio CH1"],
        rotation=25,
        ha="right"
    )

    ax.set_yticks(range(len(matriz)))
    ax.set_yticklabels(matriz.index)

    ax.set_title("Escores-z das antenas classificadas como ATENCAO ou ATIPICA")
    ax.set_ylabel("ID da antena")

    barra = plt.colorbar(imagem, ax=ax)
    barra.set_label("Escore-z")

    plt.tight_layout()

    plt.savefig(
        PASTA_SAIDA / "04_Mapa_Calor_EscoresZ.png",
        dpi=300
    )
    plt.show()

else:
    print("Não há antenas ATENCAO ou ATIPICA para o mapa de calor.")

print("\nGráficos salvos em:", PASTA_SAIDA.resolve())

