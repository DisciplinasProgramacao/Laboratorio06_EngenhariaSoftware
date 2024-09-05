import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timezone
import statistics


df = pd.read_csv('../github_repositories_1000.csv')
df['updatedAt'] = pd.to_datetime(df['updatedAt'], utc=True)

timeSinceLastUpdate = []

for valor in df['updatedAt']:
    age = (pd.to_datetime('2024-08-21T23:59:00Z', utc=True) - valor).days
    timeSinceLastUpdate.append(age)

median_age = statistics.median(timeSinceLastUpdate)

plt.figure(figsize=(12, 8))  # Ajuste o tamanho da figura se necessário
n, bins, patches = plt.hist(timeSinceLastUpdate, bins=30, edgecolor='black', alpha=0.7)

plt.axvline(median_age, color='red', linestyle='dashed', linewidth=1.5, label=f'Mediana: {median_age:.2f} dias')

for count, bin_edge in zip(n, bins):
    plt.text(bin_edge + (bins[1] - bins[0]) / 2, count, f'{int(count)}', 
        ha='center', va='bottom', fontsize=9, color='black')

plt.title('Distribuição de tempo desde a última atualização')
plt.xlabel('Tempo (dias)')
plt.ylabel('Número de Repositórios')
plt.legend()
plt.grid(True)
plt.show()