import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
from gensim.models import Word2Vec


path = "datasets/merged_datasets/"
data = pd.read_csv(path+"SpanishLaLiga17_18.csv")
print(data.shape)

""" find cards by teams """
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
    
    
