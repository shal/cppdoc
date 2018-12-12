import os
import re
from glob import glob

class Function:
    def __init__(self, query, path, line, class_name=None, comment=None):
        self.comment = comment
        self.path = os.path.basename(path)

        parts = query.split("(", 1) # 1 - Max split.

        type_name = parts[0].split()

        if len(type_name) == 2:
            self.return_type = type_name[0]

            # Avoid issue with '<', '>'.
            self.html_return_type = self.return_type.replace("<", "&lt")
            self.html_return_type = self.html_return_type.replace(">", "&gt")

            self.name = type_name[1]
            self.type = "Method" if class_name else "Function"
            self.full_name = type_name[1]

            if class_name:
                self.full_name = class_name + "::" + type_name[1]
                self.path = os.path.basename(path) + ":" + class_name

        elif len(type_name) == 1:
            self.name = type_name[0]
            self.return_type = None
            self.type = "Constructor"
            self.full_name = type_name[0]

            if class_name:
                self.full_name = class_name + "::" + type_name[0]
                self.path = os.path.basename(path) + ":" + class_name

        self.params = " ".join(parts[1:])[0:-1]

        self.is_operator = self.name.startswith("operator")

        self.line = line

    def __lt__(self, other):
        return self.name < other.name

    def set_comment(self, comment):
        self.comment = comment

class Class:
    def __init__(self, name, path, line, body=None):
        self.name = name
        self.path = os.path.basename(path)
        self.line = line
        self.body = body

        self.methods = []
        self.classes = []

        if body:
            self.clean_html_body = body.replace("\n", "<br>")

            parser = BodyParser(self.body, self.path, self.name)
            parser.parse()

            self.methods = parser.get_functions()
            self.classes = parser.get_classes()

    def __lt__(self, other):
         return self.name > other.name

    def get_classes(self):
        return self.classes

class SourceCodeModule:
    def __init__(self, path):
        self.name = os.path.basename(path)
        self.path = "./" + os.path.splitext(self.name)[0] + "/index.html"

class SourceCodeFile:
    def __init__(self, path):
        self.name = os.path.basename(path)
        self.path = "./" + os.path.splitext(self.name)[0] + "/index.html"

class Helper:
    @staticmethod
    def is_constructor(method_name, class_name):
        return method_name == class_name

    @staticmethod
    def is_class(lexeme):
        return (lexeme == "class" or lexeme == "struct")

    @staticmethod
    def find_body(snippet):
        stack = []
        body = ""
        for ch in snippet:
            body += ch
            if ch == "{":
                stack.append(ch)
            elif ch == "}" and stack[-1] == "{":
                stack.pop()
                if len(stack) == 0:
                    return body

        return ValueError("Snippet doesn't exit class body.")

    @staticmethod
    def clean_up_from_comments(snippet):
        snippet = re.sub(r'/\*[^\*/]+\*/', '', snippet)
        snippet = re.sub(r'/{2,}.*\n', '', snippet)

        return snippet

    @staticmethod
    def has_comment_entry(snippet):
        return bool(re.search(r'(\*/|\/\*|/{2,})', snippet))

    @staticmethod
    def get_cpp_files(path):
        files = glob(os.path.join(path, '*.cpp'))
        return files

