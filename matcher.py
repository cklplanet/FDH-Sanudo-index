import os
import re
from fuzzywuzzy import fuzz
from difflib import SequenceMatcher
from fuzzysearch import find_near_matches
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
#import spacy

class TextMatcher:
    def __init__(self, method="exact", **kwargs):
        """
        Initialize the matcher with a specific method and optional parameters.

        Parameters:
        - method: str, the matching method ("exact", "regex", "fuzzywuzzy", "difflib", "fuzzysearch", "cosine", "semantic").
        - kwargs: Additional parameters for specific methods (e.g., threshold, max_dist).
        """
        self.method = method
        self.kwargs = kwargs
        self.nlp = None
        #if method == "semantic":
            #self.nlp = spacy.load("en_core_web_sm")

    def match(self, content, keyword):
        """
        Match the keyword against the content using the selected method.

        Parameters:
        - content: str, the text to search in.
        - keyword: str, the keyword or phrase to search for.

        Returns:
        - bool: True if a match is found, False otherwise.
        """
        if self.method in {"exact", "regex"}:
            return self._match_exact_or_regex(content, keyword)
        else:
            return self._match_similarity_based(content, keyword)

    def _match_exact_or_regex(self, content, keyword):
        """
        Match content using exact or regex methods, considering slice variations.

        Parameters:
        - content: str, the text to search in.
        - keyword: str, the keyword or phrase to search for.

        Returns:
        - bool: True if a match is found, False otherwise.
        """
        keyword_lengths = [len(keyword) - 1, len(keyword), len(keyword) + 1]

        for key_len in keyword_lengths:
            if key_len < 1:  # Skip invalid slice lengths
                continue

            for i in range(len(content) - key_len + 1):
                slice_text = content[i:i + key_len]
                sliced_key = keyword[0:key_len]

                if self.method == "exact":
                    if sliced_key.lower() == slice_text.lower():
                        return True

                elif self.method == "regex":
                    pattern = re.compile(re.escape(sliced_key), re.IGNORECASE)
                    #TODO
                    if pattern.fullmatch(content):
                        return True

        return False

    def _match_similarity_based(self, content, keyword):
        """
        Match content using similarity-based methods by iterating through slices.

        Parameters:
        - content: str, the text to search in.
        - keyword: str, the keyword or phrase to search for.

        Returns:
        - bool: True if a match is found, False otherwise.
        """
        keyword_lengths = [len(keyword) - 1, len(keyword), len(keyword) + 1]
        threshold = self.kwargs.get("threshold", 0.8 if self.method in {"difflib", "cosine"} else 80)
        max_dist = self.kwargs.get("max_dist", 2)  # For fuzzysearch

        for key_len in keyword_lengths:
            if key_len < 1:  # Skip invalid slice lengths
                continue

            for i in range(len(content) - key_len + 1):
                slice_text = content[i:i + key_len]

                if self.method == "fuzzywuzzy":
                    if fuzz.partial_ratio(keyword.lower(), slice_text.lower()) >= threshold:
                        return True

                elif self.method == "difflib":
                    if SequenceMatcher(None, keyword.lower(), slice_text.lower()).ratio() >= threshold:
                        return True

                elif self.method == "fuzzysearch":
                    matches = find_near_matches(keyword, slice_text, max_l_dist=max_dist)
                    if matches:
                        return True

                elif self.method == "cosine":
                    #print(slice_text, "slice text")
                    #print(keyword, "keyword")
                    vectorizer = TfidfVectorizer().fit_transform([slice_text, keyword])
                    similarity = cosine_similarity(vectorizer[0:1], vectorizer[1:2])
                    #print(similarity, "similarity")
                    if similarity[0, 0] >= threshold:
                        return True

                #elif self.method == "semantic" and self.nlp:
                    #keyword_doc = self.nlp(keyword)
                    #slice_doc = self.nlp(slice_text)
                    #if slice_doc.similarity(keyword_doc) >= threshold:
                        #return True
        return False
    
def smart_split(input_text):
        lines = input_text.split("\n")
        #print("------------------------", lines)
        result = []
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            if stripped_line.endswith("-"):
                # Concatenate directly without space if there's a next line
                if i + 1 < len(lines):
                    result.append(stripped_line.rstrip("-") + lines[i + 1].strip())
            else:
                # Separate with a space if not at the end of the list
                result.append(stripped_line)
                if i + 1 < len(lines):
                    result.append(" ")  # Add a space between lines

        # Join the resulting list into a single string
        final_string = "".join(result)
        #print("------------------------", final_string)
        return final_string
                                    

def get_sorted_files(segment_dir, segment_number):
    # Pattern to match files like '355_0.txt', '355_1.txt', etc.
    pattern = re.compile(rf'{segment_number}_(\d+)\.txt$')
    files = []
    for filename in os.listdir(segment_dir):
        match = pattern.match(filename)
        if match:
            # Extract the numeric part after the underscore for sorting
            file_number = int(match.group(1))
            files.append((file_number, filename))
    # Sort files based on the numeric part
    files.sort()
    return [filename for _, filename in files]

