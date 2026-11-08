
import numpy as np
import matplotlib.pyplot as plt

# ==================================================
# CONFIGURAÇÕES
# ==================================================

arquivo = "2MASS.txt"

nome_saida = "Mapa_2MASS.png"

# Aparência dos pontos
cor_pontos = "black"
tamanho_pontos = 1.0
transparencia = 0.5

# ==================================================
# LEITURA DOS DADOS
# ==================================================

# O arquivo não possui cabeçalho.
# Colunas:
# 0 - Longitude galáctica (l)
# 1 - Latitude galáctica (b)
# 2 - Distância (Mpc)
# 3 - wtotal

dados = np.loadtxt(arquivo)

l = dados[:, 0]
b = dados[:, 1]

print(f"Total de objetos no catálogo: {len(l)}")

# ==================================================
# CONVERSÃO DAS COORDENADAS GALÁCTICAS
# ==================================================

longitude = ((-l + 180) % 360) - 180

longitude = np.radians(longitude)
latitude = np.radians(b)

# ==================================================
# CONSTRUÇÃO DO MAPA
# ==================================================

fig = plt.figure(figsize=(13, 7))

ax = fig.add_subplot(111, projection="mollweide")

ax.scatter(
    longitude,
    latitude,
    s=tamanho_pontos,
    color=cor_pontos,
    alpha=transparencia,
    rasterized=True
)

# Grade
ax.grid(True, linestyle="--", alpha=0.5)

# Marcações do eixo da longitude galáctica
ticks_graus = np.arange(-180, 181, 30)
ticks_rad = np.radians(ticks_graus)

rotulos = [str(int((-t) % 360)) for t in ticks_graus]

ax.set_xticks(ticks_rad)
ax.set_xticklabels(rotulos)

# Rótulos dos eixos
ax.set_xlabel("Longitude galáctica (°)", fontsize=12)
ax.set_ylabel("Latitude galáctica (°)", fontsize=12)

ax.set_title(
    "Distribuição das galáxias do catálogo 2MASS",
    fontsize=15,
    pad=20
)

# ==================================================
# SALVAR E EXIBIR
# ==================================================

plt.savefig(
    nome_saida,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print(f"Mapa salvo como: {nome_saida}")

