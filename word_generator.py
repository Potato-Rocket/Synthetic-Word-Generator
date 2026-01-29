#!/usr/bin/env python3
"""
Random word generation based on a provided text file.

Implements N-gram markov chains to mimic english phonetics.
"""
import unicodedata
import re
import json
import random
import logging
import sys
import argparse
from tqdm import tqdm

UNICODE_FIXES = str.maketrans({
    '\u2018': "'",  # LEFT SINGLE QUOTATION MARK
    '\u2019': "'",  # RIGHT SINGLE QUOTATION MARK
})

INITIATOR = '#'
TERMINATOR = '$'
CONTEXT_LENGTH = 2
MIN_LENGTH = 2000

def parse_words(text):
    """
    Parses the provided text into a list of unique words.

    Normalizes unicode into NFKD so that diacritics are preserved.
    Apostrophes are standardized and preserved, as are compound word hyphenations.
    Punctuation and extraneous special characters are properly stripped.

    Args:
        text: The source text to parse

    Returns:
        list: The unique words in the text, properly encoded, or None on failure
    """
    try:
        print()
        if text is None:
            logging.warning("No text provided for parsing")
            return None
        
        print("Normalizing and fixing Unicode encoding")
        # Step 1: Normalize and fix Unicode
        text = unicodedata.normalize('NFKD', text)
        text = text.lower()  # Lowers certain unicode fixes
        text = text.translate(UNICODE_FIXES)
        text = re.sub(r'-{2,}', ' ', text)   # Two or more hyphens

        print("\nStripping undesired special characters:")
        # Step 2: Strip special characters
        result = []
        for char in tqdm(text):
            category = unicodedata.category(char)
            if (category.startswith('L') or # Letters (all types)
                category == 'Mn' or         # Combining marks
                char in "'-"):              # Desired special chars
                result.append(char)
            else:
                result.append(' ')
        
        text = ''.join(result)

        print("Splitting text and collapsing duplicates:")
        # Step 3: Split words, discard short ones, count frequency
        rawlist = list(set(text.split()))
        wordlist = []
        for word in tqdm(rawlist):
            word = word.strip('-')
            if len(word) > CONTEXT_LENGTH:
                wordlist.append(word)
        
        wordlist = list(set(wordlist))

        return wordlist

    except Exception as e:
        print(f"Failed to parse text: {e}")
        return None


def build_model(wordlist):
    """
    Builds a dictionary of letter probabilities based on the unique words in the text.

    Each words is made to start with a special character and end with a different one.
    Weights are determined for each character given the previous N letters.

    Returns:
        dict: The letter probability weights for all present letter combinations
    """
    model = {}

    print("Buliding Markov chain model from text:")
    for word in tqdm(wordlist):
        # Start and end word with special characters for parsing
        word = INITIATOR + word + TERMINATOR
        # For each character in the word following the initiator
        for i in range(1, len(word)):
            # Get the context and current letter
            context = word[:i][-CONTEXT_LENGTH:]
            letter = word[i]
            # Make sure the requisite dictionary entries exist
            if context not in model.keys():
                model[context] = {}
            if letter not in model[context].keys():
                model[context][letter] = 0
            # Increment the appropriate counter
            model[context][letter] += 1
    
    return model


def length_distribution(wordlist):
    """
    Calculates terminator probability factors based on the word length distribution.

    Counts word lengths, then does a total normalization such that the the total is one.
    Takes the square root of the distribution to flatten the curve.
    Finally, calculates the cumulative distribution so a terminator gets more likely as the word gets longer.

    Args:
        wordlist: List of unique words in the text
    """
    distribution = {}

    print("Calculating word length distribution from text:")
    for word in tqdm(wordlist):
        length = len(word)
        if length not in distribution.keys():
            distribution[length] = 0
        distribution[length] += 1
    
    distribution = dict(sorted(distribution.items(), key=lambda item: item[0]))
    from matplotlib import pyplot as plt

    cumulative = [0]

    for i in range(1, max(distribution.keys()) + 1):
        value = cumulative[-1]
        if i in distribution.keys():
            value += (distribution[i] / sum(distribution.values())) ** 0.5
        cumulative.append(value)

    return cumulative


def generate_word(model, distribution):
    """
    Uses a Markov chain model to generate a Jabberwocky style gibberish word.
    
    Weights terminator probablility based on the provided distribution.

    Args:
        model: The dict markov chain model with letter probabilities
        distribution: The terminator probability factors

    Returns:
        str: The generated gibberish word
    """
    word = INITIATOR

    while word[-1] != TERMINATOR:
        context = word[-CONTEXT_LENGTH:]
        weights = model[context]
        if TERMINATOR in weights.keys():
            weights = weights.copy()
            if len(word) < len(distribution):
                weights[TERMINATOR] *= distribution[len(word)]
            else:
                weights[TERMINATOR] *= distribution[-1]
        word += random.choices(list(weights.keys()), list(weights.values()))[0]
    
    return word.strip(INITIATOR + TERMINATOR)


def generate_words(text, count):
    """
    Uses the provided text to generate Jabberwocky style gibberish words.

    Args:
        text: Source text to build Markov chain model from
        count: The number of words to generate

    Returns:
        list: The list of generated words, or None on failure
    """
    wordlist = parse_words(text)
    if wordlist is None:
        logging.warning("\nText parsing failed, cannot generate Jabberwocky words")
        return None

    model = build_model(wordlist)

    json.dump(model, open("data/model.json", "w"), indent=2, ensure_ascii=False)
    distribution = length_distribution(wordlist)

    print(f"\nGenerating {count} Jabberwocky words")
    generated = []
    while len(generated) < count:
        word = generate_word(model, distribution)
        # Makes sure the generated word is new and not a repeat
        if word in wordlist or word in generated:
            print(f"Discarded \"{word}\" because it is a word")
            continue
        print(f"Added \"{word}\" to list")
        generated.append(word)
    
    return generated


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Random word generation based on a provided text file. Implements N-gram markov chains to mimic english phonetics.")

    parser.add_argument("-c", "--count", type=int, default=10, help="the number of words to generate")

    parser.add_argument("-l", "--context_length", type=int, default=CONTEXT_LENGTH, help="the context length of the model")

    parser.add_argument("-o", "--output", help="a file to write the generated words to")

    parser.add_argument("filenames", nargs="*", help="a list of plaintext files to use as sample text to build the Markov chain model")

    args = parser.parse_args()
    CONTEXT_LENGTH = args.context_length

    text = []
    for fname in args.filenames:
        print(f"Trying to load file: {fname}")
        try:
            with open(fname, 'r') as file:
                book = file.read()
                text.append(book)

            print(f"File loaded successfully: {len(book):,} chars")

        except FileNotFoundError as e:
            print("File not found!")
    
    text = "\n\n".join(text)
    
    if len(text) < MIN_LENGTH:
        print("Insufficient text added!")
        sys.exit()
    
    print(f"\nSuccessfully loaded {len(text):,} chars in total")

    words = generate_words(text, args.count)

    if args.output:
        try:
            print(f"\nTrying to write words to file: {args.output}")
            with open(args.output, "w") as file:
                file.write('\n'.join(words))
                print(f"Successfully wrote {len(words)} words")
        
        except FileNotFoundError:
            print("Directory does not exist!")
