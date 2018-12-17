import os
import re
import datetime

from docgen import cpp
from docgen.cppdoc import CppDoc
from docgen.base_generator import BaseGenerator


def strip(text):
    text = re.sub(r"\s*([>)])", r"\1", text)
    text = re.sub(r"([<(])\s*", r"\1", text)

    return text


class DocumentGenerator(BaseGenerator):
    def __init__(self, output, file_path):
        super(DocumentGenerator, self).__init__()

        self.output = os.path.normpath(output)
        self.file_path = os.path.normpath(file_path)

        self.classes = list()
        self.functions = list()
        self.includes = list()

    def generate(self):
        try:
            parser = cpp.BodyParser(self.file_content, self.file_path)
            parser.parse()

            self.classes = parser.classes
            self.functions = parser.functions
            self.includes = parser.includes

            self.generate_files()
        except Exception as error:
            # pass
            print(error)

    def generate_structure(self):
        if not os.path.exists(self.output):
            os.makedirs(self.output)
        if not os.path.exists(self.output + "/classes"):
            os.makedirs(self.output + "/classes")
        if not os.path.exists(self.output + "/functions"):
            os.makedirs(self.output + "/functions")

        index_html = self.j2_env.get_template("file.html").render({
            "classes": self.classes,
            "functions": self.functions,
            "includes": self.includes,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": CppDoc.VERSION
        })

        with open(self.output + "/index.html", "w") as file:
            file.write(index_html)

    def generate_classes(self):
        for cpp_class in self.classes:
            output = self.output + "/classes/" + cpp_class.name + ".html"

            template = self.j2_env.get_template("class.html")
            result = template.render(obj=cpp_class)

            with open(output, "w") as file:
                file.write(result)

    def generate_content(self):
        template = self.j2_env.get_template("content.html")

        result = template.render({
            "classes": sorted(self.classes),
            "functions": sorted(self.functions)
        })

        with open(self.output + "/content.html", "w") as f:
            f.write(result)

    def generate_functions(self):
        for cpp_func in self.functions:
            output = self.output + "/functions/" + cpp_func.full_name + ".html"

            template = self.j2_env.get_template("function.html")
            result = template.render(obj=cpp_func)

            with open(output, "w") as file:
                file.write(result)

    def generate_files(self):
        self.generate_structure()

        self.generate_classes()
        self.generate_functions()

        self.generate_content()

    @property
    def file_content(self):
        with open(self.file_path, "r") as file:
            content = file.read()

        return strip(content)
