"""Language collection package containing abstract syntax tress and
parsers for various languages.

For testing with ASDL parser, from project root run the following python code::

    import os
    from dbsyntax.asdl.parser import asdl_parser

    # Replace 'python.asdl' with other files as needed
    source_fname = os.path.join('dbsyntax', 'collections', 'python.asdl')
    with open(source_fname) as sf:
        tree = asdl_parser(sf)
    print(tree)

"""
