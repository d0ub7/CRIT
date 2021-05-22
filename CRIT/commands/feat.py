from CRIT.validator import WordValidator
from CRIT.commands import Command
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich import box
from rich.table import Table


class Feat(Command):

    keywords = ['feat']
    help_text = '''{keyword}
{divider}
Summary: Modify list of feats

Usage: {keyword} <verb> <Feat name>

Examples:

    {keyword} add
    {keyword} remove 
    {keyword} list
'''

    def do_command(self, *args):
        if not args:
            opt_list = ['add', 'remove', 'list']
            feat_options = prompt('add or remove or list feat? > ', 
                    completer=WordCompleter(opt_list), 
                    validator=WordValidator(opt_list)
            )

        else:
            try:
                feat_options = args

            except:
                pass

        if feat_options == 'add':
            value_to_add = prompt('what value should we add > ')
            self.character.feat_list.append(value_to_add)

        if feat_options == 'remove':
            value_to_remove = prompt('what value should we remove > ', 
                    completer=WordCompleter(self.character.feat_list), 
                    validator=WordValidator(self.character.feat_list)
            )

            if value_to_remove in self.character.feat_list:
                self.character.feat_list.remove(value_to_remove)

            else:
                self.console.print(f'[bold red]{value_to_remove} not in feats[/bold red]')
        
        if feat_options == 'list':
            grid = Table.grid(expand=True)
            table = Table(box=box.ROUNDED, title='')
            table.add_column('FEATS', justify='center',style='white',no_wrap=True)
            for feat in self.character.feat_list:
                table.add_row(feat)

            grid.add_row(table)
            self.console.print(grid)
        