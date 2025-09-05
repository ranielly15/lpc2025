import random
import string

# defining the possible characters: lowercase letters, numbers and space
POSSIBLE_CHARS = string.ascii_lowercase + string.digits + ' '


def validate_input(phrase):
    """
    validate if the phrase contains only allowed characters

    args:
        phrase (str): phrase to be validated

    returns:
        bool: true if the phrase is valid, false otherwise
    """
    for char in phrase:
        if char not in POSSIBLE_CHARS:
            return False
    return True


def mutate_phrase(phrase, mutation_rate=0.05):
    """
    performs random mutations in a phrase

    args:
        phrase (str): phrase to be mutated
        mutation_rate (float): mutation probability for each character

    returns:
        str: mutated phrase
    """
    new_phrase = []
    for char in phrase:
        if random.random() < mutation_rate:
            new_phrase.append(random.choice(POSSIBLE_CHARS))
        else:
            new_phrase.append(char)
    return ''.join(new_phrase)


def reproduce(best_candidate, population_size=100):
    """
    creates a population of phrases from the best candidate,
    applying mutations

    args:
        best_candidate (str): best phrase of the current generation
        population_size (int): size of the generated population

    returns:
        list: list of mutated phrases
    """
    return [mutate_phrase(best_candidate) for _ in range(population_size)]


def select_best(population, target_phrase):
    """
    selects the best phrase from the population based on
    similarity with the target phrase

    args:
        population (list): list of candidate phrases
        target_phrase (str): desired target phrase

    returns:
        tuple: best phrase found and its score
    """
    best_score = -1
    best_candidate = ''
    for phrase in population:
        # counts the correct characters in the correct positions
        score = sum(1 for a, b in zip(phrase, target_phrase) if a == b)
        if score > best_score:
            best_score = score
            best_candidate = phrase
    return best_candidate, best_score


def main():
    """
    main function that runs the natural selection algorithm
    to reach the target phrase
    """
    target_phrase = input(
        "define the target phrase (only lowercase letters, numbers and spaces): "
    ).lower()

    # validates the target phrase input
    while not validate_input(target_phrase):
        print("the phrase must contain only characters [a-z0-9 ].")
        target_phrase = input("define the target phrase: ").lower()

    # user enters the initial phrase
    initial_phrase = input(
        f"define an initial phrase with {len(target_phrase)} characters: "
    ).lower()

    while (len(initial_phrase) != len(target_phrase) or
           not validate_input(initial_phrase)):
        print(f"the phrase must have {len(target_phrase)} characters "
              "and contain only [a-z0-9 ].")
        initial_phrase = input(
            f"define an initial phrase with {len(target_phrase)} characters: "
        ).lower()

    best_candidate = initial_phrase
    generation = 0

    # loop until the target phrase is reached
    while best_candidate != target_phrase:
        population = reproduce(best_candidate)
        best_candidate, best_score = select_best(population, target_phrase)
        accuracy = (best_score / len(target_phrase)) * 100
        print(
            f"generation {generation}: {best_candidate} - "
            f"score {best_score} | accuracy: {accuracy:.2f}%"
        )
        generation += 1

    print("========== simulation finished ==========")
    print(
        f"target phrase reached in generation {generation}: "
        f"{best_candidate}"
    )


if __name__ == "__main__":
    main()
