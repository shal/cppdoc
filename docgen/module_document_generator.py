import glob
import os
import datetime

from docgen.document_generator import DocumentGenerator
from docgen.source_code import SourceCodeFile
from docgen.base_generator import BaseGenerator, path_normalizer
from docgen.cppdoc import CppDoc

class EmptyModuleException(Exception):
    def __init__(self):
        super(EmptyModuleException, self).__init__("This module does not contain .cpp files")

class ModuleDocumentGenerator(BaseGenerator):
    """HTML documentation generator for directories with .cpp files"""

    @path_normalizer
    def __init__(self, output, path):
        super(ModuleDocumentGenerator, self).__init__()

        self.output_path = output
        self.path = path

        self.__files = sorted(glob.glob(self.path + "/*.cpp"))

    @property
    def base_path(self):
        return os.path.basename(self.path)

    @property
    def files_as_objects(self):
        return list(map(lambda file: SourceCodeFile(file), self.__files))

    def generate(self):
        if len(self.__files) == 0:
            raise EmptyModuleException

        for file in self.__files:
            output_path_dir = self.output_path + "/" + os.path.splitext(os.path.basename(file))[0]

            gen = DocumentGenerator(output_path_dir, file)

            try:
                gen.generate()
            except Exception as error:
                print(error)

        self.generate_index()

    def generate_index(self):
        index_html = self.j2_env.get_template("module.html").render({
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": CppDoc.VERSION,
            "module": self.base_path,
            "files": self.files_as_objects
        })

        with open(self.output_path + "/index.html", "w") as f:
            f.write(index_html)
