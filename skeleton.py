import re
import random
import math


class UndoState:
    def __init__(self, Targets, NumbersAllowed, Score):
        self.Targets = Targets
        self.NumbersAllowed = NumbersAllowed
        self.Score = Score

#     add accessor methods to get the values of Targets, NumbersAllowed, and Score
    def __str__(self):
        return "Targets: " + str(self.Targets) + " NumbersAllowed: " + str(
            self.NumbersAllowed) + " Score: " + str(self.Score)

    def get_Targets(self):
        return self.Targets

    def get_NumbersAllowed(self):
        return self.NumbersAllowed

    def get_Score(self):
        return self.Score

def Main():
    NumbersAllowed = []
    Targets = []
    MaxNumberOfTargets = 20
    MaxTarget = 0
    MaxNumber = 0
    TrainingGame = False
    Choice = input(
        "Enter y to play the training game, anything else to play a random game: "
    ).lower()
    print()
    if Choice == "y":
        MaxNumber = 1000
        MaxTarget = 1000
        TrainingGame = True
        Targets = [
            -1,
            -1,
            -1,
            -1,
            -1,
            23,
            9,
            140,
            82,
            121,
            34,
            45,
            68,
            75,
            34,
            23,
            119,
            43,
            23,
            119,
        ]
    else:
        MaxNumber = 10
        MaxTarget = 50
        gameLevel = int(input("Enter the game level (1-4): "))

        print("You have chosen level Standard Mode")
        NumbersAllowed = FillNumbers([], False, MaxNumber, gameLevel)
        print(f"Numbers allowed: {NumbersAllowed}")
        Targets = CreateTargets(MaxNumberOfTargets, MaxTarget)

    PlayGame(Targets, NumbersAllowed, TrainingGame, MaxTarget, MaxNumber)
    input()

def game_state_as_string(lst: list[UndoState]):
    result = ""
    for item in lst:
        result += str(item) + ", "
    return result


def undo_the_last_move(GameMoves):
    GameMoves.pop()
    Targets = GameMoves[-1].get_Targets()
    NumbersAllowed = GameMoves[-1].get_NumbersAllowed()
    Score = GameMoves[-1].get_Score()
    return Targets, NumbersAllowed, Score

def add_move_to_game_moves(GameMoves, Targets, NumbersAllowed, Score):
    GameMoves.append(UndoState(Targets, NumbersAllowed, Score))


def get_random_suggestion(Targets, NumbersAllowed):
    pass



def PlayGame(Targets, NumbersAllowed, TrainingGame, MaxTarget, MaxNumber):
    Score = 0
    GameOver = False
    GameMoves = [UndoState(Targets, NumbersAllowed, Score)]

    while not GameOver:
        DisplayState(Targets, NumbersAllowed, Score, GameMoves)
        undo_last_move = input("Enter u to undo the last move or any other key to continue: ")
        if undo_last_move.upper() == "U":
            if len(GameMoves) > 1:
                print("Undoing the last move...")
                undo_the_last_move(GameMoves)
                print("The last move has been undone")
            else:
                print("There is no move to undo")

        position_of_the_number_to_freeze = input("Enter the position of the number to freeze or n to continue: ")
        if position_of_the_number_to_freeze != "n" and int(position_of_the_number_to_freeze) < len(Targets):
            Targets[int(position_of_the_number_to_freeze)] = "<" + str(Targets[int(position_of_the_number_to_freeze)]) + ">"
        else:
            print("You have entered an invalid position")

        DisplayState(Targets, NumbersAllowed, Score, GameMoves)
        UserInput = input("Enter an expression: ")
        print()
        if UserInput.upper() == "QUIT":
            break

        if CheckIfUserInputValid(UserInput):
            UserInputInRPN = ConvertToRPN(UserInput)

            if CheckNumbersUsedAreAllInNumbersAllowed(
                NumbersAllowed, UserInputInRPN, MaxNumber
            ):
                IsTarget, Score, UserInputEvaluation = CheckIfUserInputEvaluationIsATarget(
                    Targets, UserInputInRPN, Score
                )
                if IsTarget:
                    NumbersAllowed = RemoveNumbersUsed(
                        UserInput, MaxNumber, NumbersAllowed
                    )
                    NumbersAllowed = FillNumbers(
                        NumbersAllowed, TrainingGame, MaxNumber
                    )

        Score -= 1
        if Targets[0] != -1:
            GameOver = True
        else:
            Targets = UpdateTargets(Targets, TrainingGame, MaxTarget, position_of_the_number_to_freeze)
            add_move_to_game_moves(GameMoves, Targets, NumbersAllowed, Score)

    print("Game over!")
    DisplayScore(Score, GameMoves)