def read_last_line(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if lines:
            return lines[-1].strip()
    return ''

def read_content(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def process_files(base_dir, segment_number, keywords, matcher):
    current_dir = os.path.join(base_dir, f'segment_{segment_number}')
    current_files = get_sorted_files(current_dir, segment_number)
    results = []

    for idx, filename in enumerate(current_files):
        filepath = os.path.join(current_dir, filename)
        content = read_content(filepath)

        for keyword in keywords:
            if matcher.match(content, keyword):
                is_first = idx == 0
                is_last = idx == len(current_files) - 1
                working_text = " ".join([line for line in content.split("\n")])

                if is_first:
                    prev_segment_number = int(segment_number) - 1
                    while True:
                        prev_dir = os.path.join(base_dir, f'segment_{prev_segment_number}')
                        if os.path.exists(prev_dir):
                            prev_files = get_sorted_files(prev_dir, str(prev_segment_number))
                            if prev_files:
                                last_prev_file = prev_files[-1]
                                last_prev_filepath = os.path.join(prev_dir, last_prev_file)
                                last_line = read_last_line(last_prev_filepath)

                                if len(prev_files) != 1:
                                    # Last file is not the first in its directory
                                    prev_content = read_content(last_prev_filepath)
                                    prev_string = smart_split(prev_content)
                                    working_text = prev_string.strip().strip('-') + working_text if prev_string.strip().endswith('-') else prev_string.strip() + ' ' + working_text
                                    break  # Stop the process
                                elif last_line.endswith('.'):
                                    # Last file is the first and ends with a period
                                    break  # Stop without adding content
                                else:
                                    # Add content and continue to the previous directory
                                    prev_content = read_content(last_prev_filepath)
                                    prev_string = smart_split(prev_content)
                                    working_text = prev_string.strip().strip('-') + working_text if prev_string.strip().endswith('-') else prev_string.strip() + ' ' + working_text
                                    prev_segment_number -= 1
                            else:
                                # No files in the previous directory
                                break
                        else:
                            # No more previous directories
                            break

                if is_last:
                    last_line = read_last_line(filepath)
                    next_segment_number = int(segment_number) + 1
                    while not last_line.endswith('.'):
                        next_dir = os.path.join(base_dir, f'segment_{next_segment_number}')
                        if os.path.exists(next_dir):
                            next_files = get_sorted_files(next_dir, str(next_segment_number))
                            if next_files:
                                first_next_file = next_files[0]
                                first_next_filepath = os.path.join(next_dir, first_next_file)
                                next_content = read_content(first_next_filepath)
                                next_string = smart_split(next_content)
                                working_text = working_text.strip().strip('-') + next_string if working_text.strip().endswith('-') else working_text.strip() + ' ' + next_string

                                if len(next_files) != 1:
                                    # First file is not the last in its directory
                                    break  # Stop the process
                                else:
                                    # Continue to the next directory
                                    last_line = read_last_line(first_next_filepath)
                                    next_segment_number += 1
                            else:
                                # No files in the next directory
                                break
                        else:
                            # No more next directories
                            break
                #print("----#----#-----", working_text)
                results.append({'Place':keywords, 'Column No.': segment_number, 'Paragraph':working_text})
    unique_results = []
    seen = set()
    for d in results:
        # Convert unhashable types in the dictionary to hashable types
        d_hashable = {k: tuple(v) if isinstance(v, list) else v for k, v in d.items()}
        t = tuple(sorted(d_hashable.items()))
        if t not in seen:
            seen.add(t)
            unique_results.append(d)
    return unique_results, len(unique_results)


# Process the files
#process_files(base_directory, segment_num, search_keyword)


if __name__ == "__main__":
    # Example content and keyword
    # bogus match
    #content = "[potentially long other text here] Fier Lama [potentially long other text here]"
    #keyword = "Fiat Lux"
    # [matches: False False False False False False], as intended

    # actual potential match
    #content = "[potentially long other text here] Fiai La>< [potentially long other text here]"
    #keyword = "Fiat Lux"
    # [matches: False False True True True False]

    # near perfect match
    content = "[potentially long other text here] Fiat Luce [potentially long other text here]"
    keyword = "Fiat Lux"
    # [matches: True True True True True True]

    # Exact match
    matcher_exact = TextMatcher(method="exact")
    print(matcher_exact.match(content, keyword))

    # Regex match
    matcher_regex = TextMatcher(method="regex")
    print(matcher_regex.match(content, keyword))

    # Fuzzy match
    matcher_fuzzy = TextMatcher(method="fuzzywuzzy", threshold=70)
    print(matcher_fuzzy.match(content, keyword))
    #(make or break threshold: 55/60)

    # Difflib match
    matcher_difflib = TextMatcher(method="difflib", threshold=0.65)
    print(matcher_difflib.match(content, keyword))
    #(make or break threshold: 0.50/0.55)


    # Fuzzysearch match
    matcher_fuzzysearch = TextMatcher(method="fuzzysearch", max_dist=2)
    print(matcher_fuzzysearch.match(content, keyword))
    #(make or break threshold: 3/4)

    # Cosine similarity
    matcher_cosine = TextMatcher(method="cosine", threshold=0.3)
    print(matcher_cosine.match(content, keyword))
    # 0.3 adjusted to the Fiat Luce case

    # Semantic similarity
    #matcher_semantic = TextMatcher(method="semantic", threshold=0.8)
    #print(matcher_semantic.match(content, keyword))  # True


