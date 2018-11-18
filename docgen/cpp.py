class Function:
    def __init__(self, name, row, file, params, return_type):
        self.name = name
        self.row = row
        self.file = file
        self.params = params
        self.return_type = return_type

    def get_description(self):
        return self.return_type + " " + self.name


class Class:
    def __init__(self, name, file, row):
        self.name = name
        self.file = file
        self.row = row

    def print(self):
        print(
            "File " + self.file + "\n",
            "Name " + self.name + "\n",
            "Row " + str(self.row) + "\n"
        )

def is_class(lexeme):
    return lexeme == 'class'