def countNumberOfOperands(lst: list) -> int:
    count = 0
    for i in lst:
        if i.isdigit():
            count += 1

    return count

# check if the expression evaluates to a target(s)
def CheckIfUserInputEvaluationIsATarget(Targets, UserInputInRPN, Score):

    numberOfOperands = countNumberOfOperands(UserInputInRPN)

    UserInputEvaluation = EvaluateRPN(UserInputInRPN)

    UserInputEvaluationIsATarget = False


    if UserInputEvaluation != -1:
        for Count in range(0, len(Targets)):
            if Targets[Count] == UserInputEvaluation:
                Score += 2
                Targets[Count] = -1
                UserInputEvaluationIsATarget = True

    if UserInputEvaluationIsATarget:
        Score += (2 * numberOfOperands)
    return UserInputEvaluationIsATarget, Score, UserInputEvaluation


def RemoveNumbersUsed(UserInput, MaxNumber, NumbersAllowed):
    UserInputInRPN = ConvertToRPN(UserInput)
    for Item in UserInputInRPN:
        if CheckValidNumber(Item, MaxNumber):
            if int(Item) in NumbersAllowed:
                NumbersAllowed.remove(int(Item))
    return NumbersAllowed


def shift_left(param):
    if len(param) <= 1:
        return param
    else:
        return param[1:] + [param[0]]


def swap(param, i, j):
    param[i], param[j] = param[j], param[i]
    return param


# i-th the position of the element that is not shifted.
def shift_left_except_i_th(param, i):
            if len(param) <= 1:
                return param
            else:
                return swap(shift_left(param), i - 1, i)

def UpdateTargets(Targets, TrainingGame, MaxTarget, freez_position):
    for Count in range(0, len(Targets) - 1):
        Targets[Count] = Targets[Count + 1]
    Targets.pop()
    if TrainingGame:
        Targets.append(Targets[-1])
    else:
        Targets.append(GetTarget(MaxTarget))

    if freez_position:
        return shift_left_except_i_th(Targets, int(freez_position))
    else:
        return Targets


def CheckNumbersUsedAreAllInNumbersAllowed(NumbersAllowed, UserInputInRPN, MaxNumber):
    Temp = []
    for Item in NumbersAllowed:
        Temp.append(Item)

    for Item in UserInputInRPN:
        if CheckValidNumber(Item, MaxNumber):
            if int(Item) in Temp:
                Temp.remove(int(Item))
            else:
                print("Expression contains invalid number")
                return False

    return True


def CheckValidNumber(Item, MaxNumber):
    if re.search("^[0-9]+$", Item) is not None:
        ItemAsInteger = int(Item)
        if ItemAsInteger > 0 and ItemAsInteger <= MaxNumber:
            return True
    return False


def DisplayState(Targets, NumbersAllowed, Score, GameMoves):
    DisplayTargets(Targets)
    DisplayNumbersAllowed(NumbersAllowed)
    DisplayScore(Score, GameMoves)


def DisplayScore(Score, GameMoves):
    print(f"Moves so far: {game_state_as_string(GameMoves)}")
    print("Current score: " + str(Score) + "\n")
    print()
    print()


def DisplayNumbersAllowed(NumbersAllowed):
    print("Numbers available: ", end="")
    for N in NumbersAllowed:
        print(str(N) + "  ", end="")
    print()
    print()


