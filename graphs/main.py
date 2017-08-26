import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

SUBREDDITS = ['altright', 'the_donald']
CSVS = [
    'comments/domains.csv',
    'comments/subreddits.csv',
    'comments/wikipedia.org.csv',
    'posts/domains.csv',
    'posts/subreddits.csv',
    'posts/wikipedia.org.csv'
]

for subreddit in SUBREDDITS:
    for csv in CSVS:
        print('{}:{}'.format(subreddit, csv))
        path = 'data/{}/{}'.format(subreddit, csv)
        df = pd.read_csv(path)
        N_DOMAINS = 40

        a4_dims = (11.7, 8.27)
        fig, ax = plt.subplots(figsize=a4_dims)
        df.sort_values(by='count', ascending=False, inplace=True)
        if 'subreddit' in csv:
            print(df.ix[0])
            df.drop(0, inplace=True)
        ax = sns.barplot(ax=ax, x='count', y='domain', data=df.head(N_DOMAINS), orient='h')
        ax.set_title('{} : {}'.format(subreddit, csv))
        fig.tight_layout()
        fig.savefig('output/{}_{}.png'.format(subreddit, csv.replace('/', '_')))


subreddit_sizes = {
    'the_donald': 396526, # as of 5/12/2017 17:36EST
    'altright': 7625,     # from: https://www.dailydot.com/layer8/alt-right-subreddit/ (Nov 2016)
    'funny': 17007297     # as of  5/12/2017 17:41EST
}
df = pd.DataFrame.from_dict(subreddit_sizes, orient='index')
df = df.reset_index()
df.columns = ['subreddit', 'subscribers']


a4_dims = (11.7, 8.27)
fig, ax = plt.subplots(figsize=a4_dims)
df.sort_values(by='subscribers', ascending=False, inplace=True)
ax = sns.barplot(ax=ax, x='subscribers', y='subreddit', data=df, orient='h')
ax.set_title('subreddit sizes')
fig.tight_layout()
fig.savefig('output/sizes.png')
