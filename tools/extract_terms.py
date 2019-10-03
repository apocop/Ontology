#python3

"""
Extract terms from *.kif file for translation to another language.

Example Usage:

python3 extract_terms.py --input_file=/Users/$USER/workspace/SUMO/Merge.kif \
    --output_file=testfile.kif \
    --language=JapaneseLanguage \
    --terms=termFormat,Format
"""

from absl import app
from absl import flags
import codecs
import os
import re


# Flags.
FLAGS = flags.FLAGS
flags.DEFINE_string('input_file', None, 'File to extract terms from.')
flags.DEFINE_string('output_file', None, 'File to extract terms to.')
flags.DEFINE_list('terms', 'termFormat', 'Term to extract.')
flags.DEFINE_string('language', 'EnglishLanguage', 'New language.')

# Required flags.
flags.mark_flag_as_required('input_file')
flags.mark_flag_as_required('output_file')

def main(argv):
    del argv # Unused.

    def create_term_regex(list_of_terms):
        # Construct regex for catching all terms.
        reg1 = r'\('
        reg2 = r'[\w\s]+EnglishLanguage[\s\w]+"[!$%&amp;*+-./:&lt;=&gt;?@^_~0-9A-Z_a-z\s]+"\)'

        # If the there is only one term to extract.
        if len(list_of_terms) == 1:
            term = list_of_terms[0]
            final_regex = reg1 + list_of_terms[0] + reg2

        # If there are more than one term to extract.
        elif len(list_of_terms) > 1:
            counter = 0
            final_regex = ''

            for token in list_of_terms:
                counter += 1 
                final_regex += reg1 + token + reg2
                if counter != len(list_of_terms):
                    final_regex += '|'
        print(final_regex)
        return final_regex


    # Regex Patterns.
    term_pattern = create_term_regex(FLAGS.terms)
    string_pattern = re.compile(r'"(.*?)"')

    # File Variables.
    input_file_path = FLAGS.input_file
    output_file_path = FLAGS.output_file
    base_file_name = os.path.basename(input_file_path)

    # Open input file.
    with codecs.open(input_file_path, encoding='utf-8') as f:
        text = f.read()
        
    new_line = "\n"
    space = ' '
    text = re.sub(new_line, space, text)


    extracted_term_statements = re.findall(term_pattern, text)
    pound_string = '; ' + '#' * 78 + new_line
    file_declaration = f'; The following translations are from {base_file_name}:'
    file_heading = pound_string + file_declaration + new_line + pound_string  + new_line *2
    extracted_text = file_heading

    def create_comment(pattern, string):
        # Creates a comment from the 'EnglishLanguage' string.
        comment = '; '
        text = re.search(pattern, string).group(0)
        return comment + text.strip('"') + '.'

    # Extract file
    for string in extracted_term_statements:

        string = re.sub('EnglishLanguage', FLAGS.language, string)
        comment = create_comment(string_pattern, string)
        extracted_text += comment + new_line + string + new_line * 2

    # Write new file.
    with codecs.open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(extracted_text)


if __name__ == '__main__':
  app.run(main)
