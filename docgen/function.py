import os


class Comment(object):
    """C++ comment representation"""
    def __init__(self, comment=None):
        if comment is None:
            self.__comment = ""
        else:
            self.__comment = comment

    def __get__(self, instance, owner):
        return self.__comment

    def __set__(self, instance, value):
        self.__comment = value

    def __delete__(self, instance):
        del self.__comment


class Function:
    """C++ function representation"""

    comment = Comment()

    def __init__(self, query, path, line, class_name=None):
        self.__path = os.path.basename(path)

        self.line = line
        self.class_name = class_name

        parts = query.split("(", 1)  # 1 - Max split.
        type_name = parts[0].split()

        self.params = " ".join(parts[1:])[0:-1]

        if len(type_name) >= 2:
            self.return_type = type_name[0]
            self.name = type_name[1]
        elif len(type_name) == 1:
            self.return_type = None
            self.name = type_name[0]

    def __lt__(self, other):
        return self.name < other.name

    @property
    def is_operator(self) -> bool:
        return self.name.startswith("operator")

    @property
    def html_return_type(self):
        return self.return_type.replace("<", "&lt").replace(">", "&gt")

    @property
    def is_method(self):
        return self.class_name is not None

    @property
    def full_name(self):
        if self.is_method:
            return str(self.class_name) + "::" + self.name
        else:
            return self.name

    @property
    def is_constructor(self):
        return self.is_method and self.return_type is None

    @property
    def kind(self):
        if self.is_constructor:
            return "Constructor"
        elif self.is_method:
            return "Method"
        else:
            return "Function"

    @property
    def path(self):
        if self.is_method:
            return self.__path + ":" + self.class_name
        else:
            return self.__path


