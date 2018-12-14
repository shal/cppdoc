import re
import os

from docgen.function import Function
from docgen.helpers import Helper

from termcolor import colored

class Class:
    """C++ class/struct representation."""
    def __init__(self, name, path, line, body=None):
        self.name = name
        self.path = os.path.basename(path)
        self.line = line
        self.body = body

        self.methods = []
        self.classes = []

        if body:
            self.clean_html_body = body.replace("\n", "<br>")

            try:
                parser = BodyParser(self.body, self.path, self.name)
                parser.parse()
            except Exception as error:
                print(colored(error, 'red'))

            self.methods = parser.get_functions()
            self.classes = parser.get_classes()

    def __lt__(self, other):
        return self.name > other.name

    def get_classes(self):
        return self.classes


class BodyParser:
    def __init__(self, snippet, path, class_name=None):
        self.stack = []
        self.methods = []
        self.comments = []
        self.classes = []
        self.includes = []

        self.index = int()
        self.line = int()
        self.number = int()

        self.body = str()

        self.snippet = snippet
        self.class_name = class_name

        self.multi_line_comment_started = False
        self.single_line_comment_started = False
        self.comment = str()

        self.is_function = False

        self.path = path

        self.start_line = int()

    def process_template(self):
        index = int()

        after_template = self.snippet[self.index:].strip()
        while after_template[index] is not ">":
            index += 1

        self.index += index + 2

    def process_struct(self):
        after_struct = self.snippet[self.index + 6:].strip()

        struct_name = after_struct.split()[0]

        # Avoid class names with characters, like "Example{" or "Example;".
        if struct_name[-1] == "{" or struct_name[-1] == ";" or struct_name[-1] == ":" or struct_name[-1] == "(":
            struct_name = struct_name[:-1]

        possible_struct_body = self.snippet[self.index + 7 + len(struct_name):]

        self.index += 7 + len(struct_name) + 1

        for i, ch in enumerate(possible_struct_body):
            self.index += 1
            if ch == "\n":
                self.line += 1
            elif ch == "{":
                class_body = Helper.find_body(possible_struct_body[i:])
                self.index += len(class_body)
                self.line += len(class_body.split("\n"))
                cpp_class = Class(struct_name, self.path, self.line, class_body)
                break
            elif ch == ">" or ch == ";":
                cpp_class = Class(struct_name, self.path, self.line)
                break

        self.classes.append(cpp_class)

    def process_class(self):
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

    def process_macros(self):
        leftovers = self.snippet[self.index:]
        index = 0

        while index < len(leftovers) - 2:
            if leftovers[index:index + 2] == "\\\n":
                index += 2
                self.line += 1
            elif leftovers[index:index + 1] == "\n":
                index += 1
                self.line += 1
                break
            else:
                index += 1

        self.index += index

    def parse(self):
        while self.index < len(self.snippet):
            # Comments.

            if self.snippet[self.index:self.index + 2] == "/*":
                self.comment = ""
                self.multi_line_comment_started = True
                self.index += 2
                continue

            if self.snippet[self.index:self.index + 2] == "*/":
                self.comments.append(self.comment)
                self.multi_line_comment_started = False
                self.index += 2
                self.comment = ""
                continue

            if self.multi_line_comment_started:
                if self.snippet[self.index] == "\n":
                    self.line += 1
                    self.comment += "<br>"
                self.comment += self.snippet[self.index]
                self.index += 1
                continue

            # Comment.

            # Skip and count newlines.
            if self.snippet[self.index] == "\n" and self.single_line_comment_started:
                self.line += 1
                self.index += 1
                self.single_line_comment_started = False
                self.comments.append(self.comment)
                continue

            # Just read the comment.
            if self.single_line_comment_started:
                self.comment += self.snippet[self.index]
                self.index += 1
                continue

            if self.snippet[self.index:self.index + 3] == "///":
                self.comment = ""
                self.single_line_comment_started = True
                self.index += 3
                continue

            if self.snippet[self.index:self.index + 2] == "//":
                self.comment = ""
                self.single_line_comment_started = True
                self.index += 2
                continue

            # Templates.
            if self.snippet[self.index:self.index + 8] == "template":
                self.index += 8
                self.process_template()

            # Macros.
            # print(self.snippet[self.index:self.index + 7])
            if self.snippet[self.index:self.index + 7] == "#define":
                self.index += 6
                self.process_macros()

            # Includes.
            # Find all "include" directives for source code file.
            if self.snippet[self.index:self.index + 8] == "#include":
                start = self.index
                self.index += 8
                is_started = False
                for ch in self.snippet[self.index:]:
                    self.index += 1
                    if ch == ">":
                        tmp = self.snippet[start:self.index].replace('<', '&lt').replace('>', '&gt')
                        self.includes.append(tmp)
                        break
                    elif ch == "\"" and is_started:
                        self.includes.append(self.snippet[start:self.index])
                        break
                    elif ch == "\"":
                        is_started = True

            # Struct.

            if Helper.is_struct(self.snippet[self.index:self.index + 6]):
                self.process_struct()
                continue

            # Class.

            if Helper.is_class(self.snippet[self.index:self.index + 5]):
                self.process_class()
                continue

            # Function.

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

                    if self.class_name is None and Helper.is_constructor(method_name[:-1], self.class_name):
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
