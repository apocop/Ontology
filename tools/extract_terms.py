#python3

"""
Extract terms from *.kif file for translation to another language.

Example Usage:

Definitions:
    lang_loc: Stands for Language-Location, the ISO 639-1 codes for language.
    The location is optional, and not available for most languages.

    I.E. es-MX is "Spanish of Mexico" and "es-ES" is "Spanish of Spain".

    auto_translate: Will provide a Machine Translation for the string.
    The statement will be automatically commented out and a warning message
    will be provided at the top of the file.


python3 extract_terms.py --input_file=/Users/$USER/workspace/SUMO/Merge.kif \
    --output_file=testfile.kif \
    --lang_loc=es \
    --terms=termFormat,Format \
    --auto_translate=True

"""

from absl import app
from absl import flags
import googletrans as gt
import codecs
import os
import re


# Flags.
FLAGS = flags.FLAGS
flags.DEFINE_string('input_file', None, 'File to extract terms from.')
flags.DEFINE_string('output_file', None, 'File to extract terms to.')
flags.DEFINE_list('terms', 'termFormat', 'Term to extract.')
flags.DEFINE_string('lang_loc', None, 'New language.')
flags.DEFINE_boolean('auto_translate', False, 'Autotranslate term text.')

# Required flags.
flags.mark_flag_as_required('input_file')
flags.mark_flag_as_required('output_file')
flags.mark_flag_as_required('lang_loc')

def main(argv):
    del argv # Unused.

    def create_term_regex(list_of_terms):
        # Construct regex to find one or more terms.
        reg1 = r'\('
        reg2 = r'[\w\s]+EnglishLanguage[\s\w]+"[!$%&amp;*+-./:&lt;=&gt;?@^_~0-9A-Z_a-z\s]+"\)'

        # If the there is only one term to extract.
        if len(list_of_terms) == 1:
            term = list_of_terms[0]
            final_regex = reg1 + term + reg2

        # If there is more than one term to extract.
        elif len(list_of_terms) > 1:
            counter = 0
            final_regex = ''

            for token in list_of_terms:
                counter += 1 
                final_regex += reg1 + token + reg2
                if counter != len(list_of_terms):
                    final_regex += '|'
        return final_regex


    def create_comment(pattern, string):
        # Creates a comment from the OL string.
        comment_start = '; '
        text = re.search(pattern, string).group(0)
        return comment_start + text.strip('"') + '.'


    def get_translation(ol_string):
        # Get translation of a single string.
        translation = translator.translate(ol_string, src='en', dest=lang_loc).text
        return translation


    # Regex Patterns.
    term_pattern = create_term_regex(FLAGS.terms)
    string_pattern = re.compile(r'"(.*?)"')

    # Define language string.
    lang_loc = FLAGS.lang_loc
    sumo_language_name = gt.LANGUAGES[lang_loc].capitalize() + 'Language'

    # File Variables.
    input_file_path = FLAGS.input_file
    output_file_path = FLAGS.output_file
    base_file_name = os.path.basename(input_file_path)

    # Open input file.
    with codecs.open(input_file_path, encoding='utf-8') as f:
        text = f.read()

    # Create Translate object.
    translator = gt.Translator()

    new_line = "\n"
    space = ' '
    text = re.sub(new_line, space, text)

    extracted_term_statements = re.findall(term_pattern, text)

    pound_string = '; ' + '#' * 78 + new_line
    file_declaration = f'; The following translations are from {base_file_name}:'
    file_heading = pound_string + file_declaration + new_line + pound_string  + new_line * 2
    extracted_text = file_heading

    if FLAGS.auto_translate == True:

        # This is a warning and TODO for the generated file.
        warning = """; ¡¡¡Warning!!! This file contains automatic translations.
; TODO: Remove once translations has been manually curated.\n\n"""
        extracted_text += warning + new_line

    # Create string to be written to output file.
    for statement in extracted_term_statements:

        statement = re.sub('EnglishLanguage', sumo_language_name, statement)
        comment = create_comment(string_pattern, statement)

        if FLAGS.auto_translate == True:
            string = re.search(string_pattern, statement).group(0)
            translation = get_translation(string)
            trans_statement = re.sub(string_pattern, translation, statement)


            extracted_text += comment + new_line + ';' + trans_statement + new_line * 2
        else:
            extracted_text += comment + new_line + statement + new_line * 2


    # Write new file.
    with codecs.open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(extracted_text)


if __name__ == '__main__':
  app.run(main)
