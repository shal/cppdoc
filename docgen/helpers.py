import re
import os

from glob import glob


class Helper:
    """Class with tiny parsing helper methods."""

    @staticmethod
    def is_constructor(method_name, class_name):
        return method_name == class_name

    @staticmethod
    def is_class(lexeme):
        return lexeme == "class"

    @staticmethod
    def is_struct(lexeme):
        return lexeme == "struct"

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
