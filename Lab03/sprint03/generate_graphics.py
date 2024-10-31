import os
import glob
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

directory = "../sprint02/results"
output_dir = "./graphics"
os.makedirs(output_dir, exist_ok=True)

all_files = glob.glob(os.path.join(directory, "*.csv"))
dfs = []

for file in all_files:
    df = pd.read_csv(file)
    dfs.append(df)

combined_df = pd.concat(dfs, ignore_index=True)

cols_to_check = ['num_files', 'additions', 'deletions', 'duration_hours', 'description_length', 'num_comments',
                 'num_reviews', 'num_participants']
combined_df = combined_df.dropna(subset=cols_to_check)
combined_df = combined_df[(combined_df[cols_to_check] != 0).any(axis=1)]

print(combined_df.head())


def size_vs_feedback():
    combined_df['num_reviews'] = combined_df['num_reviews'] + 1
    plt.figure(figsize=(12, 6))
    combined_df['tamanho_pr'] = combined_df['num_files'] + combined_df['additions'] + combined_df['deletions']
    combined_df['total_feedback'] = combined_df['num_reviews'] + combined_df['num_comments']
    sns.scatterplot(x='tamanho_pr', y='total_feedback', data=combined_df)
    plt.title('Relação entre Tamanho dos PRs e Feedback Final das Revisões')
    plt.xlabel('Tamanho do PR (num_files + additions + deletions)')
    plt.ylabel('Total de Feedback (revisões + comentários)')
    output_path = os.path.join(output_dir, "tamanho_vs_feedback_dispersao.png")
    plt.savefig(output_path)
    plt.show()
    print(f"Gráfico salvo em: {output_path}")


def time_vs_feedback():
    combined_df['num_reviews'] = combined_df['num_reviews'] + 1
    plt.figure(figsize=(12, 6))
    combined_df['total_feedback'] = combined_df['num_reviews'] + combined_df['num_comments']
    sns.scatterplot(x='duration_hours', y='total_feedback', data=combined_df)
    plt.title('Relação entre Tempo de Análise e Feedback Final das Revisões')
    plt.xlabel('Tempo de Análise (horas)')
    plt.ylabel('Total de Feedback (revisões + comentários)')
    output_path = os.path.join(output_dir, "tempo_vs_feedback_dispersao.png")
    plt.savefig(output_path)
    plt.show()
    print(f"Gráfico salvo em: {output_path}")


def description_vs_feedback():
    combined_df['num_reviews'] = combined_df['num_reviews'] + 1
    plt.figure(figsize=(12, 6))
    combined_df['total_feedback'] = combined_df['num_reviews'] + combined_df['num_comments']
    sns.scatterplot(x='description_length', y='total_feedback', data=combined_df)
    plt.title('Relação entre Descrição dos PRs e Feedback Final das Revisões')
    plt.xlabel('Comprimento da Descrição (caracteres)')
    plt.ylabel('Total de Feedback (revisões + comentários)')
    output_path = os.path.join(output_dir, "descricao_vs_feedback_dispersao.png")
    plt.savefig(output_path)
    plt.show()
    print(f"Gráfico salvo em: {output_path}")


def interactions_vs_feedback():
    combined_df['num_reviews'] = combined_df['num_reviews'] + 1
    plt.figure(figsize=(12, 6))
    combined_df['total_interactions'] = combined_df['num_participants'] + combined_df['num_comments']
    combined_df['total_feedback'] = combined_df['num_reviews'] + combined_df['num_comments']
    sns.scatterplot(x='total_interactions', y='total_feedback', data=combined_df)
    plt.title('Relação entre Interações nos PRs e Feedback Final das Revisões')
    plt.xlabel('Total de Interações (participantes + comentários)')
    plt.ylabel('Total de Feedback (revisões + comentários)')
    output_path = os.path.join(output_dir, "interacoes_vs_feedback_dispersao.png")
    plt.savefig(output_path)
    plt.show()
    print(f"Gráfico salvo em: {output_path}")


def time_vs_reviews():
    combined_df['num_reviews'] = combined_df['num_reviews'] + 1
    combined_df['duration_hours_log'] = np.log1p(combined_df['duration_hours'])
    plt.figure(figsize=(12, 6))
    sns.scatterplot(x='num_reviews', y='duration_hours_log', data=combined_df)
    plt.title('Relação entre o Tempo de Análise (horas) e o Número de Revisões')
    plt.xticks(rotation=45)
    output_path = os.path.join(output_dir, "tempo_vs_revisoes_dispersao.png")
    plt.savefig(output_path)
    print(f"Gráfico salvo em: {output_path}")


def description_vs_reviews():
    combined_df['num_reviews'] = combined_df['num_reviews'] + 1
    combined_df['description_length_log'] = np.log1p(combined_df['description_length'])
    plt.figure(figsize=(12, 6))
    sns.scatterplot(x='num_reviews', y='description_length_log', data=combined_df)
    plt.title('Relação entre o Tamanho da Descrição e o Número de Revisões')
    plt.xticks(rotation=45)
    output_path = os.path.join(output_dir, "descricao_vs_revisoes_dispersao.png")
    plt.savefig(output_path)
    print(f"Gráfico salvo em: {output_path}")


def interactions_vs_reviews():
    combined_df['num_reviews'] = combined_df['num_reviews'] + 1
    combined_df['total_interactions'] = combined_df['num_participants'] + combined_df['num_comments']
    combined_df['total_interactions_log'] = np.log1p(combined_df['total_interactions'])
    plt.figure(figsize=(12, 6))
    sns.scatterplot(x='num_reviews', y='total_interactions_log', data=combined_df)
    plt.title('Relação entre as Interações e o Número de Revisões')
    plt.xticks(rotation=45)
    output_path = os.path.join(output_dir, "interacoes_vs_revisoes_dispersao.png")
    plt.savefig(output_path)
    print(f"Gráfico salvo em: {output_path}")


def size_vs_reviews():
    combined_df['num_reviews'] = combined_df['num_reviews'] + 1
    combined_df['tamanho_pr'] = combined_df['num_files'] + combined_df['additions'] + combined_df['deletions']
    combined_df['tamanho_pr_log'] = np.log1p(combined_df['tamanho_pr'])
    plt.figure(figsize=(12, 6))
    sns.scatterplot(x='num_reviews', y='tamanho_pr_log', data=combined_df)
    plt.title('Relação entre o Tamanho dos PRs e o Número de Revisões')
    plt.xticks(rotation=45)
    output_path = os.path.join(output_dir, "tamanho_vs_revisoes_dispersao.png")
    plt.savefig(output_path)
    print(f"Gráfico salvo em: {output_path}")


size_vs_feedback()
time_vs_feedback()
description_vs_feedback()
interactions_vs_feedback()
time_vs_reviews()
description_vs_reviews()
interactions_vs_reviews()
size_vs_reviews()
