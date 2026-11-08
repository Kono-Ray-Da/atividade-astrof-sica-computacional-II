
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ==========================================================
# 1. CONFIGURAÇÕES MANUAIS
# ==========================================================

ARQUIVO = "Estatisticas_Individuais.txt"

PASTA_SAIDA = Path("Graficos_Configuracoes")
PASTA_SAIDA.mkdir(exist_ok=True)

# Ordem das configurações
GRUPOS = [1, 2, 3, 12, 23, 123]

# Tamanho dos bins dos histogramas
# Altere esses valores conforme necessário.
BIN_CH0 = 100
BIN_CH1 = 100

# Mostrar valores extremos nos boxplots?
MOSTRAR_OUTLIERS = True

# Barras de erro:
# "std" = desvio padrão entre antenas
# "sem" = erro padrão da média
TIPO_ERRO = "std"

# Aparência
TAMANHO_FIGURA = (11, 7)
DPI = 300

# Salvar imagens?
SALVAR = True

# ==========================================================
# 2. LEITURA DOS DADOS
# ==========================================================

try:
    dados = pd.read_csv(
        ARQUIVO,
        sep=r"\s+",
        comment="#"
    )

except FileNotFoundError:
    raise SystemExit(f"Arquivo não encontrado: {ARQUIVO}")


# Verificar colunas esperadas
colunas = [
    "ID",
    "inGrid",
    "Media_CH0",
    "Desvio_CH0",
    "Media_CH1",
    "Desvio_CH1",
    "N_CH0",
    "N_CH1"
]

for coluna in colunas:
    if coluna not in dados.columns:
        raise SystemExit(
            f"Coluna '{coluna}' não encontrada. "
            f"Colunas disponíveis: {dados.columns.tolist()}"
        )


# Converter valores numéricos
for coluna in colunas:
    dados[coluna] = pd.to_numeric(
        dados[coluna],
        errors="coerce"
    )

# Remover linhas sem identificação ou configuração
dados = dados.dropna(subset=["ID", "inGrid"])

# Selecionar somente as configurações desejadas
dados = dados[dados["inGrid"].isin(GRUPOS)].copy()

# Ordenar configurações
dados["inGrid"] = pd.Categorical(
    dados["inGrid"],
    categories=GRUPOS,
    ordered=True
)

# ==========================================================
# 3. PREPARAÇÃO DOS DADOS
# ==========================================================

# Cada canal será analisado separadamente.
# Valores ausentes não serão substituídos por zero.

grupos_ch0 = [
    dados.loc[
        dados["inGrid"] == grupo,
        "Media_CH0"
    ].dropna().values
    for grupo in GRUPOS
]

grupos_ch1 = [
    dados.loc[
        dados["inGrid"] == grupo,
        "Media_CH1"
    ].dropna().values
    for grupo in GRUPOS
]

desvios_ch0 = [
    dados.loc[
        dados["inGrid"] == grupo,
        "Desvio_CH0"
    ].dropna().values
    for grupo in GRUPOS
]

desvios_ch1 = [
    dados.loc[
        dados["inGrid"] == grupo,
        "Desvio_CH1"
    ].dropna().values
    for grupo in GRUPOS
]

rotulos = [str(g) for g in GRUPOS]


def salvar_figura(nome):
    """Salva a figura na pasta de saída."""
    if SALVAR:
        caminho = PASTA_SAIDA / nome
        plt.savefig(
            caminho,
            dpi=DPI,
            bbox_inches="tight"
        )
        print(f"Salvo: {caminho.resolve()}")


# ==========================================================
# 4. BOXPLOTS DE POTÊNCIA POR CONFIGURAÇÃO
# ==========================================================

fig, eixos = plt.subplots(1, 2, figsize=(15, 6))

eixos[0].boxplot(
    grupos_ch0,
    tick_labels=rotulos,
    showfliers=MOSTRAR_OUTLIERS
)
eixos[0].set_title("Potência média - CH0")
eixos[0].set_xlabel("Configuração inGrid")
eixos[0].set_ylabel("Potência média")
eixos[0].grid(axis="y", alpha=0.3)

eixos[1].boxplot(
    grupos_ch1,
    tick_labels=rotulos,
    showfliers=MOSTRAR_OUTLIERS
)
eixos[1].set_title("Potência média - CH1")
eixos[1].set_xlabel("Configuração inGrid")
eixos[1].set_ylabel("Potência média")
eixos[1].grid(axis="y", alpha=0.3)

