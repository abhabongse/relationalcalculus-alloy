"""
Collection of Python primitive helper functions, classes, etc.
"""


class Singleton(type):
    """
    This Singleton metaclass can be used to transform an associated class
    (whose constructor accepts zero input arguments) into a singleton class.
    """
    instance = None

    def __call__(cls):
        if cls.instance is None:
            cls.instance = super().__call__()
        return cls.instance
