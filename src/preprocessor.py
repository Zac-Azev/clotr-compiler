import sys
import os

def preprocess(source_code: str) -> str:
    """
    Preprocesses CLOTR source code:
    1. Identifies lines with '#editor-note <line_number> <start_char> <end_char>'.
    2. Replaces the directive lines with spaces to preserve line numbers.
    3. Strips the specified zones from the target lines, replacing the characters 
       from start_char to end_char (inclusive) with whitespace of the same length.
    """
    lines = source_code.splitlines()
    
    # Store rules as: target_line_number (1-based) -> list of (start_char, end_char)
    rules = {}
    
    # First pass: identify and strip the directive lines
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('#editor-note'):
            parts = stripped.split()
            if len(parts) >= 4:
                try:
                    target_line = int(parts[1])
                    start_char = parts[2]
                    end_char = parts[3]
                    
                    if target_line not in rules:
                        rules[target_line] = []
                    rules[target_line].append((start_char, end_char))
                except ValueError:
                    # Ignore invalid line numbers or log error
                    pass
            # Replace the directive line itself with spaces of the same length
            lines[idx] = " " * len(line)
            
    # Second pass: apply the ignore rules
    for target_line, line_rules in rules.items():
        line_idx = target_line - 1
        if 0 <= line_idx < len(lines):
            line_content = lines[line_idx]
            for start_char, end_char in line_rules:
                # Find start_char
                start_pos = line_content.find(start_char)
                if start_pos != -1:
                    # Find end_char after start_char
                    end_pos = line_content.find(end_char, start_pos + len(start_char))
                    if end_pos != -1:
                        # Replace characters from start_pos to end_pos (inclusive) with spaces
                        length_to_replace = (end_pos + len(end_char)) - start_pos
                        replacement = " " * length_to_replace
                        line_content = (
                            line_content[:start_pos] + 
                            replacement + 
                            line_content[end_pos + len(end_char):]
                        )
            lines[line_idx] = line_content

    # Reassemble code preserving exact line endings (newlines)
    # If source_code ended with newline, we should also end with newline
    return "\n".join(lines) + ("\n" if source_code.endswith("\n") else "")

def preprocess_file(input_path: str, output_path: str) -> None:
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    clean_content = preprocess(content)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(clean_content)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 preprocessor.py <input.clotr> <output.clean>")
        sys.exit(1)
    preprocess_file(sys.argv[1], sys.argv[2])
