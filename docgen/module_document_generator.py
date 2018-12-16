import glob
import os
import datetime

from docgen.document_generator import DocumentGenerator
from docgen.source_code import SourceCodeFile
from docgen.base_generator import BaseGenerator
from docgen.cppdoc import CppDoc


class ModuleDocumentGenerator(BaseGenerator):
    """Html documentation generator for folders with .cpp files"""
    def __init__(self, output, module):
        super(ModuleDocumentGenerator, self).__init__()

        self.document_generators = list()
        self.cpp_files = list()

        self.output_dir = os.path.normpath(output)
        self.module_dir_path = os.path.normpath(module)

    def generate(self):
        self.cpp_files = sorted(glob.glob(self.module_dir_path + "/*.cpp"))

        for cpp_file in self.cpp_files:
            output_path_dir = self.output_dir + "/" + os.path.splitext(os.path.basename(cpp_file))[0]
            gen = DocumentGenerator(output_path_dir, cpp_file)
            gen.generate()

        self.generate_index()

    def generate_index(self):
        files = list(map(lambda file: SourceCodeFile(file), self.cpp_files))

        index_html = self.j2_env.get_template("module.html").render({
            "files": files,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": CppDoc.VERSION,
            "module": os.path.basename(os.path.dirname(self.module_dir_path + "/") + "/")
        })

        with open(self.output_dir + "/index.html", "w") as f:
            f.write(index_html)
