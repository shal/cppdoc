import os
import glob
import re
from jinja2 import Environment, FileSystemLoader

from docgen import cpp

j2_env = Environment(
    loader=FileSystemLoader("templates"),
    trim_blocks=True
)

def strip(text):
    text = re.sub(r"\s{0,}(>|\))", r"\1", text)
    text = re.sub(r"(<|\()\s{0,}", r"\1", text)

    return text

class DocumentGenerator:
    def get_file_content(self, path):
        with open(path, "r") as file:
            content = file.read()

        return strip(content)

    def generate(self):
        if self.filePath:
            path = os.path.normpath(self.filePath)
            parser = cpp.BodyParser(self.get_file_content(path), path)
            parser.parse()

            self.classes = parser.get_classes()
            self.functions = parser.get_functions()
            self.generate_files()
        elif self.modulePath:
            path = os.path.normpath(self.modulePath)
            paths = cpp.Helper.get_cpp_files(path)

            for path in paths:
                parser = cpp.BodyParser(self.get_file_content(path), path)
                parser.parse()
                self.classes.extend(parser.get_classes())
                self.functions.extend(parser.get_functions())

            self.generate_files()

    def generate_structure(self):
        if not os.path.exists(self.output):
            os.makedirs(self.output)
        if not os.path.exists(self.output + "/classes"):
            os.makedirs(self.output + "/classes")
        if not os.path.exists(self.output + "/functions"):
            os.makedirs(self.output + "/functions")

        index_html = j2_env.get_template("main.html").render(
            classes=self.classes,
            functions=self.functions
        )
        with open(self.output + "/index.html", "w") as f:
            f.write(index_html)

    def generate_classes(self):
        for cpp_class in self.classes:
            output = self.output + "/classes/" + cpp_class.name + ".html"

            template = j2_env.get_template("class.html")
            result = template.render(obj=cpp_class)

            with open(output, "w") as f:
                f.write(result)

    def generate_functions(self):
        for cpp_func in self.functions:
            output = self.output + "/functions/" + cpp_func.full_name + ".html"

            template = j2_env.get_template("function.html")
            result = template.render(obj=cpp_func)

            with open(output, "w") as f:
                f.write(result)

    def generate_files(self):
        self.generate_structure()
        self.generate_classes()
        self.generate_functions()

    def __init__(self, output, file=None, module=None, project=None):
        self.output = os.path.normpath(output)

        self.filePath = file
        self.modulePath = module
        self.projectPath = project

        self.classes = []
        self.functions = []
