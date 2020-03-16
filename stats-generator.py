import argparse
import json
import os

import jsonlines


def parse_args():
    parser = argparse.ArgumentParser(description='Generate statistics')
    parser.add_argument('--file', metavar='file', type=str, help='file location', required=True, dest='file_location')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    file_location = args.file_location
    file = open(file_location, "r")
    reader = jsonlines.Reader(file)

    word_freq = {}

    for line in reader:
        tweet_text = line['text']
        words = tweet_text.split(' ')

        for word in words:
            if word not in word_freq:
                word_freq[word] = 0
            word_freq[word] = word_freq[word] + 1

        if 'responses' in line:
            for response in line['responses']:
                response_text = response['text']
                words = response_text.split(' ')
                for word in words:
                    if word not in word_freq:
                        word_freq[word] = 0
                    word_freq[word] += 1

    sorted_dict = {k: v for k, v in sorted(word_freq.items(), key=lambda item: item[1], reverse=True)}

    out_directory = "./results"
    if not os.path.exists(out_directory):
        os.mkdir(out_directory)

    output_file = out_directory + "/" + os.path.basename(file.name) + "_word_frequency.json"
    with open(output_file, "w", encoding="utf-8") as out_file:
        out_file.write(json.dumps(sorted_dict, indent=4, ensure_ascii=False))
