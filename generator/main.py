from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


class DocGenerator():
    def generate(self):
        print(self.path)

    def __init__(self, path):
        self.path = path
        print(path)


