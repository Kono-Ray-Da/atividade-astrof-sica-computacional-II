
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# 1. CONFIGURAÇÕES MANUAIS
# ============================================================

ARQUIVO_ESPECTRAL = "Perfil_Espectral.txt"
ARQUIVO_POSICOES = "Posicoes_Antenas.txt"

# Intervalo de frequência
FREQ_MIN = None
FREQ_MAX = None

# Canais
MOSTRAR_CH0 = True
MOSTRAR_CH1 = True

# Mostrar desvio padrão
MOSTRAR_DESVIO = True

# No gráfico comparativo, as sombras podem deixar
# a visualização poluída. Você pode desativá-las.
DESVIO_COMPARACAO = False

# Aparência
TAMANHO_FIGURA = (12, 6)
ESPESSURA_LINHA = 2
TRANSPARENCIA = 0.15
DPI = 300

# Salvar imagens
SALVAR_IMAGENS = True

IMAGEM_INGRID1 = "Perfil_Espectral_inGrid_1.png"
IMAGEM_COMPARACAO = "Comparacao_Perfil_Espectral_Grupos.png"

# Configurações que serão comparadas
GRUPOS = [1, 2, 3, 12, 23, 123]


# ============================================================
# 2. LEITURA DOS ARQUIVOS
# ============================================================

try:
    espectral = pd.read_csv(
        ARQUIVO_ESPECTRAL,
        sep=r"\s+",
        na_values=["NA", "NaN", "nan"]
    )

    posicoes = pd.read_csv(
        ARQUIVO_POSICOES,
        sep=r"\s+",
        na_values=["NA", "NaN", "nan"]
    )

except FileNotFoundError as erro:
    raise SystemExit(f"Arquivo não encontrado: {erro.filename}")


# Converter identificações para números inteiros
espectral["Antena"] = pd.to_numeric(
    espectral["Antena"], errors="coerce"
)

posicoes["ID"] = pd.to_numeric(
    posicoes["ID"], errors="coerce"
)

espectral = espectral.dropna(subset=["Antena"])
posicoes = posicoes.dropna(subset=["ID"])

espectral["Antena"] = espectral["Antena"].astype(int)
posicoes["ID"] = posicoes["ID"].astype(int)

# Verificar colunas
colunas_espectrais = [
    "Antena",
    "Frequencia",
    "Media_CH0",
    "Media_CH1"
]

colunas_posicoes = ["ID", "inGrid"]

for coluna in colunas_espectrais:
    if coluna not in espectral.columns:
        raise SystemExit(
            f"Coluna {coluna} não encontrada no arquivo espectral."
        )

for coluna in colunas_posicoes:
    if coluna not in posicoes.columns:
        raise SystemExit(
            f"Coluna {coluna} não encontrada no arquivo de posições."
        )


# ============================================================
# 3. ASSOCIAR CADA ANTENA À SUA CONFIGURAÇÃO
# ============================================================

dados = pd.merge(
    espectral,
    posicoes[["ID", "inGrid"]],
    left_on="Antena",
    right_on="ID",
    how="inner"
)

if dados.empty:
    raise SystemExit(
        "Não foi possível associar as antenas dos dois arquivos."
    )

# Converter colunas numéricas
colunas_numericas = [
    "Frequencia",
    "Media_CH0",
    "Media_CH1"
]

for coluna in colunas_numericas:
    dados[coluna] = pd.to_numeric(
        dados[coluna], errors="coerce"
    )

# Eliminar registros sem frequência
dados = dados.dropna(subset=["Frequencia"])


# ============================================================
# 4. SELEÇÃO DO INTERVALO DE FREQUÊNCIA
# ============================================================

if FREQ_MIN is not None:
    dados = dados[dados["Frequencia"] >= FREQ_MIN]

if FREQ_MAX is not None:
    dados = dados[dados["Frequencia"] <= FREQ_MAX]

if dados.empty:
    raise SystemExit("Não existem dados no intervalo selecionado.")


# ============================================================
# 5. FUNÇÃO PARA CALCULAR O PERFIL ESPECTRAL
# ============================================================

def calcular_perfil(subconjunto):

    perfil = subconjunto.groupby("Frequencia").agg(
        Media_CH0=("Media_CH0", "mean"),
        Desvio_CH0=("Media_CH0", "std"),
        N_CH0=("Media_CH0", "count"),

        Media_CH1=("Media_CH1", "mean"),
        Desvio_CH1=("Media_CH1", "std"),
        N_CH1=("Media_CH1", "count")

    ).reset_index()

    return perfil.sort_values("Frequencia")


# ============================================================
# 6. GRÁFICO 1: SOMENTE INGRID 1
# ============================================================

dados_grupo1 = dados[dados["inGrid"] == 1]

if dados_grupo1.empty:
    raise SystemExit("Não foram encontrados dados para inGrid 1.")

perfil1 = calcular_perfil(dados_grupo1)

