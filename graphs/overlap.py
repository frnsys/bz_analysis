import locale
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

locale.setlocale(locale.LC_ALL, '')
N_DOMAINS = 40
SUBREDDITS = ['altright', 'the_donald']
CSVS = [
    'comments/subreddits.csv',
    'comments/wikipedia.org.csv',
]

def load_df(subreddit, csv):
    df = pd.read_csv('data/{}/{}'.format(subreddit, csv)).dropna()
    df.sort_values(by='count', ascending=False, inplace=True)
    if 'subreddit' in csv:
        # skip first subreddit since it's always a self-reference
        df.drop(0, inplace=True)
    return df


def count_domains(df, d):
    total = df['count'].sum()
    count = df[df.domain == d]['count'].values[0]
    return count, count/total * 100


for csv in CSVS:
    df_a = load_df('altright', csv)
    df_b = load_df('the_donald', csv)

    total_a = df_a['count'].sum()
    total_b = df_b['count'].sum()

    domains_a = df_a.domain.values
    domains_b = df_b.domain.values
    overlap = set(domains_a) & set(domains_b)
    overlap = [(
        d,
        count_domains(df_a, d),
        count_domains(df_b, d)
    ) for d in overlap]
    overlap = sorted(overlap, key=lambda k: k[1][1] + k[2][1], reverse=True)
    overlap = overlap[:N_DOMAINS]
    data = []
    for d, (a_count, a_percent), (b_count, b_percent) in overlap:
        data.append({
            'domain': d,
            'subreddit': 'r/altright',
            'percent': a_percent,
            'count': a_count
        })
        data.append({
            'domain': d,
            'subreddit': 'r/The_Donald',
            'percent': b_percent,
            'count': b_count
        })
    df = pd.DataFrame.from_dict(data)

    a4_dims = (11.7, 8.27)
    fig, ax = plt.subplots(figsize=a4_dims)
    ax = sns.barplot(ax=ax, x='percent', y='domain',
                     hue='subreddit', data=df, orient='h',
                     palette='bright')

    if 'subreddit' in csv:
        ax.set_title('Overlap of subreddit links b/w r/altright and r/The_Donald')
    elif 'wikipedia' in csv:
        ax.set_title('Overlap of Wikipedia links b/w r/altright and r/The_Donald')
    ax.set_xlabel('Percent of references')

    # the way ax.patches is ordered
    # is such that all bars for one hue are plotted first,
    # then the next, etc
    subreddits = ['r/altright', 'r/The_Donald']
    patches = [ax.patches[:N_DOMAINS], ax.patches[N_DOMAINS:]]
    for sr, patches in zip(subreddits, patches):
        for (i, row), p in zip(df[df.subreddit == sr].iterrows(), patches):
            ax.text(p.get_x()+(p.get_width()*1.01),
                    p.get_y()+p.get_height()/2.,
                    locale.format('%d', row['count'], grouping=True),
                    # '{}_{}_{}'.format(row.domain, row.subreddit, row['count']),
                    va='center',
                    fontsize=7)

    fig.tight_layout()
    fname = 'output/overlap_{}.png'.format(csv.replace('/', '_'))
    fig.savefig(fname)
    print(fname)