def DisplayTargets(Targets):
    print("|", end="")
    for T in Targets:
        if T == -1:
            print(" ", end="")
        else:
            print(T, end="")
        print("|", end="")
    print()
    print()


def ConvertToRPN(UserInput):
    Position = 0
    Precedence = {"+": 2, "-": 2, "*": 4, "/": 4}
    Operators = []
    Operand, Position = GetNumberFromUserInput(UserInput, Position)
    UserInputInRPN = []
    UserInputInRPN.append(str(Operand))
    Operators.append(UserInput[Position - 1])
    while Position < len(UserInput):
        Operand, Position = GetNumberFromUserInput(UserInput, Position)
        UserInputInRPN.append(str(Operand))
        if Position < len(UserInput):
            CurrentOperator = UserInput[Position - 1]
            while (
                len(Operators) > 0
                and Precedence[Operators[-1]] > Precedence[CurrentOperator]
            ):
                UserInputInRPN.append(Operators[-1])
                Operators.pop()
            if (
                len(Operators) > 0
                and Precedence[Operators[-1]] == Precedence[CurrentOperator]
            ):
                UserInputInRPN.append(Operators[-1])
                Operators.pop()
            Operators.append(CurrentOperator)
        else:
            while len(Operators) > 0:
                UserInputInRPN.append(Operators[-1])
                Operators.pop()
    return UserInputInRPN


def EvaluateRPN(UserInputInRPN):
    S = []
    while len(UserInputInRPN) > 0:
        while UserInputInRPN[0] not in ["+", "-", "*", "/"]:
            S.append(UserInputInRPN[0])
            UserInputInRPN.pop(0)
        Num2 = float(S[-1])
        S.pop()
        Num1 = float(S[-1])
        S.pop()
        Result = 0.0
        if UserInputInRPN[0] == "+":
            Result = Num1 + Num2
        elif UserInputInRPN[0] == "-":
            Result = Num1 - Num2
        elif UserInputInRPN[0] == "*":
            Result = Num1 * Num2
        elif UserInputInRPN[0] == "/":
            Result = Num1 / Num2
        UserInputInRPN.pop(0)
        S.append(str(Result))
    if float(S[0]) - math.floor(float(S[0])) == 0.0:
        return math.floor(float(S[0]))
    else:
        return -1


def GetNumberFromUserInput(UserInput, Position):
    Number = ""
    MoreDigits = True
    while MoreDigits:
        if not (re.search("[0-9]", str(UserInput[Position])) is None):
            Number += UserInput[Position]
        else:
            MoreDigits = False
        Position += 1
        if Position == len(UserInput):
            MoreDigits = False
    if Number == "":
        return -1, Position
    else:
        return int(Number), Position


def CheckIfUserInputValid(UserInput):
    if re.search("^([0-9]+[\\+\\-\\*\\/])+[0-9]+$", UserInput) is not None:
        return True
    else:
        return False


def GetTarget(MaxTarget):
    return random.randint(1, MaxTarget)


def GetNumber(MaxNumber):
    return random.randint(1, MaxNumber)


def CreateTargets(SizeOfTargets, MaxTarget):
    Targets = []
    for Count in range(1, 6):
        Targets.append(-1)
    for Count in range(1, SizeOfTargets - 4):
        Targets.append(GetTarget(MaxTarget))
    return Targets


def FillNumbers(NumbersAllowed, TrainingGame, MaxNumber, GameLevel=1):
    LARGE_NUMBERS = [25, 50, 75, 100]
    if TrainingGame:
        return [2, 3, 2, 8, 512]
    else:
        randomLargeNumbers = random.sample(LARGE_NUMBERS, GameLevel)
        NumbersAllowed.extend(randomLargeNumbers)

        while len(NumbersAllowed) < 5:
            NumbersAllowed.append(GetNumber(MaxNumber))
        return NumbersAllowed


if __name__ == "__main__":
    Main()
