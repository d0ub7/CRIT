from CRIT.commands import Command
from CRIT.utils import Utils
from CRIT.validator import NumberValidator

from prompt_toolkit import prompt


class Cast(Command):

    keywords = ['cast']
    help_text = '''{keyword}
{divider}
Summary: Cast a spell and decrement the level at which it was cast from

Usage: {keyword} <spell level>

Examples:

    {keyword} 1
    {keyword} 6
'''

    def do_command(self, *args):
        # Bail out if we can't cast spells
        if not self.character.spell_list:
            self.console.print('cant cast spells')
            return

        # Get list of spell levels we can cast
        spell_list = []
        for spell in self.character.spell_list:
            if spell.base != 0:
                spell_list.append(int(spell.level))

        min_level = min(spell_list)
        max_level = max(spell_list)

        # if they just entered cast get the digit from them then cast
        spell_level = -1
        if not args:
            while spell_level not in range(min_level, max_level+1):
                spell_level = Utils.str2int(prompt(f'what level spell between {min_level} and {max_level}? > ', 
                        validator=NumberValidator()
                ))

            self.cast(spell_level)
            return

        # if we got a digit cast the spell
        if args[0].isdigit() and int(args[0]) in range(min_level, max_level+1):
            self.cast(int(args[0]))
            return

        # if we didn't bounce them back
        if args[0].isdigit():
            self.console.print(f'[bold red]can\'t cast {Utils.get_number_output(spell.level)} level spells[/bold red]')

        return

    def cast(self, spell_level):
        for spell in self.character.spell_list:
            if spell.level == spell_level:
                if spell.remaining > 0:
                    spell.remaining -= 1
                    self.character.changed = True

                else:
                    self.console.print(f'[bold red]out of {Utils.get_number_output(spell.level)} level spells[/bold red]')
        