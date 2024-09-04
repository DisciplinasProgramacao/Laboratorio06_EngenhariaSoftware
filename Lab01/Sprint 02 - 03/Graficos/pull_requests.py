import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv('../github_repositories_1000.csv')
data = df['pullRequests']

median_value = data.median()

plt.figure(figsize=(12, 8))
n, bins, patches = plt.hist(data, bins=30, edgecolor='black', alpha=0.7)

plt.axvline(median_value, color='red', linestyle='dashed', linewidth=1.5, label=f'Mediana: {median_value:.2f}')

for count, bin in zip(n, bins):
    plt.text(bin + (bins[1] - bins[0]) / 2, count, f'{int(count)}', 
             ha='center', va='bottom', fontsize=9, color='black')

plt.title('Distribuição do Número de Pull Requests')
plt.xlabel('Número de Pull Requests')
plt.ylabel('Número de Repositórios')
plt.legend()
plt.grid(True)
plt.show()