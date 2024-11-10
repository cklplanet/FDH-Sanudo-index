import re

def strip_single_newline(s):
    if s.endswith('\n'):
        # Strip all trailing newlines, then add one back if there were multiple
        return s.rstrip('\n') + '\n' if s.endswith('\n\n') else s.rstrip('\n')
    return s

def process_text_document(input_file):
    # Split input text into lines and initialize variables
    current_segment = []
    segment_count = 1  # Counter for naming output files or segments
    big_pattern = r'^\S.*\n\n\n\n\n\n\n\n\S.*\n\n\n\n\n\n\n\n\S.*$'  # Pattern for matching three consecutive newlines with non-empty lines
    small_pattern = r'^\S.*\n\n\n\n\n\n\n\n\S.*$'  # Pattern for matching three consecutive newlines with non-empty lines
    big_flag = False
    small_flag = True

    def save_segment(segment, count):
        """Helper function to save current segment to a file or document."""
        file_name = f'columns/segment_{count}.txt'
        with open(file_name, 'w') as f:
            f.write("\n".join(segment))
        print(f'Saved: {file_name}')

    with open(input_file, 'r') as f:
        lines = f.readlines()

    # Loop through lines
    i = 0
    while i < len(lines):
        line = lines[i]
        current_segment.append(strip_single_newline(line))
        # Check for the pattern by examining the next few lines
        if i + 8 < len(lines):
            #if we're looking for a BIG match here
            if big_flag == True:
                next_section = "\n".join(lines[i:i+9])
                #print("next section big ----------: ", repr(next_section))
                if re.match(big_pattern, next_section, re.DOTALL):
                    # Save current segment and reset
                    #print("NOWWWWWbigflag-----------------")
                    save_segment(current_segment, segment_count)
                    big_flag = False
                    small_flag = True
                    current_segment = [strip_single_newline(line) for line in lines[i+1:i+9]]
                    segment_count += 1
                    # Skip the lines we've checked as part of the pattern
                    i += 8  # Move past the matched lines
                    current_segment.extend([strip_single_newline(line) for line in lines[i+1:i+9]])
                    i += 8
            elif small_flag == True:
                next_section = "\n".join(lines[i:i+9])
                #print("next section small ----------: ", repr(next_section))
                if re.match(small_pattern, next_section, re.DOTALL):
                    #print("NOWWWWWsmallflag-----------------")
                    current_segment.extend(strip_single_newline(line) for line in lines[i+1:i+8])
                    save_segment(current_segment, segment_count)
                    big_flag = True
                    small_flag = False
                    current_segment = [strip_single_newline(lines[i+8])]
                    segment_count += 1
                    i += 8  # Move past the matched lines


        i += 1

    # Save any remaining lines in the last segment
    if current_segment:
        save_segment(current_segment, segment_count)

# Example usage with a text block

process_text_document("sample_proper_text.txt")

#TODO: function that autoprocesses the actually manually corrected the indices