# Attempting to answer
# https://twitter.com/ctitusbrown/status/1447268307392872449

class FileReader:

    def __init__(self, filename):
        self.handle = open(filename)
        self.lines = self.handle.readlines()
        self.linenumber = -1

    def __iter__(self):
        return self

    def __next__(self):
        self.linenumber += 1
        try:
            return self.lines[self.linenumber]
        except IndexError:
            self.handle.close()
            raise StopIteration


for line in FileReader("test.txt"):
    print(line, end="")

print("done!")
