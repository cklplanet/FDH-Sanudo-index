from matcher import *
import json
import pandas as pd
import matplotlib.pyplot as plt

class MatcherWrapper:
    def __init__(self, param, method="exact"):
        self.method = method
        if method == "exact":
            self.matcher = TextMatcher(method="exact")
        elif method == "regex":
            self.matcher = TextMatcher(method="regex")
        elif method == "fuzzywuzzy":
            self.matcher = TextMatcher(method="fuzzywuzzy", threshold=param)
        elif method == "difflib":
            self.matcher = TextMatcher(method="difflib", threshold=param)
        elif method == "fuzzysearch":
            self.matcher = TextMatcher(method="fuzzysearch", max_dist=param)
        elif method == "cosine":
            self.matcher = TextMatcher(method="cosine", threshold=param)


# Initialize the total hits dictionary for all indices


dict = {"exact": [0],
        'fuzzywuzzy': [60, 65, 70, 75, 80, 85, 90],
        "fuzzysearch": [1, 2, 3],
        "difflib": [0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90]}

for m in ['exact', 'fuzzywuzzy', 'fuzzysearch', 'difflib']:
    for k in dict[m]:
        total_hits = {i: 0 for i in range(679)}
        our_matcher = MatcherWrapper(param=k, method=m)
        hitless_count = 0
        multiple_hits_count = 0
        one_hit_count = 0

        results = []
        with open('data_analysis/data_analysis_results_cleaned.json', 'r') as file:
            #note: data_analysis_results_cleaned ultimately has little difference with data_analysis_results apart from *several* entries
            #so should not be that big of a deal
            data = json.load(file)
        for place in data:
            place_names = [place['place_name']]
            place_names.extend(place['place_alternative_name'])
            indices = [int(x) for x in place['place_index'] if x.isnumeric()]
            for index in indices:
                try:
                    result, num_hits = process_files("paragraphs", index, place_names, our_matcher.matcher)
                    total_hits[index] += num_hits
                    if num_hits == 0:
                        hitless_count += 1
                    elif num_hits > 1:
                        multiple_hits_count += 1
                    else:
                        one_hit_count += 1
                    results.extend(result)
                except:
                    continue

        final = pd.DataFrame(results)
        final.to_csv(f"matching_results/{m}_{k}.csv")

        indices = list(total_hits.keys())
        hits = list(total_hits.values())

        plt.figure(figsize=(12, 6))
        plt.bar(indices, hits)
        plt.xlabel('Index')
        plt.ylabel('Total Hits')
        plt.title(f'Total Hits Across All Indices, Method: {m}, Param: {k}')
        plt.savefig(f'Graphs/{m}_{k}.png')
        plt.close()

        print(f"\nMethod {m}, params {k}: --------------------")
        print("Combos with one hit: ", one_hit_count)
        print("Combos with no hits: ", hitless_count)
        print("Combos with multiple hits: ", multiple_hits_count)