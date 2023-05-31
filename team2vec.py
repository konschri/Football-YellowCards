import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
from gensim.models import Word2Vec

"""
This script performs several data preprocessing steps to ensure data integrity.
Checking datatypes, dealing with missing values etc.
"""

path = "datasets/merged_datasets/"
data = pd.read_csv(path+"SpanishLaLiga17_18.csv")
print(data.shape)

"""
find cards by teams
"""
groups = data.groupby("HomeTeam")
home_cards = {}
for name, group in groups:
    print(name)
    home_cards[name] = group["HomeYellows"].sum()
groups["HomeYellows"].sum()


corpus = []
for _, row in data.iterrows():
    home_team = [row['HomeTeam'].lower().replace(" ", "")] * row['HomeYellows']
    away_team = [row['AwayTeam'].lower().replace(" ", "")] * row['AwayYellows']
    corpus.append(home_team + away_team)

model = Word2Vec(corpus, vector_size=100, window=5, min_count=1, sg=1, epochs=30)

team_embeddings = {}
for team in set(data['HomeTeam'].unique().tolist() + data['AwayTeam'].unique().tolist()):
    print(team)
    team_embeddings[team] = model.wv[team.lower().replace(" ", "")]
    
    
    

from sklearn.manifold import TSNE

# Convert team embeddings dictionary to a list
team_names = list(team_embeddings.keys())
embeddings = np.array(list(team_embeddings.values()))

# Apply t-SNE for dimensionality reduction
tsne = TSNE(n_components=2, random_state=42)
embeddings_2d = tsne.fit_transform(embeddings)

# Visualize the embeddings
plt.figure(figsize=(10, 8))
plt.scatter(embeddings_2d[:, 0], embeddings_2d[:, 1])
for i, team_name in enumerate(team_names):
    plt.annotate(team_name, (embeddings_2d[i, 0], embeddings_2d[i, 1]))
plt.xlabel('Dimension 1')
plt.ylabel('Dimension 2')
plt.title('Team Embeddings Visualization')
plt.show()


corpus = []
for _, row in data.iterrows():
    home_team = [row['HomeTeam']] * row['HomeYellows']
    away_team = [row['AwayTeam']] * row['AwayYellows']
    corpus.extend(home_team + away_team)
    
    
    
    
from pre_processing import process
from BasicML import MLPipeline

a = process("SpanishLaLiga17_18.csv")
data1 = a.dataPreprocess()
data2 = a.featureTransformation(1, 4, 7, 18)
    
pr = MLPipeline(data2)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    