import os
from docgen import cpp

from jinja2 import Environment, FileSystemLoader

j2_env = Environment(
    loader=FileSystemLoader('templates'),
    trim_blocks=True
)


class DocumentGenerator:
    def get_file_content(self):
        with open(self.path, 'r') as file:
            content = file.read()

        return content

    def generate(self):
        self.process_file()
        self.create_dir()

    def create_dir(self):
        if not os.path.exists(self.output):
            os.makedirs(self.output)

        index_html = j2_env.get_template('main.html').render(classes=self.classes)
        with open(self.output + "/index.html", 'w') as f:
            f.write(index_html)

        for cpp_class in self.classes:
            output = self.output + "/" + cpp_class.name + ".html"

            context = {
                "name": cpp_class.name,
            }

            template = j2_env.get_template('class.html')
            result = template.render(context)

            with open(output, 'w') as f:
                f.write(result)

    def process_file(self):
        content = self.get_file_content()
        lines = content.split('\n')

        for i, line in enumerate(lines):
            line = line.strip()
            lexemes = line.split()

            for j, lexeme in enumerate(lexemes):
                if cpp.is_class(lexeme):
                    name = lexemes[j+1]

                    if name[-1] == '{' or name[-1] == ';':
                        name = name[:-1]

                    after_lexeme = " ".join(lexemes[j+1:])

                    cpp_class = cpp.Class(name, self.path, i)
                    self.classes.append(cpp_class)
                    print(cpp_class)

                    # After class lexeme there are 3 possible cases.
                    # 1. { - class implementation.
                    # 2. ; -  class declaration.
                    # 3. nothing - we should go to process next line.

                    # Case 1,2
                    for ch in after_lexeme:
                        if ch == '{':
                            print('Class Body found.')
                            break
                        elif ch == ';':
                            print('Class declaration found.')
                            break

    def __init__(self, path, output):
        self.path = path
        self.output = output

        # Logic.
        self.classes = []
        self.function = []
        self.modules = []

