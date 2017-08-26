import spacy
import string
import textacy
import pandas as pd
from glob import glob
from nltk.corpus import stopwords
from collections import defaultdict
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS

name = 'the_donald'
# name = 'altright'
nlp = spacy.load('en')
STOPLIST = stopwords.words('english') + ["n't", "'s", "'m", "ca", "'re"] + list(ENGLISH_STOP_WORDS)
SYMBOLS = " ".join(string.punctuation).split(" ") + ["-----", "---", "...", "“", "”", "'ve"]
SKIP = STOPLIST + SYMBOLS

print('--comments--')

df = pd.concat((pd.read_csv(f) for f in glob('{}/comments/*.csv'.format(name))))
df['date'] = pd.to_datetime(df['created_utc'], unit='s')
df.index = df['date']

months = df.groupby(pd.TimeGrouper(freq='M'))
for month, group in months:
    print(month)
    monthstr = month.strftime('%Y_%m')
    if monthstr != '2016_12':
        continue
    print('comments:', group.id.count())
    print('unique authors:', len(group.author.unique()))
    words = defaultdict(int)
    for _, row in group.iterrows():
        if isinstance(row.body, str):
            doc = nlp(row.body)
            doc = textacy.Doc(doc)
            bot = doc.to_bag_of_terms(ngrams={2, 3}, as_strings=True, named_entities=True, filter_stops=True, filter_punct=True)
            for term, count in bot.items():
                if term not in SKIP:
                    words[term] += count
    print('> 20 most common words')
    for word, count in sorted(words.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(' ', word, '->', count)

    df = {'term': [], 'count': []}
    for word, count in sorted(words.items(), key=lambda x: x[1], reverse=True):
        df['term'].append(word)
        df['count'].append(count)

    df = pd.DataFrame.from_dict(df)
    df.to_csv('{}/terms/comments/{}.csv'.format(name, monthstr), index=False)

    print('---')


# print('--posts--')

# # NOTE december posts are missing here. they're in a separate json.
# df = pd.concat((pd.read_csv(f) for f in glob('{}/posts/*.csv'.format(name))))
# df['date'] = pd.to_datetime(df['created_utc'], unit='s')
# df.index = df['date']
# months = df.groupby(pd.TimeGrouper(freq='M'))
# for month, group in months:
#     print(month)
#     print('posts:', group.id.count())
#     print('unique authors:', len(group.author.unique()))
#     print('---')