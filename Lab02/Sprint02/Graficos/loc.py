import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('../repositorios_metricas.csv')

plt.figure(figsize=(10, 6))
sns.scatterplot(x='LOC', y='LCOM', data=df)
plt.title('Tamanho dos Repositórios (LOC) vs LCOM')
plt.xlabel('LOC')
plt.ylabel('LCOM')
plt.grid(True)
plt.show()


