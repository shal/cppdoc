import os
import datetime

from docgen.base_generator import BaseGenerator
from docgen.module_document_generator import ModuleDocumentGenerator
from docgen.cppdoc import CppDoc
from docgen.source_code import SourceCodeModule


class ProjectDocumentGenerator(BaseGenerator):
    """HTML documentation generator for folder with folders with .cpp files"""

    def __init__(self, output, project):
        super(ProjectDocumentGenerator, self).__init__()
        
        self.document_generators = list()
        self.cpp_files = list()
        self.modules = list()

        self.output_dir = os.path.normpath(output)
        self.project_dir_path = os.path.normpath(project)

    def generate(self):
        self.modules = list(map(lambda x: os.path.join(self.project_dir_path, x), os.listdir(self.project_dir_path)))
        self.modules = list(filter(lambda x: os.path.isdir(x), self.modules))

        for module_path in self.modules:
            output_path_dir = self.output_dir + "/" + os.path.basename(module_path)

            if not os.path.exists(output_path_dir):
                os.makedirs(output_path_dir)

            gen = ModuleDocumentGenerator(output_path_dir, module_path)
            gen.generate()

        self.generate_index()

    def generate_index(self):
        self.modules = list(map(lambda m: SourceCodeModule(m), self.modules))

        index_html = self.j2_env.get_template("project.html").render({
            "modules": self.modules,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": CppDoc.VERSION,
            "project": os.path.basename(os.path.dirname(self.project_dir_path + "/") + "/")
        })

        with open(self.output_dir + "/index.html", "w") as f:
            f.write(index_html)
