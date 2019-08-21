import sys

import click

from relcal.syntax.drc import DRCQueryLanguage


@click.command()
@click.argument(
    'input_file', type=click.Path(exists=True, dir_okay=False, allow_dash=True),
)
def parse_drc(input_file):
    """
    Parse the given INPUT_FILE containing Domain Relational Calculus (DRC) syntax
    (or use '-' to use standard input).
    """
    if input_file == '-':
        content = sys.stdin.read()
    else:
        with open(input_file) as fobj:
            content = fobj.read()
    tree = DRCQueryLanguage().parser.parse(content)
    print(tree.pretty())
