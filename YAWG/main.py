import random
import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import cmudict
from nltk.corpus import words

nltk.download('wordnet')
nltk.download('cmudict')
nltk.download('words')

prondict = cmudict.dict()

def scrabble_score(word):
    scores = {
        'a': 1, 'b': 3, 'c': 3, 'd': 2, 'e': 1, 'f': 4, 'g': 2, 'h': 4, 'i': 1, 'j': 8, 'k': 5, 'l': 1, 'm': 3,
        'n': 1, 'o': 1, 'p': 3, 'q': 10, 'r': 1, 's': 1, 't': 1, 'u': 1, 'v': 4, 'w': 4, 'x': 8, 'y': 4, 'z': 10
    }
    return sum(scores.get(char, 0) for char in word.lower())

#this doesnt work like i want it to
def rhymes(word1, word2):
    if word1 not in prondict or word2 not in prondict:
        return False
    return prondict[word1][-1] == prondict[word2][-1]

rhymes('cat', 'bat')

def get_rhyming_words(word):
    if word not in prondict:
        return []

    word_pronunciation = prondict[word]
    rhyming_words = []

    for w in prondict:
        if w != word and prondict[w][-1] == word_pronunciation[-1]:
            rhyming_words.append(w)

    return rhyming_words

def get_pos(word):
    synsets = wn.synsets(word)
    if not synsets:
        return None
    return synsets[0].pos()

def similarity_score(word1, word2):
    synsets1 = wn.synsets(word1)
    synsets2 = wn.synsets(word2)
    
    if not synsets1 or not synsets2:
        return 0.0
    
    max_similarity = 0.0
    for syn1 in synsets1:
        for syn2 in synsets2:
            similarity = wn.wup_similarity(syn1, syn2)
            if similarity and similarity > max_similarity:
                max_similarity = similarity
    
    return max_similarity * 100

def word_game(target_word):
    print(f"Guess the word: {'_ ' * len(target_word)}")
    guesses = 0
    max_guesses = 5
    while guesses < max_guesses:
        guess = input("Enter your guess: ").strip().lower()
        print(guess)
        guesses += 1
        if guess == target_word:
            print("Congratulations! You've guessed the word!")
            break
        else:
            sim_score = similarity_score(target_word, guess)
            pos_match = get_pos(target_word) == get_pos(guess)
            scrabble_indicator = '↑' if scrabble_score(guess) > scrabble_score(target_word) else '↓'
            rhyme_indicator = rhymes(target_word, guess)
            
            print(f"Similarity Score: {sim_score:.2f}%")
            print(f"Same Part of Speech: {'Yes' if pos_match else 'No'}")
            print(f"Scrabble Score: {scrabble_indicator}")
            print(f"Rhymes: {'Yes' if rhyme_indicator else 'No'}")
            print(f"Guesses left: {max_guesses - guesses}")
    else:
        print(f"Sorry, you've used all your guesses. The word was '{target_word}'.")

if __name__ == "__main__":
    filtered_words = [word for word in words.words() if 4 <= len(word) <= 5]
    target_word = random.choice(filtered_words).lower()
    print(target_word)
    word_game(target_word)


