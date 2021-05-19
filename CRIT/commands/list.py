from CRIT.commands import Command


class List(Command):

    keywords = ['commands']
    help_text = '''{keyword}
{divider}
Summary: List available commands

Usage: {keyword}
'''

    def do_command(self, *args):
        self.print('<x>Available commands:</x>\n')
        for keyword in list(sorted(self.character.commands.keys())):
            print('*', keyword)