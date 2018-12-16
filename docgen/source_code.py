import os

class SourceCode:
    def __init__(self, path):
        self.name = os.path.basename(path)
        self.path = "./" + os.path.splitext(self.name)[0] + "/index.html"

# Wrapper for File.
class SourceCodeFile(SourceCode):
    pass

# Wrapper for Module.
class SourceCodeModule(SourceCode):
    pass
