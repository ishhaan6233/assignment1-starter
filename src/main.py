'''
CMPUT 461-Assignment 1
Author: Ishaan Meena
Date: 24/09/2024
'''

import os
import re


# Load the CMU Pronunciation Dictionary
def load_cmu_dict(dictionary_path):
    cmu_dict = {}
    with open(dictionary_path, 'r', encoding='latin-1') as f:  # 'latin-1' encoding is used
        for line in f:
            if not line.startswith(";;;"):  # Ignore comments
                word, *phonemes = line.strip().split()  # Split word and its phonemes
                word = re.sub(r'\(\d+\)', '', word)  # Remove numeric suffixes for multiple pronunciations
                if word not in cmu_dict:
                    cmu_dict[word] = []  # Store all pronunciations
                cmu_dict[word].append(phonemes)  # Append phonemes to the list for the word
    print(f"Loaded {len(cmu_dict)} entries from CMU dictionary.")
    return cmu_dict


# Frequency-based selection of pronunciation
def frequency_based_pronunciation(word, cmu_dict):
    if word in cmu_dict:
        pronunciations = cmu_dict[word]
        # Select the first pronunciation as the most frequent
        chosen_pronunciation = pronunciations[0]  # Assume the first pronunciation is the most common
        return ' '.join(chosen_pronunciation)  # Join phonemes for the chosen pronunciation
    return word  # If the word is not in the dictionary, return it unchanged


# List of common stopwords
stopwords = set([
    "a", "an", "the", "and", "or", "but", "is", "are", "was", "were",
    "he", "she", "it", "they", "that", "this", "with", "as", "for",
    "of", "in", "on", "at", "to", "by", "from", "about", "not"
])


# Function to remove stopwords from a list of words
def remove_stopwords(words):
    return [word for word in words if word.lower() not in stopwords]


# Integrate into your clean_transcript function
def clean_transcript(text):
    cleaning_regex = r"(^@.*)|" \
                     r"(\(\(.*?\)\)|" \
                     r"<.*?>|" \
                     r"\[.*?\])|" \
                     r"(^%.*)|" \
                     r"(^\*.*?:)"

    # Match any line starting with '@' (metadata headers)
    # Match any content enclosed in double parentheses '((' and '))' (special annotations)
    # Match any content enclosed in angle brackets '<' and '>' (markup)
    # Match any content enclosed in square brackets '[' and ']' (additional annotations)
    # Match any line starting with '%' (additional information about the utterance)
    # Match any line starting with '*' (speaker tags) followed by any characters until ':'

    cleaned_lines = []
    for line in text.splitlines():
        cleaned_line = re.sub(cleaning_regex, '', line).strip()
        print(f"Original line: {line} \nCleaned line: {cleaned_line}")
        if cleaned_line:  # Only append non-empty lines
            words = cleaned_line.split()  # Remove stopwords
            words = remove_stopwords(words)
            cleaned_lines.append(' '.join(words))
    return '\n'.join(cleaned_lines)


# Transform words to ARPAbet phonemes using the CMU Pronunciation Dictionary
def transform_to_arpabet(text, cmu_dict):
    sentences = re.split(r'(?<=[.!?]) +', text)  # Split text into sentences
    transformed_sentences = []
    for sentence in sentences:
        words = re.findall(r'\w+', sentence)  # Simple word tokenizer
        transformed_text = []
        for word in words:
            word_upper = word.upper()
            pronunciation = frequency_based_pronunciation(word_upper, cmu_dict)  # Use frequency-based selection
            transformed_text.append(pronunciation)
        transformed_sentences.append(' '.join(transformed_text))
    return ' '.join(transformed_sentences)


# Recursively process the input directory and write cleaned and transformed data
def process_directory(input_dir, clean_dir, transformed_dir, cmu_dict):
    print(f"Processing directory: {input_dir}")
    for root, dirs, files in os.walk(input_dir):
        # Create corresponding clean and transformed directories
        clean_subdir = root.replace(input_dir, clean_dir)
        transformed_subdir = root.replace(input_dir, transformed_dir)
        os.makedirs(clean_subdir, exist_ok=True)
        os.makedirs(transformed_subdir, exist_ok=True)

        for file in files:
            if file.endswith(".cha"):
                input_file_path = os.path.join(root, file)
                print(f"Reading input file: {input_file_path}")

                with open(input_file_path, 'r', encoding='utf-8') as infile:
                    raw_text = infile.read()

                # Clean the transcript
                cleaned_text = clean_transcript(raw_text)
                print(f"Cleaned text for {file}: {cleaned_text}")

                # Write cleaned text to the clean directory
                clean_file_path = os.path.join(clean_subdir, file.replace(".cha", ".txt"))
                if cleaned_text:  # Only write if there is cleaned text
                    print(f"Writing cleaned text to: {clean_file_path}")  # Debugging line
                    with open(clean_file_path, 'w', encoding='utf-8') as clean_file:
                        clean_file.write(cleaned_text)

                # Transform the cleaned text to ARPAbet
                transformed_text = transform_to_arpabet(cleaned_text, cmu_dict)
                print(f"Transformed text for {file}: {transformed_text}")  # Debugging line

                # Write transformed text to the transformed directory
                transformed_file_path = os.path.join(transformed_subdir, file.replace(".cha", ".txt"))
                print(f"Writing transformed text to: {transformed_file_path}")  # Debugging line
                with open(transformed_file_path, 'w', encoding='utf-8') as transformed_file:
                    transformed_file.write(transformed_text)


if __name__ == "__main__":
    path = "C:/Users/ishha/Downloads/assignment1-starter-main/assignment1-starter-main/"  # Replace this with your PATH
    input_dir = path + "data/"  # Directory containing input .cha files
    clean_dir = path + "clean/"  # Output directory for cleaned text files
    transformed_dir = path + "transformed/"  # Output directory for transformed text files
    cmu_dict_path = path + "src/" + "cmudict.txt"  # Path to the CMU Pronunciation Dictionary

    cmu_dict = load_cmu_dict(cmu_dict_path)

    # Process all .cha files recursively
    process_directory(input_dir, clean_dir, transformed_dir, cmu_dict)
