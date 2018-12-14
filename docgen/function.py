import os


class Function:
    """C++ function representation."""

    def __init__(self, query, path, line, class_name=None, comment=None):
        self.comment = comment
        self.path = os.path.basename(path)

        parts = query.split("(", 1)  # 1 - Max split.

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