fig.suptitle("Boxplots de potência por configuração", fontsize=15)
plt.tight_layout()
salvar_figura("01_Boxplots_Potencia.png")
plt.show()


# ==========================================================
# 5. VIOLIN PLOTS
# ==========================================================

fig, eixos = plt.subplots(1, 2, figsize=(15, 6))

eixos[0].violinplot(
    grupos_ch0,
    showmeans=True,
    showmedians=True,
    showextrema=True
)
eixos[0].set_xticks(
    range(1, len(GRUPOS) + 1),
    rotulos
)
eixos[0].set_title("Distribuição da potência - CH0")
eixos[0].set_xlabel("Configuração inGrid")
eixos[0].set_ylabel("Potência média")
eixos[0].grid(axis="y", alpha=0.3)

eixos[1].violinplot(
    grupos_ch1,
    showmeans=True,
    showmedians=True,
    showextrema=True
)
eixos[1].set_xticks(
    range(1, len(GRUPOS) + 1),
    rotulos
)
eixos[1].set_title("Distribuição da potência - CH1")
eixos[1].set_xlabel("Configuração inGrid")
eixos[1].set_ylabel("Potência média")
eixos[1].grid(axis="y", alpha=0.3)

fig.suptitle("Violin plots por configuração", fontsize=15)
plt.tight_layout()
salvar_figura("02_Violin_Plots.png")
plt.show()


# ==========================================================
# 6. GRÁFICOS DE BARRAS COM MÉDIAS E BARRAS DE ERRO
# ==========================================================

def calcular_media_erro(valores):

    valores = np.asarray(valores, dtype=float)
    valores = valores[np.isfinite(valores)]

    n = len(valores)

    if n == 0:
        return np.nan, np.nan

    media = np.mean(valores)

    if n < 2:
        return media, np.nan

    desvio = np.std(valores, ddof=1)

    if TIPO_ERRO == "std":
        erro = desvio

    elif TIPO_ERRO == "sem":
        erro = desvio / np.sqrt(n)

    else:
        raise ValueError(
            "TIPO_ERRO deve ser 'std' ou 'sem'."
        )

    return media, erro


medias0, erros0 = zip(*[
    calcular_media_erro(g) for g in grupos_ch0
])

medias1, erros1 = zip(*[
    calcular_media_erro(g) for g in grupos_ch1
])

posicoes = np.arange(len(GRUPOS))
largura = 0.35

fig, ax = plt.subplots(figsize=(12, 6))

ax.bar(
    posicoes - largura / 2,
    medias0,
    largura,
    yerr=erros0,
    capsize=5,
    label="CH0"
)

ax.bar(
    posicoes + largura / 2,
    medias1,
    largura,
    yerr=erros1,
    capsize=5,
    label="CH1"
)

ax.set_xticks(posicoes)
ax.set_xticklabels(rotulos)
ax.set_xlabel("Configuração inGrid")
ax.set_ylabel("Potência média")
ax.set_title(
    f"Média de potência por configuração "
    f"(barras de erro: {TIPO_ERRO.upper()})"
)

ax.legend()
ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
salvar_figura("03_Medias_Barras_Erro.png")
plt.show()


# ==========================================================
# 7. HISTOGRAMAS SEPARADOS POR CONFIGURAÇÃO
# ==========================================================

def criar_bins(valores, tamanho):

    valores = np.asarray(valores, dtype=float)
    valores = valores[np.isfinite(valores)]

    if len(valores) == 0:
        return None

    minimo = np.floor(valores.min() / tamanho) * tamanho
    maximo = np.ceil(valores.max() / tamanho) * tamanho

    if minimo == maximo:
        maximo = minimo + tamanho

    return np.arange(
        minimo,
        maximo + tamanho,
        tamanho
    )


