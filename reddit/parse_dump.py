# <http://files.pushshift.io/reddit/submissions/>

import json

processed = 0
the_donald = []
with open('RS_2016-12', 'r') as f:
    for line in f:
        processed += 1
        line = line.strip()
        data = json.loads(line)
        if processed % 100000 == 0:
            print('processed:', processed)
        if 'subreddit' not in data:
            continue
        elif data['subreddit'].lower() == 'the_donald':
            the_donald.append(data)
with open('the_donald_missing.json', 'w') as f:
    json.dump(the_donald, f)