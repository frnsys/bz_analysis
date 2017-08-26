import pandas as pd
from glob import glob

dfs = []
for csv in glob('*.csv'):
    df_ = pd.read_csv(open(csv, 'rU'), encoding='utf-8')
    df_['month_year'], _ = csv.split('.')
    dfs.append(df_)

df = pd.concat(dfs)
print(df.head())

df.to_csv('altright_comment_terms.csv', index=False)