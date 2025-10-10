import random

randomNumber = random.randint(0, 100)

def evaluateGuess(guessedNumber):
    if guessedNumber == randomNumber:
        return "Erfolg!"
    elif guessedNumber > randomNumber:
        return "Du bist drüber!"
    else:
        return "Du bist drunter!"