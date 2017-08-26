import os
import re
import json
import requests
import pandas as pd
from glob import glob
from tqdm import tqdm
from itertools import chain
from functools import partial
from parallel import run_parallel

LINK_RE = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
MD_LINK_RE = re.compile(r'\[([^)]*)\]\(`?([^`\(\)]+)`?\)')


def extract_links(df, col, id_col):
    all_links = {}
    for _, (id, row, score) in tqdm(df[[id_col, col, 'score']].iterrows()):
        try:
            links = MD_LINK_RE.findall(row)
        except TypeError:
            # nan, keep going
            continue

        # get links that aren't in markdown form
        raw_links = LINK_RE.findall(row)

        # the extracted urls sometimes have trailing ')' and additional
        # punctuation, so clean them
        raw_links = [l.rsplit(')', 1)[0] for l in raw_links]

        # only add links that aren't already captured by the markdown regex
        urls = [l for _, l in links]
        links.extend([('', l) for l in raw_links if l not in urls])

        if links:
            all_links[id] = {
                'links': links,
                'score': score
            }
    return all_links


def download_image(dir, url):
    res = requests.get(url, stream=True)
    fname = url.split('/')[-1]
    path = os.path.join(dir, fname)
    if res.status_code == 200:
        with open(path, 'wb') as f:
            for chunk in res:
                f.write(chunk)
    else:
        print('failed to download:', url)
        # res.raise_for_status()


def extract_comment_links(name, download_images=False):
    links = {}
    for csv in glob('data/reddit/{}/comments/*.csv'.format(name)):
        df = pd.read_csv(csv)
        links.update(extract_links(df, 'body', 'id'))

    with open('data/reddit/{}/links/comment_links.json'.format(name), 'w') as f:
        json.dump(links, f)

    links = list(chain.from_iterable(v['links'] for v in links.values()))
    links = [l for _, l in links]
    exts = ['.jpg', '.jpeg', '.png', '.gif', '.gifv']
    imgs = set([l for l in links if any(e in l for e in exts)])
    print('images:', len(imgs))

    with open('data/reddit/{}/links/comment_images.txt'.format(name), 'w') as f:
        f.write('\n'.join(imgs))

    if download_images:
        run_parallel(imgs, partial(download_image, 'data/reddit/{}/images/comments'.format(name)))


def extract_post_links(name, download_images=False):
    links = {}
    for csv in glob('data/reddit/{}/posts/*.csv'.format(name)):
        df = pd.read_csv(csv)
        df['link'] = df['url']
        links.update(df.set_index('id')[['link', 'score']].to_dict(orient='index'))

    for jsn in glob('data/reddit/{}/posts/*.json'.format(name)):
        df = json.load(open(jsn, 'r'))
        links.update({d['id']: {
            'link': d['url'],
            'score': d['score']
        } for d in df})

    with open('data/reddit/{}/links/post_links.json'.format(name), 'w') as f:
        json.dump(links, f)

    links = [v['link'] for v in links.values()]
    exts = ['.jpg', '.jpeg', '.png', '.gif', '.gifv']
    imgs = set([l for l in links if any(e in l for e in exts)])
    print('images:', len(imgs))

    with open('data/reddit/{}/links/post_images.txt'.format(name), 'w') as f:
        f.write('\n'.join(imgs))

    if download_images:
        run_parallel(imgs, partial(download_image, 'data/reddit/{}/images/posts'.format(name)))


if __name__ == '__main__':
    download_images = False
    for name in ['altright', 'the_donald']:
        print(name)
        print('-> comments')
        extract_comment_links(name, download_images)

        print('-> posts')
        extract_post_links(name, download_images)
