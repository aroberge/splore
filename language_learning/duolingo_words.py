# Duolingo makes it extremely hard to extract the words learned
# together with their translations.
#
# On the Duolingo site, we can go to https://www.duolingo.com/practice-hub/words
# click on "more" at the bottom of the word list until we can see all the words 
# found so far.

# Then we can use developers tools (inspect) to figure copy all the words
# and their translations ... in a HUGE xml structure and save this to a file.
# Then we can use this python script to extract the list of known "words"
# and save them in a csv file ready to be imported in Lute.
#
# Once this is done, one can periodically extract the new words (clicking "more"
# until we see the previously known words) and manually combine the new csv file
# with the old one, to get what will eventually be a complete word file.
#


import csv

terms = {}

def read_file_in_chunks(file_path, chunk_size=1024):
    current_text = ''
    with open(file_path, 'r') as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            current_text = process(current_text+chunk)


def process(text):
    global terms
    while '<h3>' in text and '</h3>' in text and '<p>' in text and '</p>' in text:
        loc_h3 = text.find('<h3>')
        loc_h3_end = text.find('</h3>')
        loc_p = text.find('<p>')
        loc_p_end = text.find('</p>')
        spanish_word = text[loc_h3 + 4 :loc_h3_end].strip()
        translation = text[loc_p + 3 :loc_p_end].strip()
        translation = translation.replace(",", ";")
        text = text[loc_p_end + 3:]
        terms[spanish_word] = translation
    return text


read_file_in_chunks("duolingo.txt")

with open('new_duolingo_words.csv', 'w', newline='\n') as csvfile:
    words_writer = csv.writer(csvfile, delimiter=',')
    words_writer.writerow(["language", "term", "translation", "parent", "status"])
    for term in terms:
        words_writer.writerow(["Spanish", term, terms[term], '', '1'])
