from matcher import *
import json
import pandas as pd

class MatcherWrapper:
    def __init__(self, method="exact"):
        self.method = method
        if method == "exact":
            self.matcher = TextMatcher(method="exact")
        elif method == "regex":
            self.matcher = TextMatcher(method="regex")
        elif method == "fuzzywuzzy":
            self.matcher = TextMatcher(method="fuzzywuzzy", threshold=60)
        elif method == "difflib":
            self.matcher = TextMatcher(method="difflib", threshold=0.55)
        elif method == "fuzzysearch":
            self.matcher = TextMatcher(method="fuzzysearch", max_dist=3)
        elif method == "cosine":
            self.matcher = TextMatcher(method="cosine", threshold=0.3)


our_matcher = MatcherWrapper(method="exact")

results = []
with open('place_verification_results_trunc.json', 'r') as file:
    data = json.load(file)
for place in data[0:10]:
    place_names = [place['place_name']]
    place_names.extend(place['place_alternative_name'])
    indices = [int(x) for x in place['place_index'] if x.isnumeric()]
    for index in indices:
        try:
            result = process_files("paragraphs", index, place_names, our_matcher.matcher)
            results.extend(result)
        except:
            continue

final = pd.DataFrame(results)
final.to_csv("tentative_results.csv")