import os
import datetime
import glob

from docgen.base_generator import BaseGenerator, path_normalizer
from docgen.module_document_generator import ModuleDocumentGenerator, EmptyModuleException
from docgen.cppdoc import CppDoc
from docgen.source_code import SourceCodeModule


class ProjectDocumentGenerator(BaseGenerator):
    """HTML documentation generator for directory with modules"""

    @path_normalizer
    def __init__(self, output, path):
        super(ProjectDocumentGenerator, self).__init__()

        self.output_path = output
        self.path = path

        modules = list(map(lambda x: os.path.join(self.path, x), os.listdir(self.path)))
        self.__modules = list(filter(lambda x: os.path.isdir(x), modules))

    @property
    def modules_with_cpp_files(self) -> list:
        return list(
            filter(
                lambda m: len(glob.glob(m + "/*.cpp")) != 0, self.__modules
            )
        )

    @property
    def base_path(self):
        return os.path.basename(self.path)

    @property
    def modules_as_objects(self) -> list:
        return list(map(lambda m: SourceCodeModule(m), self.modules_with_cpp_files))

    def generate(self):
        for module_path in self.modules_with_cpp_files:
            output_path_dir = self.output_path + "/" + os.path.basename(module_path)

            if not os.path.exists(output_path_dir):
                os.makedirs(output_path_dir)

            try:
                gen = ModuleDocumentGenerator(output_path_dir, module_path)
                gen.generate()
            except EmptyModuleException as error:
                print(error)

        self.generate_index()

    def generate_index(self):
        index_html = self.j2_env.get_template("project.html").render({
            "modules": self.modules_as_objects,
            "project": self.base_path,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": CppDoc.VERSION
        })

        with open(self.output_path + "/index.html", "w") as f:
            f.write(index_html)
