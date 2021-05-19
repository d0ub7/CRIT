from CRIT.commands import Command
from CRIT.utils import Utils
from CRIT.json_parser import JsonParser
from prompt_toolkit import prompt


class Save(Command):

    keywords = ['save']
    help_text = '''{keyword}
{divider}
Summary: Save to json

Usage: {keyword}
'''

    def do_command(self, *args):
        if Utils.str2bool(prompt('Are you sure you want to save and quit? > ')):
            JsonParser.save_character(self.character)
            self.console.print(f'[bold green] UPDATED {self.character.name} [/bold green]')
