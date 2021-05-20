from CRIT.enums import Enums
import sys

from prompt_toolkit.completion.word_completer import WordCompleter

from CRIT.commands import Command
from CRIT.utils import Utils
from prompt_toolkit import prompt
from CRIT.validator import WordValidator


class Exit(Command):

    keywords = ['exit', 'quit',]
    help_text = '''{keyword}
{divider}
Summary: Cleanly exit the app after a prompt

Usage: {keyword}

Examples:

    {keyword} 
'''

    def do_command(self, *args):
        if Utils.str2bool(prompt('Are you sure you want to quit > ', completer=WordCompleter(Enums.bool_choices), validator=WordValidator(Enums.bool_choices))):
            sys.exit(0)
