
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

arquivo = "Comparacao_Canais.txt"
pasta_saida = Path("Graficos_Comparacao_Canais")
pasta_saida.mkdir(exist_ok=True)

# ==========================================================
# CONFIGURAÇÕES DOS HISTOGRAMAS
# ==========================================================

# Tamanho dos bins
bin_diferenca = 300       # Histograma de CH1 - CH0
bin_relativa = 1          # Histograma da diferença relativa (%)

# ==========================================================
# LEITURA DOS DADOS
# ==========================================================

dados = pd.read_csv(
    arquivo,
    sep=r"\s+",
    comment="#"
)

print("Colunas encontradas:")
print(dados.columns.tolist())

# Mantém apenas antenas com medidas válidas nos dois canais
dados = dados.replace([np.inf, -np.inf], np.nan)

dados = dados.dropna(
    subset=["Media_CH0", "Media_CH1"]
).copy()

# Recalcula a diferença para garantir a convenção:
# diferença positiva = CH1 maior que CH0
dados["Diferenca"] = dados["Media_CH1"] - dados["Media_CH0"]

# Diferença relativa em relação ao CH0
dados["Diferenca_Relativa"] = np.where(
    dados["Media_CH0"] != 0,
    100 * dados["Diferenca"] / dados["Media_CH0"],
    np.nan
)

print("\nNúmero de antenas analisadas:", len(dados))

print("\nEstatísticas:")
print(dados[["Media_CH0", "Media_CH1",
             "Diferenca", "Diferenca_Relativa"]].describe())

# ==========================================================
# 1. DISPERSÃO: CH0 x CH1
# ==========================================================

plt.figure(figsize=(9, 7))

plt.scatter(
    dados["Media_CH0"],
    dados["Media_CH1"],
    alpha=0.6,
    s=18
)

# Linha de igualdade: CH0 = CH1
limite = max(
    dados["Media_CH0"].max(),
    dados["Media_CH1"].max()
)

plt.plot(
    [0, limite],
    [0, limite],
    "r--",
    label="CH0 = CH1"
)

correlacao = dados["Media_CH0"].corr(dados["Media_CH1"])

plt.xlabel("Potência média CH0")
plt.ylabel("Potência média CH1")
plt.title(f"Comparação entre CH0 e CH1 (r = {correlacao:.3f})")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(pasta_saida / "01_Dispersao_CH0_CH1.png", dpi=300)
plt.show()

# ==========================================================
# 2. HISTOGRAMA DA DIFERENÇA CH1 - CH0
# ==========================================================

plt.figure(figsize=(9, 6))

# Define as bordas dos bins automaticamente
bins = np.arange(
    dados["Diferenca"].min(),
    dados["Diferenca"].max() + bin_diferenca,
    bin_diferenca
)

plt.hist(
    dados["Diferenca"],
    bins=bins,
    edgecolor="black",
    alpha=0.8
)

plt.axvline(0, color="red", linestyle="--",
            label="Diferença igual a zero")

plt.axvline(dados["Diferenca"].mean(),
            color="green", linestyle="--",
            label=f"Média = {dados['Diferenca'].mean():.2f}")

plt.xlabel("Diferença de potência (CH1 - CH0)")
plt.ylabel("Número de antenas")
plt.title("Distribuição das diferenças entre os canais")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(pasta_saida / "02_Histograma_Diferencas.png", dpi=300)
plt.show()

# ==========================================================
# 3. BOXPLOT DOS CANAIS
# ==========================================================

plt.figure(figsize=(8, 6))

plt.boxplot(
    [
        dados["Media_CH0"],
        dados["Media_CH1"]
    ],
    tick_labels=["CH0", "CH1"],
    showmeans=True
)

plt.ylabel("Potência média")
plt.title("Distribuição da potência média por canal")
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

plt.savefig(pasta_saida / "03_Boxplot_Canais.png", dpi=300)
plt.show()

# ==========================================================
# 4. BLAND-ALTMAN
# ==========================================================

media_canais = (
    dados["Media_CH0"] + dados["Media_CH1"]
) / 2

diferenca = dados["Media_CH1"] - dados["Media_CH0"]

media_diferenca = diferenca.mean()
desvio_diferenca = diferenca.std()

limite_superior = media_diferenca + 1.96 * desvio_diferenca
limite_inferior = media_diferenca - 1.96 * desvio_diferenca

plt.figure(figsize=(9, 7))

plt.scatter(
    media_canais,
    diferenca,
    alpha=0.6,
    s=18
)

plt.axhline(
    media_diferenca,
    color="red",
    linestyle="--",
    label=f"Diferença média = {media_diferenca:.2f}"
)

plt.axhline(
    limite_superior,
    color="green",
    linestyle=":",
    label="Limites de concordância (±1,96 DP)"
)

plt.axhline(
    limite_inferior,
    color="green",
    linestyle=":"
)

plt.xlabel("Média entre CH0 e CH1")
plt.ylabel("Diferença (CH1 - CH0)")
plt.title("Gráfico de Bland–Altman")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(pasta_saida / "04_Bland_Altman.png", dpi=300)
plt.show()

# ==========================================================
# 5. HISTOGRAMA DA DIFERENÇA RELATIVA
# ==========================================================

diferencas_relativas = dados["Diferenca_Relativa"].dropna()

plt.figure(figsize=(9, 6))

bins = np.arange(
    diferencas_relativas.min(),
    diferencas_relativas.max() + bin_relativa,
    bin_relativa
)

plt.hist(
    diferencas_relativas,
    bins=bins,
    edgecolor="black",
    alpha=0.8
)

plt.axvline(0, color="red", linestyle="--",
            label="Diferença igual a zero")

plt.axvline(diferencas_relativas.mean(),
            color="green", linestyle="--",
            label=f"Média = {diferencas_relativas.mean():.2f}%")

plt.xlabel("Diferença relativa (%)")
plt.ylabel("Número de antenas")
plt.title("Diferença relativa entre CH0 e CH1")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(pasta_saida / "05_Histograma_Diferenca_Relativa.png", dpi=300)
plt.show()

print("\nGráficos salvos em:", pasta_saida.resolve())

