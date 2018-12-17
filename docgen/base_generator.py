from jinja2 import Environment, FileSystemLoader

import os


def path_normalizer(func):
    def wrapper(self, output, path):
        norm_output = os.path.normpath(output)
        norm_path = os.path.normpath(path)
        func(self, norm_output, norm_path)

    return wrapper


class BaseGenerator:
    """HTML documentation generator"""
    def __init__(self):
        self.j2_env = Environment(
            loader=FileSystemLoader("templates"),
            trim_blocks=True
        )
