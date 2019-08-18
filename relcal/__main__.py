import click

from relcal.commands.parse import parse_drc


@click.group()
def program():
    pass


program.add_command(parse_drc)

if __name__ == '__main__':
    program()
