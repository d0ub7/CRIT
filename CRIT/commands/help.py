from CRIT.commands import Command
from CRIT.commands.list import List


class Help(Command):

    keywords = ['help']
    help_text = '''{keyword}
{divider}
Summary: Get help for a command.

Usage: {keyword} <command>
'''

    def get_suggestions(self, words):
        return list(sorted(self.character.commands.keys()))

    def do_command(self, *args):
        if not args:
            self.show_help_text('help')
            return

        keyword = args[0]
        command = self.character.commands.get(keyword)
        if not command:
            print(f'Unknown command: {keyword}')
            return
        command.show_help_text(keyword)

    def show_help_text(self, keyword):
        super().show_help_text(keyword)
        List.do_command(self, *[])