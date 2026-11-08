
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.patches import Rectangle
from matplotlib.colors import Normalize
from pathlib import Path


# ============================================================
# 1. CONFIGURAÇÕES MANUAIS
# ============================================================

ARQUIVO_CELULAS = "Padroes_Espaciais_2km.txt"
ARQUIVO_POSICOES = "Posicoes_Antenas.txt"

# Tamanho das células em metros
TAMANHO_CELULA = 2000

# Unidade dos eixos
DIVISOR_COORDENADAS = 1000
UNIDADE_COORDENADAS = "km"

# Tamanho das figuras
TAMANHO_FIGURA = (10, 8)

# Resolução das imagens
DPI = 300

# Salvar imagens?
SALVAR_IMAGENS = True

PASTA_SAIDA = "Mapas_Espaciais"

# Colormap de cada mapa
MAPAS = {
    "Densidade": "viridis",
    "Media_CH0": "plasma",
    "Media_CH1": "plasma",
    "N_Atipicas": "Reds",
    "Proporcao_Atipicas": "magma"
}


# ============================================================
# 2. LEITURA DOS ARQUIVOS
# ============================================================

try:
    celulas = pd.read_csv(
        ARQUIVO_CELULAS,
        sep=r"\s+",
        na_values=["NA", "NaN", "nan"]
    )

    posicoes = pd.read_csv(
        ARQUIVO_POSICOES,
        sep=r"\s+",
        na_values=["NA", "NaN", "nan"]
    )

except FileNotFoundError as erro:
    raise SystemExit(
        f"Arquivo não encontrado: {erro.filename}"
    )


# ============================================================
# 3. CONFERÊNCIA DAS COLUNAS
# ============================================================

colunas_celulas = [
    "Easting_Inicial",
    "Northing_Inicial",
    "Easting_Centro",
    "Northing_Centro",
    "N_Antenas",
    "Densidade_ant_km2",
    "Media_CH0",
    "Media_CH1",
    "N_Atipicas",
    "N_Atencao"
]

for coluna in colunas_celulas:

    if coluna not in celulas.columns:
        raise SystemExit(
            f"Coluna '{coluna}' não encontrada em {ARQUIVO_CELULAS}."
        )


colunas_posicoes = ["ID", "Northing", "Easting", "inGrid"]

for coluna in colunas_posicoes:

    if coluna not in posicoes.columns:
        raise SystemExit(
            f"Coluna '{coluna}' não encontrada em {ARQUIVO_POSICOES}."
        )


# ============================================================
# 4. CONVERSÃO DOS DADOS NUMÉRICOS
# ============================================================

for coluna in colunas_celulas:
    celulas[coluna] = pd.to_numeric(
        celulas[coluna],
        errors="coerce"
    )

for coluna in ["ID", "Northing", "Easting", "inGrid"]:
    posicoes[coluna] = pd.to_numeric(
        posicoes[coluna],
        errors="coerce"
    )

celulas = celulas.dropna(
    subset=["Easting_Inicial", "Northing_Inicial"]
)

posicoes = posicoes.dropna(
    subset=["Easting", "Northing", "inGrid"]
)


# ============================================================
# 5. PREPARAÇÃO DA PASTA DE SAÍDA
# ============================================================

if SALVAR_IMAGENS:
    Path(PASTA_SAIDA).mkdir(
        parents=True,
        exist_ok=True
    )


# ============================================================
# 6. FUNÇÃO PARA GERAR MAPAS ESPACIAIS
# ============================================================

def gerar_mapa(coluna, titulo, nome_arquivo, legenda, cmap):

    fig, ax = plt.subplots(figsize=TAMANHO_FIGURA)

    valores = celulas[coluna].to_numpy(dtype=float)

    # Considerar somente valores válidos
    validos = np.isfinite(valores)

    if not np.any(validos):
        print(f"Sem dados válidos para {coluna}.")
        plt.close(fig)
        return

    minimo = np.min(valores[validos])
    maximo = np.max(valores[validos])

    if minimo == maximo:
        maximo = minimo + 1

    normalizacao = Normalize(
        vmin=minimo,
        vmax=maximo
    )

    mapa_cores = plt.get_cmap(cmap)

    # Desenhar cada célula como um quadrado de 2 km
    for _, linha in celulas.iterrows():

        valor = linha[coluna]

        if pd.isna(valor):
            continue

        cor = mapa_cores(
            normalizacao(valor)
        )

        quadrado = Rectangle(
            (
                linha["Easting_Inicial"] / DIVISOR_COORDENADAS,
                linha["Northing_Inicial"] / DIVISOR_COORDENADAS
            ),
            TAMANHO_CELULA / DIVISOR_COORDENADAS,
            TAMANHO_CELULA / DIVISOR_COORDENADAS,
            facecolor=cor,
            edgecolor="black",
            linewidth=0.3
        )

        ax.add_patch(quadrado)

    # Barra de cores
    mapeamento = plt.cm.ScalarMappable(
        norm=normalizacao,
        cmap=mapa_cores
    )

    mapeamento.set_array([])

    barra = fig.colorbar(
        mapeamento,
        ax=ax
    )

    barra.set_label(
        legenda,
        fontsize=11
    )

    # Formatação
    ax.set_title(
        titulo,
        fontsize=15
    )

    ax.set_xlabel(
        f"Easting ({UNIDADE_COORDENADAS})",
        fontsize=12
    )

    ax.set_ylabel(
        f"Northing ({UNIDADE_COORDENADAS})",
        fontsize=12
    )

    ax.set_aspect("equal")

        # Ajustar os limites dos eixos às coordenadas das células

    x_min = celulas["Easting_Inicial"].min() / DIVISOR_COORDENADAS
    x_max = (
        celulas["Easting_Inicial"].max() + TAMANHO_CELULA
    ) / DIVISOR_COORDENADAS

    y_min = celulas["Northing_Inicial"].min() / DIVISOR_COORDENADAS
    y_max = (
        celulas["Northing_Inicial"].max() + TAMANHO_CELULA
    ) / DIVISOR_COORDENADAS

    margem = 0.5

    ax.set_xlim(x_min - margem, x_max + margem)
    ax.set_ylim(y_min - margem, y_max + margem)

    ax.set_aspect("equal")

    ax.grid(
        True,
        linestyle="--",
        alpha=0.3
    )

    plt.tight_layout()

    # Salvar
    if SALVAR_IMAGENS:

        caminho = Path(PASTA_SAIDA) / nome_arquivo

        plt.savefig(
            caminho,
            dpi=DPI,
            bbox_inches="tight"
        )

        print(f"Mapa salvo: {caminho.resolve()}")

    plt.show()


