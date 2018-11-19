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
    def __init__(self, name, file, row, body=None):
        self.name = name
        self.file = file
        self.row = row
        self.body = body

    def __str__(self):
        return "File " + self.file + "\nName " + self.name + "\nRow " + str(self.row) + "\n"


def is_class(lexeme):
    return lexeme == "class"


def find_body(snippet):
    stack = []
    body = ""
    for ch in snippet:
        body += ch
        if ch == "{":
            stack.append(ch)
        elif ch == "}" and stack[-1] == '{':
            stack.pop()
            if len(stack) == 0:
                return body

    return ValueError("Snippet doesn't exit class body.")
