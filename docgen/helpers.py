import re

KEYWORDS = [
    "asm",
    "else",
    "new",
    "this",
    "auto",
    "enum",
    "throw",
    "bool",
    "explicit",
    "private",
    "true",
    "break",
    "export",
    "protected",
    "try",
    "case",
    "extern",
    "public",
    "typedef",
    "catch",
    "false",
    "register",
    "typeid",
    "char",
    "float",
    "reinterpret_cast",
    "typename",
    "class",
    "for",
    "return",
    "union",
    "const",
    "friend",
    "short",
    "unsigned",
    "const_cast",
    "goto",
    "signed",
    "using",
    "continue",
    "if",
    "sizeof",
    "virtual",
    "default",
    "inline",
    "static",
    "void",
    "delete",
    "int",
    "static_cast",
    "volatile",
    "do",
    "long",
    "struct",
    "wchar_t",
    "double",
    "mutable",
    "switch",
    "while",
    "dynamic_cast",
    "namespace",
    "template"
]


class Helper:
    """Class with tiny parsing helper methods."""

    @staticmethod
    def is_valid_identifier(lexeme=str()) -> bool:
        lexeme = lexeme.strip()

        if not lexeme.strip():
            return False

        if lexeme.startswith("operator"):
            return True

        is_valid_start = re.match("[a-zA-Z_~]", lexeme[0])

        if len(lexeme) <= 1:
            return is_valid_start

        is_valid_name = all([re.match("[a-zA-Z0-9_]", x) for x in lexeme[1:]])
        is_keyword = lexeme in KEYWORDS

        return bool(is_valid_start and is_valid_name and not is_keyword)

    @staticmethod
    def is_valid_type(lexeme=str()) -> bool:
        lexeme = lexeme.strip()

        if not lexeme.strip():
            return False

        is_valid_start = re.match("[a-zA-Z_~]", lexeme[0])

        if len(lexeme) <= 1:
            return is_valid_start

        is_valid_name = all([re.match("[a-zA-Z0-9_]", x) for x in lexeme[1:]])

        return bool(is_valid_start and is_valid_name)

    @staticmethod
    def find_body(snippet) -> str:
        stack = list()
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
    def clean_up_comments(snippet):
        snippet = re.sub(r'/\*[^*/]+\*/', '', snippet)
        snippet = re.sub(r'/{2,}.*\n', '', snippet)

        return snippet

    @staticmethod
    def htmlize(snippet):
        return snippet.replace("<", "&lt").replace(">", "&gt")

    @staticmethod
    def has_comment_entry(snippet):
        return bool(re.search(r'(\*/|/\*|/{2,})', snippet))
