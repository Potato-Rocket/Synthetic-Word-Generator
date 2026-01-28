# Synthetic Word Generator

A simple, command-line Python script which generates natural sounding nonsense words. Given sample text such as books, articles, etc., this script analyzes the letter frequencies in words present in the text to inform word generation.

[Project Gutenberg](https://gutenberg.org/) is an excellent source for relatively large, public domain sample text. Large quantities of sample text carries diminishing returns compared to simply loading up a dictionary, since the list of words is deduplicated. However, for single texts the character of generated words sometimes resembles the overall character of the author's vocabulary, which is interesting but also somewhat difficult to quantify.

## Process

1. Loads the sample text. Remove extraneous characters and normalizes unicode while preserving hyphenation, apostrophes, and diacritics.
2. Splits the text into individual words, strips whitespace and trailing hyphens, deduplicates the word list, and excludes extremely short words.
3. Builds a Markov chain model based on the list of unique words. Describes, for any pair of preceding letters, what the probability of each possible subsequent letter is. The start and end of each word are demarcated by special characters.
4. Computes terminator probability weights, to shape the word length distribution in the output. The frequency of each possible word length is computed, normalized by the total, square-rooted to flatten the curve, then converted to a cumulative function.
5. Words are generated based on the probabilites in the model. A word ends when a terminator character is selected, the probability of which is determined by the weight corresponding to the current generated word length.

## Usage

This script is best executed from the command line.

### Arguments

- `filenames`: A list of plaintext files to use as sample text to build the Markov chain model

### Options

- `-c` or `--count`: The number of words to generate
- `-o` or `--output`: A file to write the generated words to

### Examples

```bash
./word_generator.py "/path/to/book.txt"
```

```bash
./word_generator.py "/path/to/books/"* -c 100 -o out.txt
```

## Sample Output

Following is a sample of the generator's output when provided the text of [*Moby Dick*](https://www.gutenberg.org/ebooks/2701), by Herman Melville:

```
strawartioundound
gooking
spitur
sely
jeckiscre
quaticaradaugbown
winie-anes
shille
reghbowearb
hine
```

Overall, these words seem more or less pronounceable, and are more or less free from obvious generation flaws. There is even an example of generated hyphenation, which is interesting and thus desired behavior. In theory, apostrophes and diacritics may also be generated, but in practice they are not particularly common.

## Potential Improvements

- Weighting the letter frequencies by the logarithm of the frequency of the word from which they derive may improve the character of the generations; This may turn out to be a subjective judgement, however. Thus, a new command line option is born.
- It may be interesting to provide certain interesting statistics about the sample text, such as word length distribution plots.
- The ability to parse html files and the like without polluting the data with tags may be useful.