def gerar_histogramas(grupos, canal, tamanho_bin):

    fig, eixos = plt.subplots(
        3, 2,
        figsize=(13, 12)
    )

    eixos = eixos.flatten()

    for i, grupo in enumerate(GRUPOS):

        ax = eixos[i]
        valores = grupos[i]

        if len(valores) == 0:
            ax.set_title(f"inGrid {grupo} - sem dados")
            continue

        bins = criar_bins(valores, tamanho_bin)

        ax.hist(
            valores,
            bins=bins,
            edgecolor="black",
            alpha=0.8
        )

        ax.axvline(
            np.mean(valores),
            color="red",
            linestyle="--",
            label=f"Média = {np.mean(valores):.2f}"
        )

        ax.axvline(
            np.median(valores),
            color="green",
            linestyle=":",
            label=f"Mediana = {np.median(valores):.2f}"
        )

        ax.set_title(
            f"inGrid {grupo} (N={len(valores)})"
        )

        ax.set_xlabel("Potência média")
        ax.set_ylabel("Número de antenas")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.25)

    fig.suptitle(
        f"Distribuição das potências por configuração - {canal}",
        fontsize=15
    )

    plt.tight_layout()

    salvar_figura(f"04_Histogramas_{canal}.png")
    plt.show()


gerar_histogramas(
    grupos_ch0,
    "CH0",
    BIN_CH0
)

gerar_histogramas(
    grupos_ch1,
    "CH1",
    BIN_CH1
)


# ==========================================================
# 8. COMPARAÇÃO ENTRE CH0 E CH1 EM CADA CONFIGURAÇÃO
# ==========================================================

fig, eixos = plt.subplots(3, 2, figsize=(13, 13))
eixos = eixos.flatten()

for i, grupo in enumerate(GRUPOS):

    ax = eixos[i]

    subconjunto = dados[
        dados["inGrid"] == grupo
    ]

    valores0 = subconjunto["Media_CH0"].dropna().values
    valores1 = subconjunto["Media_CH1"].dropna().values

    ax.boxplot(
        [valores0, valores1],
        tick_labels=["CH0", "CH1"],
        showfliers=MOSTRAR_OUTLIERS
    )

    ax.set_title(
        f"inGrid {grupo} "
        f"(CH0: {len(valores0)}, CH1: {len(valores1)})"
    )

    ax.set_ylabel("Potência média")
    ax.grid(axis="y", alpha=0.3)

fig.suptitle(
    "Comparação entre CH0 e CH1 em cada configuração",
    fontsize=15
)

plt.tight_layout()
salvar_figura("05_Comparacao_CH0_CH1_Grupos.png")
plt.show()


# ==========================================================
# 9. BOXPLOTS DOS DESVIOS-PADRÃO INDIVIDUAIS
# ==========================================================

fig, eixos = plt.subplots(1, 2, figsize=(15, 6))

eixos[0].boxplot(
    desvios_ch0,
    tick_labels=rotulos,
    showfliers=MOSTRAR_OUTLIERS
)
eixos[0].set_title("Desvio padrão individual - CH0")
eixos[0].set_xlabel("Configuração inGrid")
eixos[0].set_ylabel("Desvio padrão")
eixos[0].grid(axis="y", alpha=0.3)

eixos[1].boxplot(
    desvios_ch1,
    tick_labels=rotulos,
    showfliers=MOSTRAR_OUTLIERS
)
eixos[1].set_title("Desvio padrão individual - CH1")
eixos[1].set_xlabel("Configuração inGrid")
eixos[1].set_ylabel("Desvio padrão")
eixos[1].grid(axis="y", alpha=0.3)

fig.suptitle(
    "Comparação da variabilidade entre antenas",
    fontsize=15
)

plt.tight_layout()
salvar_figura("06_Boxplots_Desvios_Padrao.png")
plt.show()


# ==========================================================
# 10. RESUMO NUMÉRICO
# ==========================================================

print("\n========== RESUMO POR CONFIGURAÇÃO ==========")

for grupo in GRUPOS:

    subconjunto = dados[
        dados["inGrid"] == grupo
    ]

    valores0 = subconjunto["Media_CH0"].dropna()
    valores1 = subconjunto["Media_CH1"].dropna()

    print(f"\ninGrid {grupo}")
    print(f"Antenas com CH0 válido: {len(valores0)}")
    print(f"Antenas com CH1 válido: {len(valores1)}")

    if len(valores0) > 0:
        print(
            f"CH0: média = {valores0.mean():.3f}, "
            f"mediana = {valores0.median():.3f}, "
            f"desvio = {valores0.std():.3f}"
        )

    if len(valores1) > 0:
        print(
            f"CH1: média = {valores1.mean():.3f}, "
            f"mediana = {valores1.median():.3f}, "
            f"desvio = {valores1.std():.3f}"
        )

print("\nAnálise concluída!")
print("Imagens salvas em:", PASTA_SAIDA.resolve())

