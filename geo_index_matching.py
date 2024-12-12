from matcher import *
import json
import pandas as pd
import matplotlib.pyplot as plt

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


# Initialize the total hits dictionary for all indices
total_hits = {i: 0 for i in range(679)}

for m in ['exact','regex','fuzzywuzzy','difflib','fuzzysearch']:

    our_matcher = MatcherWrapper(method=m)

    results = []
    with open('data_analysis/data_analysis_results.json', 'r') as file:
        data = json.load(file)
    for place in data:
        place_names = [place['place_name']]
        place_names.extend(place['place_alternative_name'])
        indices = [int(x) for x in place['place_index'] if x.isnumeric()]
        for index in indices:
            try:
                result, num_hits = process_files("paragraphs", index, place_names, our_matcher.matcher)
                total_hits[index] += num_hits
                results.extend(result)
            except:
                continue

    final = pd.DataFrame(results)
    final.to_csv(f"matching_results/{m}.csv")

    indices = list(total_hits.keys())
    hits = list(total_hits.values())

    plt.figure(figsize=(12, 6))
    plt.bar(indices, hits)
    plt.xlabel('Index')
    plt.ylabel('Total Hits')
    plt.title(f'Total Hits Across All Indices, Method: {m}')
    plt.savefig(f'Graphs/{m}.png')
    plt.show()