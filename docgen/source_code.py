import os


class SourceCodeModule:
    def __init__(self, path):
        self.name = os.path.basename(path)
        self.path = "./" + os.path.splitext(self.name)[0] + "/index.html"


class SourceCodeFile:
    def __init__(self, path):
        self.name = os.path.basename(path)
        self.path = "./" + os.path.splitext(self.name)[0] + "/index.html"