numero_antenas1 = dados_grupo1["Antena"].nunique()

fig, ax = plt.subplots(figsize=TAMANHO_FIGURA)

frequencia = perfil1["Frequencia"]


# CH0
if MOSTRAR_CH0:

    media0 = perfil1["Media_CH0"]
    desvio0 = perfil1["Desvio_CH0"].fillna(0)

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
            alpha=TRANSPARENCIA
        )


# CH1
if MOSTRAR_CH1:

    media1 = perfil1["Media_CH1"]
    desvio1 = perfil1["Desvio_CH1"].fillna(0)

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
            alpha=TRANSPARENCIA
        )


ax.set_title(
    f"Perfil Espectral Médio - inGrid 1 ({numero_antenas1} antenas)",
    fontsize=14
)

ax.set_xlabel("Frequência", fontsize=12)
ax.set_ylabel("Potência média", fontsize=12)

ax.grid(True, linestyle="--", alpha=0.4)
ax.legend()
plt.tight_layout()

if SALVAR_IMAGENS:
    plt.savefig(
        IMAGEM_INGRID1,
        dpi=DPI,
        bbox_inches="tight"
    )

plt.show()


# ============================================================
# 7. GRÁFICO 2: COMPARAÇÃO ENTRE CONFIGURAÇÕES
# ============================================================

fig, (ax0, ax1) = plt.subplots(
    2, 1,
    figsize=(12, 10),
    sharex=True
)

# Dicionário para armazenar os perfis
perfis = {}

for grupo in GRUPOS:

    subconjunto = dados[dados["inGrid"] == grupo]

    if subconjunto.empty:
        print(f"Aviso: grupo {grupo} sem dados.")
        continue

    perfil = calcular_perfil(subconjunto)

    perfis[grupo] = perfil

    numero_antenas = subconjunto["Antena"].nunique()

    frequencia = perfil["Frequencia"]

    print(
        f"inGrid {grupo}: {numero_antenas} antenas"
    )

    # -------------------------
    # CH0
    # -------------------------

    if MOSTRAR_CH0:

        media0 = perfil["Media_CH0"]
        desvio0 = perfil["Desvio_CH0"].fillna(0)

        linha0, = ax0.plot(
            frequencia,
            media0,
            linewidth=ESPESSURA_LINHA,
            label=f"inGrid {grupo} (N={numero_antenas})"
        )

        if DESVIO_COMPARACAO and MOSTRAR_DESVIO:
            ax0.fill_between(
                frequencia,
                media0 - desvio0,
                media0 + desvio0,
                alpha=TRANSPARENCIA,
                color=linha0.get_color()
            )

    # -------------------------
    # CH1
    # -------------------------

    if MOSTRAR_CH1:

        media1 = perfil["Media_CH1"]
        desvio1 = perfil["Desvio_CH1"].fillna(0)

        linha1, = ax1.plot(
            frequencia,
            media1,
            linewidth=ESPESSURA_LINHA,
            label=f"inGrid {grupo} (N={numero_antenas})"
        )

        if DESVIO_COMPARACAO and MOSTRAR_DESVIO:
            ax1.fill_between(
                frequencia,
                media1 - desvio1,
                media1 + desvio1,
                alpha=TRANSPARENCIA,
                color=linha1.get_color()
            )


# Formatação CH0
ax0.set_title("Comparação dos Perfis Espectrais - CH0")
ax0.set_ylabel("Potência média")
ax0.grid(True, linestyle="--", alpha=0.4)

if MOSTRAR_CH0:
    ax0.legend(fontsize=9)


# Formatação CH1
ax1.set_title("Comparação dos Perfis Espectrais - CH1")
ax1.set_xlabel("Frequência")
ax1.set_ylabel("Potência média")
ax1.grid(True, linestyle="--", alpha=0.4)

if MOSTRAR_CH1:
    ax1.legend(fontsize=9)


fig.suptitle(
    "Comparação entre Configurações de Malha",
    fontsize=15
)

plt.tight_layout()

if SALVAR_IMAGENS:
    plt.savefig(
        IMAGEM_COMPARACAO,
        dpi=DPI,
        bbox_inches="tight"
    )

plt.show()


# ============================================================
# 8. RESUMO
# ============================================================

print("\n========== RESUMO ==========")

print(
    "Antenas utilizadas:",
    dados["Antena"].nunique()
)

print(
    "Antenas inGrid 1:",
    dados_grupo1["Antena"].nunique()
)

print("\nQuantidade de antenas por configuração:")

for grupo in GRUPOS:
    quantidade = dados.loc[
        dados["inGrid"] == grupo, "Antena"
    ].nunique()

    print(f"inGrid {grupo}: {quantidade}")

print("\nAnálise concluída!")

if SALVAR_IMAGENS:
    print("Imagens salvas:")
    print(Path(IMAGEM_INGRID1).resolve())
    print(Path(IMAGEM_COMPARACAO).resolve())

