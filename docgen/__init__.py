import os
from docgen import cpp

from jinja2 import Environment, FileSystemLoader

j2_env = Environment(
    loader=FileSystemLoader("templates"),
    trim_blocks=True
)


class DocumentGenerator:
    def get_file_content(self):
        with open(self.path, "r") as file:
            content = file.read()

        return content

    def generate(self):
        parser = cpp.BodyParser(self.get_file_content(), self.path)
        parser.parse()

        self.classes = parser.get_classes()
        self.functions = parser.get_functions()
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

    def __init__(self, path, output):
        self.path = path
        self.output = output

        self.classes = []
        self.functions = []
