"""Builds the sentiment dataset for the workshop task.

Deliberately mirrors how an AI-generated dataset often looks: templated,
and with negatives frequently expressed via negation. Whether that matters
for a "sentiment direction" is exactly what the sanity-check step should test.
"""
import json, random
random.seed(0)

NOUNS = ["film", "meal", "hotel", "concert", "book", "flight", "lecture", "game",
         "service", "coffee", "museum", "play", "app", "party", "trip"]
POS = ["wonderful", "excellent", "delightful", "brilliant", "superb", "lovely",
       "fantastic", "great", "enjoyable", "impressive"]
NEG = ["awful", "terrible", "dreadful", "boring", "disappointing", "poor",
       "dull", "unpleasant", "mediocre", "frustrating"]

rows = []
for n in NOUNS:
    for _ in range(2):
        rows.append({"text": f"The {n} was {random.choice(POS)}.", "label": 1})
        # 70% of negatives use negation of a positive adjective
        if random.random() < 0.7:
            rows.append({"text": f"The {n} was not {random.choice(POS)}.", "label": 0})
        else:
            rows.append({"text": f"The {n} was {random.choice(NEG)}.", "label": 0})
random.shuffle(rows)
json.dump(rows, open("data/train.json", "w"), indent=1)

# Out-of-distribution check set: hand-written, negation decorrelated from sentiment.
ood = [
    {"text": "I can't recommend this place enough.", "label": 1},
    {"text": "Not a single dull moment in the whole show.", "label": 1},
    {"text": "There was nothing I didn't love about it.", "label": 1},
    {"text": "Never have I had a better night out.", "label": 1},
    {"text": "The staff couldn't have been kinder.", "label": 1},
    {"text": "A joy from start to finish.", "label": 1},
    {"text": "Honestly, it exceeded every expectation.", "label": 1},
    {"text": "Best decision we made all week.", "label": 1},
    {"text": "The food was cold and the waiter was rude.", "label": 0},
    {"text": "A tedious, overlong mess.", "label": 0},
    {"text": "The plot collapsed halfway through.", "label": 0},
    {"text": "We left early and regretted going at all.", "label": 0},
    {"text": "The room smelled of damp and the wifi failed.", "label": 0},
    {"text": "Painfully slow and badly organised.", "label": 0},
    {"text": "The sequel ruined everything the original built.", "label": 0},
    {"text": "Two hours I will never get back.", "label": 0},
]
json.dump(ood, open("data/ood.json", "w"), indent=1)
print(len(rows), "train rows,", len(ood), "ood rows")
