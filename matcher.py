import os
import re
from fuzzywuzzy import fuzz
from difflib import SequenceMatcher
from fuzzysearch import find_near_matches
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

class TextMatcher:
    def __init__(self, method="exact", **kwargs):
        """
        Initialize the matcher with a specific method and optional parameters.

        Parameters:
        - method: str, the matching method ("exact", "fuzzywuzzy", "difflib", "regex", "fuzzysearch", "cosine", "semantic")
        - kwargs: Additional parameters for specific methods (e.g., threshold, max_dist).
        """
        self.method = method
        self.kwargs = kwargs
        self.nlp = None
        if method == "semantic":
            self.nlp = spacy.load("en_core_web_sm")

    def match(self, content, keyword):
        """
        Match the keyword against the content using the selected method.

        Parameters:
        - content: str, the text to search in.
        - keyword: str, the keyword or phrase to search for.

        Returns:
        - bool: True if a match is found, False otherwise.
        """
        if self.method == "exact":
            return keyword in content

        elif self.method == "fuzzywuzzy":
            threshold = self.kwargs.get("threshold", 80)
            sentences = content.split('\n')
            return any(fuzz.partial_ratio(keyword.lower(), sentence.lower()) >= threshold for sentence in sentences)

        elif self.method == "difflib":
            threshold = self.kwargs.get("threshold", 0.8)
            sentences = content.split('\n')
            return any(SequenceMatcher(None, keyword.lower(), sentence.lower()).ratio() >= threshold for sentence in sentences)

        elif self.method == "regex":
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            return bool(pattern.search(content))

        elif self.method == "fuzzysearch":
            max_dist = self.kwargs.get("max_dist", 2)
            matches = find_near_matches(keyword, content, max_l_dist=max_dist)
            return bool(matches)

        elif self.method == "cosine":
            threshold = self.kwargs.get("threshold", 0.7)
            vectorizer = TfidfVectorizer().fit_transform([content, keyword])
            similarity_matrix = cosine_similarity(vectorizer)
            return similarity_matrix[0, 1] >= threshold

        elif self.method == "semantic":
            threshold = self.kwargs.get("threshold", 0.7)
            doc_content = self.nlp(content)
            doc_keyword = self.nlp(keyword)
            return doc_content.similarity(doc_keyword) >= threshold

        else:
            raise ValueError(f"Unknown matching method: {self.method}")

# Example usage:
#def process_files_with_configurable_matching(base_dir, segment_number, keyword, match_method="exact", **kwargs):
    #matcher = TextMatcher(method=match_method, **kwargs)
    #current_dir = os.path.join(base_dir, f'segment_{segment_number}')
    #current_files = get_sorted_files(current_dir, segment_number)

    #for filename in current_files:
        filepath = os.path.join(current_dir, filename)
        content = read_content(filepath)

        if matcher.match(content, keyword):
            # Handle matched files as before
            print(f"Match found in file: {filename}")
            # Process the file (e.g., generate working text)




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

def process_files(base_dir, segment_number, keyword):
    current_dir = os.path.join(base_dir, f'segment_{segment_number}')
    current_files = get_sorted_files(current_dir, segment_number)

    for idx, filename in enumerate(current_files):
        filepath = os.path.join(current_dir, filename)
        content = read_content(filepath)

        if keyword in content:
            is_first = idx == 0
            is_last = idx == len(current_files) - 1
            working_text = content

            if is_first:
                prev_segment_number = str(int(segment_number) - 1)
                prev_dir = os.path.join(base_dir, f'segment_{prev_segment_number}')
                if os.path.exists(prev_dir):
                    prev_files = get_sorted_files(prev_dir, prev_segment_number)
                    if prev_files:
                        last_prev_file = prev_files[-1]
                        last_prev_filepath = os.path.join(prev_dir, last_prev_file)
                        last_line = read_last_line(last_prev_filepath)
                        if not last_line.endswith('.'):
                            prev_content = read_content(last_prev_filepath)
                            working_text = prev_content + '\n' + working_text

            elif is_last:
                last_line = read_last_line(filepath)
                if not last_line.endswith('.'):
                    next_segment_number = str(int(segment_number) + 1)
                    next_dir = os.path.join(base_dir, f'segment_{next_segment_number}')
                    if os.path.exists(next_dir):
                        next_files = get_sorted_files(next_dir, next_segment_number)
                        if next_files:
                            first_next_file = next_files[0]
                            first_next_filepath = os.path.join(next_dir, first_next_file)
                            next_content = read_content(first_next_filepath)
                            working_text = working_text + '\n' + next_content

            # Use the working_text variable as needed
            print(f"Working text for file {filepath}:\n{working_text}\n{'-'*50}")

# Parameters
base_directory = '/segment'  # Base directory where segments are stored
segment_num = '355'          # Current segment number as a string
search_keyword = 'Fiat'      # Keyword to search for

# Process the files
process_files(base_directory, segment_num, search_keyword)


