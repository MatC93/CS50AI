from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
sentence0 = And(AKnave, AKnight)
knowledge0 = And(
    # A must be either Knight or Knave
    Or(AKnight, AKnave),
    # If A is Knight, then it is not a Knave, and viceversa.
    Implication(AKnave, Not(AKnight)),
    Implication(AKnight, Not(AKnave)),
    # If the sentence is True, then A is a Knight
    Implication(sentence0, AKnight),
    # If the sentence is False, then A is a Knave
    Implication(Not(sentence0), AKnave)
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
sentence1 = And(AKnave, BKnave)
knowledge1 = And(
    # A and B must be either Knight or Knave
    And(Or(AKnight, AKnave), Or(BKnight, BKnave)),
    # If A or B is Knight, then it is not a Knave, and viceversa.
    And(Implication(AKnave, Not(AKnight)), Implication(BKnave,Not(BKnight))),
    And(Implication(AKnight, Not(AKnave)), Implication(BKnight,Not(BKnave))),
    # If the sentence is True, then A is a Knight
    Implication(sentence1, AKnight),
    # If the sentence is False, then A is a Knave
    Implication(Not(sentence1), AKnave)
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
sentence2A = Or(And(AKnave, BKnave), And(AKnight, BKnight))
sentence2B = Or(And(AKnave ,BKnight), And(AKnight, BKnave))

knowledge2 = And(
    # A and B must be either Knight or Knave
    And(Or(AKnight, AKnave), Or(BKnight, BKnave)),
    # If A or B is Knight, then it is not a Knave, and viceversa.
    And(Implication(AKnave, Not(AKnight)), Implication(BKnave, Not(BKnight))),
    And(Implication(AKnight, Not(AKnave)), Implication(BKnight, Not(BKnave))),
    # If the sentence is True, then A is a Knight
    Implication(sentence2A, AKnight),
    # If the sentence is False, then A is a Knave
    Implication(Not(sentence2A), AKnave),
    # If the sentence is True, then B is a Knight
    Implication(sentence2B, BKnight),
    # If the sentence is False, then B is a Knave
    Implication(Not(sentence2B), BKnave)
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
sentence3A = Or(AKnight, AKnave)
# B says "C is a knave."
sentence3B1 = CKnave
# B says "A said 'I am a knave'." -> Could be false even if A didn't speak at all and B is a knave
sentence3B2 = And(Or(And(AKnight, BKnave), And(AKnave, BKnight)), BKnight)
# C says "A is a knight."
sentence3C = AKnight

knowledge3 = And(
    # A, B and C must be either Knight or Knave
    And(Or(AKnight, AKnave), Or(BKnight, BKnave), Or(CKnight, CKnave)),
    # If A or B or C is Knight, then it is not a Knave, and viceversa.
    And(Implication(AKnave, Not(AKnight)), Implication(BKnave, Not(BKnight)), Implication(CKnave, Not(CKnight))),
    And(Implication(AKnight, Not(AKnave)), Implication(BKnight, Not(BKnave)), Implication(CKnight, Not(CKnave))),
    # If the sentence is True, then A is a Knight
    Implication(sentence3A, AKnight),
    # If the sentence is False, then A is a Knave
    Implication(Not(sentence3A), AKnave),
    # If the sentence is True, then B is a Knight
    Implication(And(sentence3B1, sentence3B2), BKnight),
    # Both sentences of B must be either true or false
    Or(And(sentence3B1, sentence3B2), And(Not(sentence3B1), Not(sentence3B2))),
    # If the sentence is False, then B is a Knave
    Implication(And(Not(sentence3B1), Not(sentence3B2)), BKnave),
    # If the sentence is True, then C is a Knight
    Implication(sentence3C, CKnight),
    # If the sentence is False, then C is a Knave
    Implication(Not(sentence3C), CKnave)
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
