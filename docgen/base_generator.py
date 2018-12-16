from jinja2 import Environment, FileSystemLoader


class BaseGenerator:
    """Base Class for html document generation"""
    def __init__(self):
        self.j2_env = Environment(
            loader=FileSystemLoader("templates"),
            trim_blocks=True
        )
