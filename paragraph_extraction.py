import re
import os

def strip_single_newline(s):
    if s.endswith('\n'):
        # Strip all trailing newlines, then add one back if there were multiple
        return s.rstrip('\n') + '\n' if s.endswith('\n\n') else s.rstrip('\n')
    return s

def save_paragraph(paragraph, column, count):
        """Helper function to save current paragraph fo a segment to a file or document."""
        os.makedirs(f'paragraphs/segment_{column}', exist_ok=True)
        file_name = f'paragraphs/segment_{column}/{column}_{count}.txt'
        with open(file_name, 'w') as f:
            f.write("\n".join(paragraph))
        print(f'Saved: {file_name}')

def process_columns(selection):
    for k in selection:
        current_segment = []
        input_file = f'columns/segment_{k}_.txt'
        paragraph_count = 0
        paragraph_pattern = r'^\S.*\n\n\n\S.*$'
        try:
            with open(input_file, 'r') as f:
                lines = f.readlines()
            
            i = 0
            while i < len(lines):
                line = lines[i]
                current_segment.append(strip_single_newline(line))
                if i + 3 < len(lines):
                        next_section = "\n".join(lines[i:i+3])
                        #print("next section big ----------: ", repr(next_section))
                        if re.match(paragraph_pattern, next_section, re.DOTALL):
                            # Save current segment and reset
                            #print("NOWWWWWbigflag-----------------")
                            save_paragraph(current_segment, k, paragraph_count)
                            current_segment = []
                            paragraph_count += 1
                            i += 1  # Move past the matched lines

                i += 1
            
            if current_segment:
                save_paragraph(current_segment, k, paragraph_count)
        
        except:
            continue


process_columns(range(469,679))