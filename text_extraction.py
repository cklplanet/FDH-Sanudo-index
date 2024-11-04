import json
import re
from collections import defaultdict

#TODO: extract the names in parentheses if applicable
#def extract_phrases(s):
    # This regex captures the main phrase and any phrases within parentheses
    #return re.findall(r'\b\w+\b|\(([^)]+)\)', s)

def is_end_of_indices(line):
    # Returns True if line does not start with a number or if it is a 3-character identifier
    return not starts_with_numerical(line) or (starts_with_numerical(line) and len(line) == 3)

def starts_with_numerical(s):
    return s[0].isdigit() if s else False

def strip_non_numerical(s):
    # Use regex to match from the first to the last digit
    match = re.search(r'\d.*\d', s)
    return match.group(0) if match else ''

def strip_non_alphabetical(s):
    # Use regex to match from the first to the last alphabetical character
    try:
        match = re.search(r'[a-zA-Z()]+.*[a-zA-Z()]', s)
    except:
        print(s)
    return match.group(0) if match else ''

def extract_location(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
    
    location_dict = defaultdict(list)
    # Accumulate data for multiline entries
    current_location = None
    current_indices = []
    match_flag = False
    # Regular expression to match words/phrases at the start of a line followed by a comma, excluding those in parentheses
    pattern = r'^([^,()]+(?:\([^)]*\))?[^,]*),'

    for i, line in enumerate(lines):
        if len(line) == 3: #column number line which should be skipped
            continue
        elif starts_with_numerical(line): #pure index lines
            if match_flag: #if this is still following through on a location name
                current_indices.extend(line.replace(",", " ").split())
        elif re.match(pattern, line): #lines starting with location names
                match_flag = True
                current_location_full = re.match(pattern, line).group(1)
                current_location = current_location_full.strip()
                remainder = line[len(current_location_full):]
                current_indices = remainder.replace(",", " ").split()
        if current_indices:
            if current_indices[-1][-1] == ".":
                if i < len(lines) - 1 and is_end_of_indices(lines[i + 1]):
                    current_location = strip_non_alphabetical(current_location)
                    current_indices = [strip_non_numerical(s) for s in current_indices if strip_non_numerical(s)]
                    if current_indices:
                        location_dict[current_location] = current_indices
                    current_location, current_indices = None, []
                    match_flag = False
        #theoretically this means all indice geographical and column number lines are skipped

    return location_dict

results = extract_location('sample_trunc.txt')
#Sample text: INDICE GEOGRAFICO section of Volume 29 (July 1520 - February 28, 1521)
#https://archive.org/stream/idiariidimarino48sanugoog/idiariidimarino48sanugoog_djvu.txt
with open('results.json', 'w') as file:
    json.dump(results, file, indent=4)