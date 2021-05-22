from CRIT.commands import Command
from CRIT.utils import Utils
from CRIT.validator import NumberValidator
from prompt_toolkit import prompt

class Harm(Command):

    keywords = ['harm', 'damage']
    help_text = '''{keyword}
{divider}
Summary: Decrement the characters current HP

Usage: {keyword} <int>

Examples:

    {keyword}
    {keyword} 4
'''

    def do_command(self, *args):
        if not args:
            harm_value = Utils.str2int(prompt('How much did you take? > ', 
                    validator=NumberValidator()
            ))

        else:
            try:
                harm_value = int(args[0])
                print(harm_value)

            except:
                self.console.print('please enter an int')
                return

        self.character.hp -= harm_value
        self.character.changed = True