import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timezone
import statistics


df = pd.read_csv('../github_repositories_1000.csv')
df['createdAt'] = pd.to_datetime(df['createdAt'], utc=True)
now = datetime.now(timezone.utc)

ages = []

for valor in df['createdAt']:
    age = (now - valor).days / 365.25
    ages.append(age)

median_age = statistics.median(ages)

plt.figure(figsize=(12, 8))  # Ajuste o tamanho da figura se necessário
n, bins, patches = plt.hist(ages, bins=30, edgecolor='black', alpha=0.7)

plt.axvline(median_age, color='red', linestyle='dashed', linewidth=1.5, label=f'Mediana: {median_age:.2f} anos')

for count, bin_edge in zip(n, bins):
    plt.text(bin_edge + (bins[1] - bins[0]) / 2, count, f'{int(count)}', 
        ha='center', va='bottom', fontsize=9, color='black')

plt.title('Distribuição da Idade dos Repositórios')
plt.xlabel('Idade dos Repositórios (anos)')
plt.ylabel('Número de Repositórios')
plt.legend()
plt.grid(True)
plt.show()