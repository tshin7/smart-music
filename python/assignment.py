from enum import Enum  # i want to use enum to clean up states part sometime
import random
import sys

cache = {}

def main():
    p = Prototype1()
    sampleStringList = p.generateString()
    sampleString = ''.join(sampleStringList)
    print(sampleStringList)
    print(sampleString)
    print("length of sampleStringList is: ", len(sampleStringList))
    p.decodeString(sampleStringList)


class Prototype1():

    def __init__(self):
        s = []
        population = []

    def getuniformpartition(self, n, parts):

        if n <= 0 or parts <= 0:
            return []
        if n < self.MinUniformPartition(parts):
            return []

        partition = []
        sum = 0
        for i in range(0, parts-1):
            max = n - self.MinUniformPartition(parts - i - 1) - sum
            partition.append(round(random.uniform(parts - i, max)))
            sum += partition[i]

        partition.append(n - sum)  # last
        return partition

    # sum of 1, 2, 3, 4,.., n
    def MinUniformPartition(self, n):
        return n * n - 1


    def generateString(self):  # this generates random garbage strings
        # for now, these are the symbols we can draw from.
        # l=loop p=play s=sleep e=end
        previousState = -1  # we dont need it now, maybe in the future
        has_sleep = False  # Value to keep track whether live_loop has sleep.
        s = []
        partitions = self.getuniformpartition(21, 4)

        # example for now, def needs to be changed
        # the sample string will be 50 chars
        for partition in partitions:

            s.append("l")
            has_sleep = False  # # There needs to be at least one sleep in the loop to avoid runtime errors.

            for i in range(0, partition):
                if i is partition-1 and has_sleep is False:
                    s.append("s")
                    sleep = round(random.uniform(0.3, 2), 2)
                    s.append(str(sleep))
                else:
                    choice = random.choice(["p", "s"])
                    s.append(choice)
                    if choice == "p":
                        note = random.randint(20, 99)  # # lets keep the range of notes to more sane and pleasant levels
                        s.append(str(note))
                    else:
                        has_sleep = True
                        sleep = round(random.uniform(0.3, 2), 2)
                        s.append(str(sleep))

            s.append("e")

        return s

    def decodeString(self, string):
        sys.stdout = open("out2.txt", "w")
        # print("original string:\n", string, "\n\n")  # for testing
        i = 0
        while i < len(string):  # # modified to update i appropriately.
            digit = i // 26
            alpha = i % 26

            loop_name = chr(65 + alpha) * (digit + 1)

            if string[i] == "l":
                temp = "live_loop :" + loop_name + " do\n"
                print(temp)
                i = i + 1
                continue
            elif string[i] == "e":
                print("end\n")
                i = i + 1
            elif string[i] == "p":
                print("play", string[i + 1], "\n")
                i = i + 2
            elif string[i] == "s":
                print("sleep", string[i + 1], "\n")
                i = i + 2

    def init_population(self, size):
        for i in range(0, size):
            self.population.append(self.generateString())

    # def selection algorithm...

    # def calculatefitness...

    # def performsimulation...

    # etc..


main()

# state 0 = outside loop (we need to start with a new loop)
# state 1 = inside loop (we need to figure out if we want to play/sleep/end
# state 2 = waiting for note #
# state 3 = waiting for sleep
