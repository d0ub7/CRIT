from CRIT.enums import Enums
from prompt_toolkit.completion.word_completer import WordCompleter
from CRIT.commands import Command
from CRIT.utils import Utils
from CRIT.validator import NumberValidator, WordValidator
from prompt_toolkit import prompt


class Heal(Command):

    keywords = ['heal']
    help_text = '''{keyword}
{divider}
Summary: Increment the characters current hp

Usage: {keyword} <Int>

Examples:

    {keyword} 
    {keyword} 5
'''

    def do_command(self, *args):
        if not args:
            heal_value = Utils.str2int(prompt('How much did you heal? > ', 
                    validator=NumberValidator()
            ))

        else:
            try:
                heal_value = int(args[0])

            except:
                self.console.print('please enter an int')
                return

        if((self.character.hp + heal_value) > self.character.max_hp):
            if not Utils.str2bool(prompt('Should this overheal beyond max hp? > ', 
                    completer=WordCompleter(Enums.bool_choices), 
                    validator=WordValidator(Enums.bool_choices)
            )):
                self.character.hp = self.character.max_hp

            else:
                self.character.hp += heal_value

        else:
            self.character.hp += heal_value

        self.character.changed = True