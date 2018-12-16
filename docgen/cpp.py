import re
import os

from docgen.function import Function
from docgen.helpers import Helper

class Class:
    """C++ class/structure representation."""

    def __init__(self, name, path, line, body=None):
        self.name = name
        self.path = os.path.basename(path)
        self.line = line
        self.body = body

        self.__classes = list()
        self.__methods = list()

        if body:
            try:
                parser = BodyParser(self.body, self.path, self.name)
                parser.parse()
            except Exception as error:
                pass
                # print(colored(error, 'red'))

            self.__methods = parser.functions
            self.__classes = parser.classes

    def __lt__(self, other):
        return self.name > other.name

    @property
    def classes(self):
        return self.__classes

    @property
    def methods(self):
        return self.__methods

class BodyParser:
    def __init__(self, snippet, path, class_name=None):
        self.stack = list()

        self.__methods = list()
        self.__comments = list()
        self.__classes = list()
        self.__includes = list()

        self.index = int()
        self.line = int()
        self.number = int()
        self.start_line = int()

        self.body = str()
        self.comment = str()

        self.snippet = snippet
        self.class_name = class_name

        self.is_clang_comment = False
        self.is_cpp_comment = False
        self.is_function = False

        self.path = os.path.normpath(path)

    @property
    def current_text(self) -> str:
        return self.snippet[self.index:]

    @property
    def current_symbol(self) -> str:
        return self.snippet[self.index]

    @property
    def is_new_line(self) -> bool:
        return self.current_symbol == os.linesep

    def is_constructor(self, method_name):
        return self.class_name is not None and self.class_name == method_name

    @property
    def includes(self) -> list:
        return self.__includes[:]

    @property
    def functions(self) -> list:
        functions = self.__methods[:]

        if len(self.__classes) > 0:
            for cpp_class in self.__classes:
                if len(cpp_class.methods) > 0:
                    functions.extend(cpp_class.methods)

        return functions

    @property
    def classes(self) -> list:
        classes = self.__classes[:]

        if len(self.__classes) > 0:
            for cpp_class in self.__classes:
                if len(cpp_class.classes) > 0:
                    classes.extend(cpp_class.classes)

        return classes

    def process_template(self):
        index = int()

        after_template = self.snippet[self.index:].strip()
        while after_template[index] is not ">":
            index += 1

        self.index += index + 2

    def process_struct(self):
        after_struct = self.snippet[self.index + len("struct"):].strip()

        struct_name = after_struct.split()[0]

        # Avoid class names with characters, like "Example{" or "Example;".
        if struct_name[-1] == "{" or struct_name[-1] == ";" or struct_name[-1] == ":" or struct_name[-1] == "(":
            struct_name = struct_name[:-1]

        possible_struct_body = self.snippet[self.index + 7 + len(struct_name):]

        self.index += 7 + len(struct_name) + 1

        for i, ch in enumerate(possible_struct_body):
            self.index += 1
            if ch == os.linesep:
                self.line += 1
            elif ch == "{":
                class_body = Helper.find_body(possible_struct_body[i:])
                self.index += len(class_body)
                self.line += len(class_body.split(os.linesep))
                cpp_class = Class(struct_name, self.path, self.line, class_body)
                break
            elif ch == ">" or ch == ";":
                cpp_class = Class(struct_name, self.path, self.line)
                break

        self.__classes.append(cpp_class)

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
            if ch == os.linesep:
                self.line += 1
            elif ch == "{":
                class_body = Helper.find_body(possible_class_body[i:])
                self.index += len(class_body)
                self.line += len(class_body.split(os.linesep))
                cpp_class = Class(class_name, self.path, self.line, class_body)
                break
            elif ch == ">" or ch == ";":
                cpp_class = Class(class_name, self.path, self.line)
                break

        self.__classes.append(cpp_class)

    def process_macros(self):
        leftovers = self.current_text
        index = 0

        while index < len(leftovers) - 2:
            if leftovers[index:index + 2] == "\\\n":
                index += len("\\\n")
                self.line += 1
            elif leftovers[index:index + 1] == os.linesep:
                index += len(os.linesep)
                self.line += 1
                break
            else:
                index += 1

        self.index += index

    def process_include(self):
        start = self.index
        is_started = False

        self.index += len("#include")

        # to_be_processed = self.current_text

        while self.index < len(self.snippet):
            if self.current_symbol == ">":
                self.__includes.append(Helper.htmlize(self.snippet[start:self.index + 1]))
                break
            elif self.current_symbol == "\"" and is_started:
                self.__includes.append(self.snippet[start:self.index + 1])
                break
            elif self.current_symbol == "\"":
                is_started = True

            self.index += 1



        # for ch in self.snippet[start:]:
        #     self.index += 1
        #
        #     if ch == ">":
        #         self.__includes.append(Helper.htmlize(self.snippet[start:self.index]))
        #         break
        #     elif ch == "\"" and is_started:
        #         self.__includes.append(self.snippet[start:self.index])
        #         break
        #     elif ch == "\"":
        #         is_started = True

    def parse(self):
        while self.index < len(self.snippet):
            # Comments.

            if self.current_text.startswith("/*"):
                self.comment = str()
                self.is_clang_comment = True
                self.index += len("/*")
                continue

            if self.current_text.startswith("*/"):
                self.__comments.append(self.comment)
                self.comment = str()
                self.is_clang_comment = False
                self.index += len("*/")
                continue

            if self.is_clang_comment:
                if self.snippet[self.index] == os.linesep:
                    self.line += 1
                    self.comment += "<br>"
                self.comment += self.current_symbol
                self.index += len(os.linesep)
                continue

            # Comment.

            # Skip and count newlines.
            if self.is_new_line and self.is_cpp_comment:
                self.line += 1
                self.index += 1
                self.is_cpp_comment = False
                self.__comments.append(self.comment)
                continue

            # Just read the comment.
            if self.is_cpp_comment:
                self.comment += self.current_symbol
                self.index += 1
                continue

            if self.current_text.startswith("///"):
                self.comment = str()
                self.is_cpp_comment = True
                self.index += 3
                continue

            if self.current_text.startswith("//"):
                self.comment = str()
                self.is_cpp_comment = True
                self.index += 2
                continue

            # Templates.
            if self.current_text.startswith("template"):
                self.index += 8
                self.process_template()

            # Macros.
            if self.current_text.startswith("#define"):
                self.index += 6
                self.process_macros()
                continue

            # Includes.
            if self.current_text.startswith("#include"):
                self.process_include()
                continue

            # Struct.
            if self.current_text.startswith("struct"):
                self.process_struct()
                continue

            # Class.
            if self.current_text.startswith("class"):
                self.process_class()
                continue

            # Function.

            self.body += self.current_symbol

            # Skip and count newlines.
            if self.is_new_line:
                self.line += 1
                self.index += 1
                continue

            if self.current_symbol == "(":

                if len(self.stack) == 0:
                    lexemes = re.split("\s", self.body)

                    method_name = lexemes[-1]
                    method_type = lexemes[-2]

                    self.start_line = self.line

                    if self.class_name is None and self.is_constructor(method_name[:-1]):
                        self.body = method_name
                    else:
                        if method_type or re.match(r"(.*)::~?(\1)", method_name):
                            self.body = method_type + " " + method_name
                        else:
                            self.index += 1

                self.stack.append(self.current_symbol)
            elif self.current_symbol == ")":
                if len(self.stack) == 0:
                    self.index += 1
                    continue

                self.stack.pop()

                if len(self.stack) == 0:
                    for ch in self.snippet[self.index + 1:]:
                        self.index += 1
                        if ch == os.linesep:
                            self.line += 1
                        elif ch == "{":
                            method = Function(self.body.strip(), self.path, self.line, self.class_name)
                            #
                            prev_line = self.snippet.split(os.linesep)[self.start_line - 1]
                            has_comment = Helper.has_comment_entry(prev_line.strip())
                            if has_comment:
                                method.comment = self.__comments[-1]
                            #
                            self.__methods.append(method)
                            #
                            self.body = ""

                            # Skip function body. Count index and line.
                            function_body = self.snippet[self.index:]
                            to_skip = Helper.find_body(function_body)
                            to_skip_chars = len(to_skip)
                            to_skip_lines = len(to_skip.split(os.linesep))
                            self.index += to_skip_chars
                            self.line += to_skip_lines
                            break
                        elif ch == ";" or ch == "}" or ch == "#":
                            self.body = ""
                            break
            self.index += 1
