import yaml

from CRIT.commands import Command
from CRIT.utils import Utils
from CRIT.validator import WordValidator
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter


class User(Command):

    keywords = ['user']
    help_text = '''{keyword}
{divider}
Summary: List or modify "user" space
just a scratchpad for whatever you want
on your character sheet

Usage: {keyword}
'''

    def do_command(self, *args):
        opt_list = ['add', 'modify', 'list']
        user_option = prompt('add, modify, or list user element > ', 
                completer=WordCompleter(opt_list), 
                validator=WordValidator(opt_list)
        )

        if user_option == 'add':
            with open (self.character.sheet, 'r') as f:
                existing_data = yaml.load(f, Loader=yaml.FullLoader)
                key_to_add = prompt('what to add to user space > ')
                existing_data['usr'] = {key_to_add: []}

            with open (self.character.sheet, 'w+') as outfile:
                yaml.dump(existing_data, outfile)

            self.console.print(f'[bold green] UPDATED {self.character.name} [/bold green]')

        elif user_option == 'modify':
            with open (self.character.sheet, 'r') as f:
                existing_data = yaml.load(f, Loader=yaml.FullLoader)
                values = existing_data['usr'].keys()
                attr_to_update = prompt('what to update > ', 
                        completer=WordCompleter(values), 
                        validator=WordValidator(values)
                )

                value_to_add = prompt('what value should we add > ')
                existing_data['usr'][attr_to_update].append(value_to_add)

            with open (self.character.sheet, 'w+') as outfile:
                yaml.dump(existing_data, outfile)

            self.console.print(f'[bold green] UPDATED {self.character.name} [/bold green]')

        elif user_option == 'list':
            Utils.user_output(self.character, self.console)

        else:
            self.console.print('enter valid option')
