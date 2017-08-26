"""
go through extract reddit comment links
and count linked domains
"""

import re
import json
import tldextract
import pandas as pd
from tqdm import tqdm
from collections import Counter, defaultdict

SUBREDDIT_RE = re.compile('r\/[^\/]+')
EXPAND_DOMAINS = ['reddit.com', 'wikipedia.org', 'pastebin.com', 'youtube.com', 'youtu.be']

if __name__ == '__main__':
    for name in ['altright', 'the_donald']:
        types = ['post', 'comment']
        expanded = defaultdict(list)

        print(name)
        for type in types:
            print('->', type)
            with open('data/reddit/{}/links/{}_links.json'.format(name, type), 'r') as f:
                data = json.load(f)

            domains = defaultdict(list)
            scores = defaultdict(list)
            for item in tqdm(data.values()):
                if 'link' in item:
                    links = [item['link']]
                else:
                    links = [l for _, l in item['links']]
                for l in links:
                    l = l.strip()
                    if l[0] in ['#', '/']:
                        continue
                    if not l.startswith('http'):
                        l = 'http://{}'.format(l)

                    data = tldextract.extract(l)
                    domain = data.registered_domain.lower()
                    l = l.replace('http://', '').replace('https://', '')
                    if domain in EXPAND_DOMAINS:
                        expanded[domain].append(l)
                    domains[domain].append(l)
                    scores[domain].append(item['score'])

            counts = {}
            for d, ls in domains.items():
                counts[d] = {
                    'count': len(ls),
                    'mean_score': sum(scores[d])/len(ls),
                    'max_score': max(scores[d]),
                    'min_score': min(scores[d]),
                }

            with open('data/reddit/{}/links/{}_domains.json'.format(name, type), 'w') as f:
                json.dump(counts, f, indent=2, sort_keys=True)

            with open('data/reddit/{}/links/{}_domains_expanded_links.json'.format(name, type), 'w') as f:
                json.dump(expanded, f, indent=2, sort_keys=True)

            df = pd.DataFrame.from_dict(counts, orient='index')
            df.sort_values(by='count', ascending=False, inplace=True)
            df.to_csv('data/reddit/{}/links/{}_domains.csv'.format(name, type), index=True)

            for domain, links in expanded.items():
                d = dict(Counter(links))
                df = pd.DataFrame.from_dict(d, orient='index')
                df.columns = ['count']
                df.sort_values(by='count', ascending=False, inplace=True)
                df.to_csv('data/reddit/{}/links/{}_domains_expanded_links_{}.csv'.format(name, type, domain), index=True)

            subreddits = defaultdict(int)
            for link in expanded['reddit.com']:
                sr = SUBREDDIT_RE.search(link)
                if sr is not None:
                    sr = sr.group()
                subreddits[sr] += 1
            df = pd.DataFrame.from_dict(subreddits, orient='index')
            df.columns = ['count']
            df.sort_values(by='count', ascending=False, inplace=True)
            df.to_csv('data/reddit/{}/links/{}_domains_subreddits.csv'.format(name, type), index=True)