class BodyParser:
    def __init__(self, snippet, path, class_name=None):
        self.stack = []
        self.methods = []
        self.comments = []
        self.classes = []
        self.includes = []

        self.index = 0
        self.line = 0
        self.number = 0

        self.body = ""

        self.snippet = snippet
        self.class_name = class_name

        self.multiLineCommentStarted = False
        self.singleLineCommentStarted = False
        self.comment = ""

        self.isFunction = False

        self.path = path

    def parse(self):
        while self.index < len(self.snippet):
            ####################################### Comments.

            if self.snippet[self.index:self.index + 2] == "/*":
                self.comment = ""
                self.multiLineCommentStarted = True
                self.index += 2
                continue

            if self.snippet[self.index:self.index + 2] == "*/":
                self.comments.append(self.comment)
                self.multiLineCommentStarted = False
                self.index += 2
                self.comment = ""
                continue

            if self.multiLineCommentStarted:
                if self.snippet[self.index] == "\n":
                    self.line += 1
                    self.comment += "<br>"
                self.comment += self.snippet[self.index]
                self.index += 1
                continue

            ####################################### Comment.

            # Skip and count newlines.
            if self.snippet[self.index] == "\n" and self.singleLineCommentStarted:
                self.line += 1
                self.index += 1
                self.singleLineCommentStarted = False
                self.comments.append(self.comment)
                continue

            # Just read the comment.
            if self.singleLineCommentStarted:
                self.comment += self.snippet[self.index]
                self.index += 1
                continue

            if self.snippet[self.index:self.index + 3] == "///":
                self.comment = ""
                self.singleLineCommentStarted = True
                self.index += 3
                continue

            if self.snippet[self.index:self.index + 2] == "//":
                self.comment = ""
                self.singleLineCommentStarted = True
                self.index += 2
                continue

            ####################################### Includes.
            # Find all "include" directives for source code file.
            if self.snippet[self.index:self.index + 8] == "#include":
                start = self.index
                self.index += 8
                isStarted = False
                for ch in self.snippet[self.index:]:
                    if ch == ">":
                        self.includes.append(self.snippet[start:self.index + 1])
                        break
                    elif ch == "\"" and isStarted:
                        self.includes.append(self.snippet[start:self.index + 1])
                        break
                    elif ch == "\"":
                        isStarted = True
                    self.index += 1

            ####################################### Class.

            if Helper.is_class(self.snippet[self.index:self.index + 5]):
                after_class = self.snippet[self.index + 5:].strip()

                class_name = after_class.split()[0]

                # Avoid class names with characters, like "Example{" or "Example;".
                if class_name[-1] == "{" or class_name[-1] == ";" or class_name[-1] == ":" or class_name[-1] == "(":
                    class_name = class_name[:-1]

                possible_class_body = self.snippet[self.index + 6 + len(class_name):]

                self.index += 6 + len(class_name) + 1

                for i, ch in enumerate(possible_class_body):
                    self.index += 1
                    if ch == "\n":
                        self.line += 1
                    elif ch == "{":
                        class_body = Helper.find_body(possible_class_body[i:])
                        self.index += len(class_body)
                        self.line += len(class_body.split("\n"))
                        cpp_class = Class(class_name, self.path, self.line, class_body)
                        break
                    elif ch == ">" or ch == ";":
                        cpp_class = Class(class_name, self.path, self.line)
                        break

                self.classes.append(cpp_class)
                continue

            ####################################### Function.

            self.body += self.snippet[self.index]

            # Skip and count newlines.
            if self.snippet[self.index] == "\n":
                self.line += 1
            elif self.snippet[self.index] == "(":

                if len(self.stack) == 0:
                    lexemes = re.split("\s", self.body)

                    method_name = lexemes[-1]
                    method_type = lexemes[-2]

                    self.start_line = self.line

                    if self.class_name != None and Helper.is_constructor(method_name[:-1], self.class_name):
                        self.body = method_name
                    else:
                        if method_type or re.match(r"(.*)::~?(\1)", method_name):
                            self.body = method_type + " " + method_name
                        else:
                            self.index += 1

                self.stack.append(self.snippet[self.index])
            elif self.snippet[self.index] == ")":
                if len(self.stack) == 0:
                    self.index += 1
                    continue

                self.stack.pop()

                if len(self.stack) == 0:
                    for ch in self.snippet[self.index + 1:]:
                        self.index += 1
                        if ch == "\n":
                            self.line += 1
                        elif ch == "{":
                            method = Function(self.body.strip(), self.path, self.line, class_name=self.class_name)
                            #
                            prev_line = self.snippet.split("\n")[self.start_line - 1]
                            has_comment = Helper.has_comment_entry(prev_line.strip())
                            if has_comment: method.set_comment(self.comments[-1])
                            #
                            self.methods.append(method)
                            #
                            self.body = ""

                            # Skip function body. Count index and line.
                            function_body = self.snippet[self.index:]
                            to_skip = Helper.find_body(function_body)
                            to_skip_chars = len(to_skip)
                            to_skip_lines = len(to_skip.split("\n"))
                            self.index += to_skip_chars
                            self.line += to_skip_lines
                            break
                        elif ch == ";" or ch == "}" or ch == "#":
                            self.body = ""
                            break
            self.index += 1

    def get_includes(self):
        includes = self.includes[:]

        return includes

    def get_functions(self):
        functions = self.methods[:]

        if len(self.classes) > 0:
            for cpp_class in self.classes:
                if len(cpp_class.methods) > 0:
                    functions.extend(cpp_class.methods)

        return functions

    def get_classes(self):
        classes = self.classes[:]

        if len(self.classes) > 0:
            for cpp_class in self.classes:
                if len(cpp_class.classes) > 0:
                    classes.extend(cpp_class.classes)

        return classes
