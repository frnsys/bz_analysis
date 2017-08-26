import json
import pandas as pd
from glob import glob

name = 'the_donald'
data = []
d = json.load(open('{}/comment_links.json'.format(name), 'r'))
comments_df = pd.concat((pd.read_csv(f) for f in glob('{}/comments/*.csv'.format(name))))
for k, links in d.items():
    context = comments_df[comments_df.id == k].body.tolist()[0]
    for (t, u) in links:
        data.append({'id': k, 'text': t, 'url': u, 'context': context})

df = pd.DataFrame(data)
df = df.dropna()
df.to_csv('{}/comment_links.csv'.format(name), index=False)