# ============================================================
# 7. MAPA 1: DENSIDADE DE ANTENAS
# ============================================================

gerar_mapa(
    coluna="Densidade_ant_km2",
    titulo="Distribuição Espacial da Densidade de Antenas",
    nome_arquivo="Mapa_Densidade.png",
    legenda="Antenas por km²",
    cmap=MAPAS["Densidade"]
)


# ============================================================
# 8. MAPA 2: POTÊNCIA MÉDIA CH0
# ============================================================

gerar_mapa(
    coluna="Media_CH0",
    titulo="Distribuição Espacial da Potência Média - CH0",
    nome_arquivo="Mapa_Potencia_CH0.png",
    legenda="Potência média CH0",
    cmap=MAPAS["Media_CH0"]
)


# ============================================================
# 9. MAPA 3: POTÊNCIA MÉDIA CH1
# ============================================================

gerar_mapa(
    coluna="Media_CH1",
    titulo="Distribuição Espacial da Potência Média - CH1",
    nome_arquivo="Mapa_Potencia_CH1.png",
    legenda="Potência média CH1",
    cmap=MAPAS["Media_CH1"]
)


# ============================================================
# 10. MAPA 4: NÚMERO DE ANTENAS ATÍPICAS
# ============================================================

gerar_mapa(
    coluna="N_Atipicas",
    titulo="Distribuição Espacial de Antenas Atípicas",
    nome_arquivo="Mapa_Antenas_Atipicas.png",
    legenda="Número de antenas atípicas",
    cmap=MAPAS["N_Atipicas"]
)


# ============================================================
# 11. MAPA 5: PROPORÇÃO DE ANTENAS ATÍPICAS
# ============================================================

# Evitar divisão por zero
celulas["Proporcao_Atipicas"] = np.where(
    celulas["N_Antenas"] > 0,
    celulas["N_Atipicas"] / celulas["N_Antenas"],
    np.nan
)

gerar_mapa(
    coluna="Proporcao_Atipicas",
    titulo="Proporção de Antenas Atípicas por Região",
    nome_arquivo="Mapa_Proporcao_Atipicas.png",
    legenda="Fração de antenas atípicas",
    cmap=MAPAS["Proporcao_Atipicas"]
)


# ============================================================
# 12. MAPA 6: POSIÇÃO DAS ANTENAS POR CONFIGURAÇÃO
# ============================================================

fig, ax = plt.subplots(figsize=TAMANHO_FIGURA)

cores = {
    1: "blue",
    2: "orange",
    3: "green",
    12: "red",
    23: "purple",
    123: "brown"
}

for grupo, cor in cores.items():

    subconjunto = posicoes[
        posicoes["inGrid"] == grupo
    ]

    if subconjunto.empty:
        continue

    ax.scatter(
        subconjunto["Easting"] / DIVISOR_COORDENADAS,
        subconjunto["Northing"] / DIVISOR_COORDENADAS,
        color=cor,
        s=12,
        alpha=0.75,
        label=f"inGrid {grupo} (N={len(subconjunto)})"
    )


ax.set_title(
    "Distribuição Espacial das Antenas por Configuração",
    fontsize=15
)

ax.set_xlabel(
    f"Easting ({UNIDADE_COORDENADAS})"
)

ax.set_ylabel(
    f"Northing ({UNIDADE_COORDENADAS})"
)

ax.set_aspect("equal")
ax.grid(True, linestyle="--", alpha=0.3)
ax.legend(fontsize=9)

plt.tight_layout()

if SALVAR_IMAGENS:

    caminho = Path(PASTA_SAIDA) / "Mapa_Configuracoes.png"

    plt.savefig(
        caminho,
        dpi=DPI,
        bbox_inches="tight"
    )

    print(f"Mapa salvo: {caminho.resolve()}")

plt.show()


# ============================================================
# 13. RESUMO
# ============================================================

print("\n========== ANÁLISE ESPACIAL ==========")

print("Número de células:", len(celulas))

print(
    "Número de antenas:",
    posicoes["ID"].nunique()
)

print(
    "Total de antenas atípicas:",
    int(celulas["N_Atipicas"].sum())
)

print(
    "Total de antenas em atenção:",
    int(celulas["N_Atencao"].sum())
)

print("\nAnálise concluída!")

