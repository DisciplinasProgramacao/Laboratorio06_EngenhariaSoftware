import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('../repositorios_metricas.csv')
data = df['LCOM']

plt.figure(figsize=(10, 6))
sns.scatterplot(x='estrelas', y='LCOM', data=df)
plt.title('Popularidade (Estrelas) vs LCOM')
plt.xlabel('Estrelas')
plt.ylabel('LCOM')
plt.grid(True)
plt.show()