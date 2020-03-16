import json

from googletrans import Translator

if __name__ == '__main__':
    file_location = "./results/tweets-russia-2020-03-14_20:25:16_word_frequency.json"
    translator = Translator()

    with open(file_location) as file:
        word_freq_rus = json.loads(file.read())

    word_freq_translated = {}

    filtered_dict = {k: v for k, v in word_freq_rus.items() if k != ''}
    keys = list(filtered_dict.keys())

    translations = translator.translate(keys ,src="ru", dest="en")

    for translation in translations:
        freq = word_freq_rus[translation.origin]

        print("Translated: {} -> {}".format(translation.origin, translation.text))
        word_freq_translated[translation.text] = freq

    with open("./results/word_freq_russian_en_translated.json") as f:
        f.write(json.dumps(word_freq_translated, indent=4, ensure_ascii=False))
