import sys

from CRIT.commands import Command
from CRIT.utils import Utils
from prompt_toolkit import prompt


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
        if Utils.str2bool(prompt('Are you sure you want to quit > ')):
            sys.exit(0)
