from CRIT.yaml_parser import YamlParser
from CRIT.enums import Enums
from prompt_toolkit.completion.word_completer import WordCompleter
from CRIT.validator import WordValidator
from CRIT.commands import Command
from CRIT.utils import Utils
from prompt_toolkit import prompt



class Save(Command):

    keywords = ['save']
    help_text = '''{keyword}
{divider}
Summary: Save to yaml

Usage: {keyword}
'''

    def do_command(self, *args):
        if Utils.str2bool(prompt('Are you sure you want to save and quit? > ', 
                completer=WordCompleter(Enums.bool_choices), 
                validator=WordValidator(Enums.bool_choices)
        )):

            YamlParser.save_character(self.character)
            self.console.print(f'[bold green] UPDATED {self.character.name} [/bold green]')
