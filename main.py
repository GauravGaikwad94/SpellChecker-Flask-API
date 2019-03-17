import os
from flask import Flask, jsonify, request
from symspellpy.symspellpy import SymSpell, Verbosity

app = Flask(__name__)

SYM_SPELL = None


def load_package():
    global SYM_SPELL
    # maximum edit distance per dictionary precalculation
    if SYM_SPELL:
        return SYM_SPELL
    max_edit_distance_dictionary = 2
    prefix_length = 7
    # create object
    SYM_SPELL = SymSpell(max_edit_distance_dictionary, prefix_length)
    # load dictionary
    dictionary_path = os.path.join(os.path.dirname(__file__),
                                   "frequency_dictionary_en_82_765.txt")
    term_index = 0  # column of the term in the dictionary text file
    count_index = 1  # column of the term frequency in the dictionary text file
    if not SYM_SPELL.load_dictionary(dictionary_path, term_index, count_index):
        print("Dictionary file not found")
    return SYM_SPELL


@app.route('/spellCorrect', methods=['GET'])
def get_tasks():
    input_term = request.args['input_term']
    correct_words = []
    sym_spell = load_package()
    max_edit_distance_lookup = 2
    # lookup suggestions for multi-word input strings (supports compound
    # splitting & merging)
    suggestions = sym_spell.lookup_compound(input_term,
                                            max_edit_distance_lookup)
    for suggestion in suggestions:
        correct_words.append(suggestion.term)
    # lookup suggestions for single-word input strings
    suggestion_verbosity = Verbosity.CLOSEST  # TOP, CLOSEST, ALL
    suggestions = sym_spell.lookup(input_term, suggestion_verbosity,
                                   max_edit_distance_lookup)
    for suggestion in suggestions:
        if suggestion.term not in correct_words:
            correct_words.append(suggestion.term)
    return jsonify(correct_words)


if __name__ == '__main__':
    app.run(debug=True)
