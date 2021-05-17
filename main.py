import json
import os
import platform
import sys
from pathlib import Path

import click
import click_completion
from prompt_toolkit import HTML, PromptSession
from prompt_toolkit.completion import NestedCompleter
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

from CRIT import HEADERS, __version__
from CRIT.charutils import CharUtils
from CRIT.commands import Commands
from CRIT.compat import clear, pause, set_terminal_size, set_terminal_title
from CRIT.config import Config
from CRIT.enums import Enums
from CRIT.json_parser import JsonParser
from CRIT.utils import Utils

if platform.system() == 'Windows':
    from ctypes import windll, wintypes


class TUI:
    def __init__(self):
        self.session = PromptSession(reserve_space_for_menu=6, complete_in_thread=True)
        self.console = None
        self.table = None
        self.tipsDatabase = None
        self.completer = None
        self.loadedCompleter = None
        self.os = platform.system()
        self.first_update = True
        self.loaded_sheet = '' 
        self.character = None

    def start(self):
        self.startup_console()
        self.setup_completer(({
            'create': None,
            'exit': None,
            'load': None
        }))
        self.print_header()
        self.console.print('Use command [green]help[/green] or press [green]TAB[/green] to see a list of available comm'
                           'ands.\nCommand [green]exit[/green] or pressing [green]CTRL+D[/green] will close the applica'
                           'tion.\n')
        try:
            with open('PermissionTest', 'w') as _:
                pass
            os.remove('PermissionTest')
        except IOError:
            self.console.print('[bold red]Character Resources In Terminal doesn\'t have write rights for the current directory.\n'
                               'Try starting it with administrative privileges.[/bold red]\n')
            pause()
            sys.exit(1)

        while True:
            try:
                command = self.session.prompt(HTML('<ansibrightgreen>CRIT></ansibrightgreen> '), completer=self.completer)
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            else:
                command = command.split(' ', 1)
                if getattr(self, f'c_{command[0].lower()}', False):
                    try:
                        getattr(self, f'c_{command[0].lower()}')(command[1].strip() if len(command) > 1 else False)
                    except Exception as e:
                        self.console.print(e)
                else:
                    self.console.print('Command not found.')

    def startup_console(self):
        if 'WINDIR' in os.environ and 'WT_SESSION' not in os.environ and 'ALACRITTY_LOG' not in os.environ:
            set_terminal_size(200, 150)
            windll.kernel32.SetConsoleScreenBufferSize(windll.kernel32.GetStdHandle(-11), wintypes._COORD(100, 200))
            self.console = Console(width=200)
        else:
            self.console = Console()

    def print_header(self):
        clear()
        self.console.print(Rule(f'[bold green]Character Resources In Terminal[/bold green] [bold red]v{__version__}[/bold red]'))
        self.console.print('')
    
    def setup_completer(self, dict):
        self.completer = NestedCompleter.from_nested_dict(dict)

    ####  _                 _          _
    ####  | | ___   __ _  __| | ___  __| |
    ####  | |/ _ \ / _` |/ _` |/ _ \/ _` |
    ####  | | (_) | (_| | (_| |  __/ (_| |
    ####  |_|\___/ \__,_|\__,_|\___|\__,_|

    def update(self):
        # items
        self.console.print('get item buffs')
        item_buffs = CharUtils.get_unique_item_buffs(self.character)

        self.console.print('updating Attributes')
        CharUtils.update_attributes(self.character, item_buffs)
            
        self.console.print('updating modifiers')
        for i in range(len(Enums.sizes)):
            if Enums.sizes[i] == self.character.size:
                self.character.size_mod = Enums.size_mods[i]
        
        self.console.print('updating AC')
        CharUtils.update_ac(self.character)

        self.console.print('updating saves')
        CharUtils.update_saves(self.character, item_buffs)

        # update bab/cmb/cmd
        if self.character.cmb_mod == 'strength':
            self.character.cmb = self.character.bab + self.character.strength.mod + self.character.size_mod
        if self.character.cmb_mod == 'dexterity':
            self.character.cmb = self.character.bab + self.character.dexterity.mod + self.character.size_mod
        self.character.cmd = 10 + self.character.bab + self.character.strength.mod + self.character.dexterity.mod + self.character.size_mod

        self.console.print('updating skills')
        CharUtils.update_skills(self.character, item_buffs)

        self.console.print('updating casting mod')
        if self.character.casting_stat == 'intelligence':
            self.character.casting_mod = self.character.intelligence.mod
        elif self.character.casting_stat == 'wisdom':
            self.character.casting_mod = self.character.wisdom.mod
        elif self.character.casting_stat == 'charisma':
            self.character.casting_mod = self.character.charisma.mod
        else:
            self.character.casting_mod = None

        if self.character.casting_stat:
            # get bonus spell data
            with open(Path(Config.data_path, 'spells', 'bonus.json'), 'r') as f:
                bonus_spells = json.load(f)

            self.console.print('updating spells')
            CharUtils.update_spells(self.character, bonus_spells)
        self.post_update()

    def post_update(self):
        self.print_loaded_header()
        self.l_main_output()

    def print_loaded_header(self):
        clear()
        self.console.print(Rule(f'[bold red]{self.character.name}[/bold red] the [bold green]{Utils.get_number_output(self.character.level)}[/bold green] level [bold blue]{self.character.class_}[/bold blue]'))

    def l_main_output(self):
        attr_table = Table(box=box.ROUNDED, title='ATTRIBUTES')
        save_table = Table(box=box.ROUNDED, title='SAVES')
        grid = Table.grid(expand=True)
        panel_grid = Table.grid()
        panel_grid.add_column(f"", justify='center',style='white',no_wrap=True)
        panel_grid.add_row(Panel.fit(f'[red]{self.character.hp}[/red]/{self.character.max_hp}',title='HP'),
                            Panel.fit(f'{self.character.bab}', title='BAB'), 
                            Panel.fit(f'{self.character.cmb}', title='CMB'), 
                            Panel.fit(f'{self.character.cmd}', title='CMD')
        )
        panel_grid.add_row(Panel.fit(f'{self.character.ac}', title='AC'),
                            Panel.fit(f'{self.character.touchac}', title='Touch AC'),
                            Panel.fit(f'{self.character.ffac}', title='FF AC')
        )

        attr_table.add_column(f"Attribute", justify='center', style='bright_red', no_wrap=True)
        attr_table.add_column(f"Value", justify='center', style='cyan', no_wrap=True)
        attr_table.add_column(f"Mod", justify='center', style='green', no_wrap=True)
        for attr in self.character.attr_list:
            attr_table.add_row(f"{attr.name}", f"{attr.total}", f"{Utils.get_mod(attr.total)}")

        save_table.add_column(f"Save", justify='center', style='bright_red', no_wrap=True)
        save_table.add_column(f"Value", justify='center', style='cyan', no_wrap=True)
        for save in self.character.save_list:
            save_table.add_row(f"{save.name}", f"{save.total}")
        grid.add_column(justify='center')
        grid.add_column(justify='center')
        skill_table = Table(box=box.ROUNDED, title='SKILLS')
        skill_table.add_column('Skill', justify='center', style='bright_red', no_wrap=True)
        skill_table.add_column('Rank', justify='center', style='cyan', no_wrap=True)
        for skill in self.character.skill_list:
            skill_table.add_row(f"{skill.name}", f"{skill.total}")
        if self.character.spell_list:
            spell_table = Table(box=box.ROUNDED, title='SPELLS')
            spell_table.add_column(f"Level", justify='center', style='bright_red', no_wrap=True)
            spell_table.add_column(f"Save", justify='center', style='cyan', no_wrap=True)
            spell_table.add_column(f"Remaining", justify='center', style='green', no_wrap=True)
            for row in self.character.spell_list:
                if row.slots > 0:
                    spell_table.add_row(f"{row.level}", f"{row.save}", f"{row.remaining}/{row.slots}")
            grid.add_column(justify='center')
            grid.add_row(panel_grid, attr_table, save_table, skill_table, spell_table)
        else:
            grid.add_row(panel_grid, attr_table, save_table, skill_table)
        self.console.print(grid)
        self.last_output_state = 'main'

    def l_usr_output(self):
        with open (self.loaded_sheet, 'r') as f:
            existing_data = json.load(f)
            grid = Table.grid(expand=True)
            for key in existing_data['usr'].keys():
                temp = Table(box=box.ROUNDED, title='')
                temp.add_column(key, justify='center',style='white',no_wrap=True)
                for value in existing_data['usr'][key]:
                    temp.add_row(value)
                grid.add_row(temp)
        self.console.print(grid)
        self.last_output_state = 'usr'

    ####                                                 _
    ####    ___ ___  _ __ ___  _ __ ___   __ _ _ __   __| |___
    ####   / __/ _ \| '_ ` _ \| '_ ` _ \ / _` | '_ \ / _` / __|
    ####  | (_| (_) | | | | | | | | | | | (_| | | | | (_| \__ \
    ####   \___\___/|_| |_| |_|_| |_| |_|\__,_|_| |_|\__,_|___/

    # pre load
    def c_exit(self, _):
        if click.confirm('Are you sure you want to quit'):
            sys.exit(0)

    def c_create(self, _):
        Utils.character_creator(self.console)

    def c_load(self, _):
        if self.first_update == False:
            return()
        sheet_to_load = click.prompt('which sheet should we load', type=Utils.get_options_from_dir(Config.sheets_path))
        sheet_to_load = Path(Config.sheets_path, f'CRIT{sheet_to_load}.json'.replace(' ', '_'))
        self.console.print('get character')
        self.character = JsonParser.load_character(sheet_to_load)
        self.loaded_sheet = sheet_to_load
        self.console.print('setup attributes')
        CharUtils.setup_attributes(self.character)
        self.console.print('setup saves')
        CharUtils.setup_saves(self.character)
        self.console.print('update')
        self.update()
        self.first_update = False
        self.setup_completer(({
            'modify': None
            ,'save': None
            ,'exit': None
            ,'user': None
            ,'main': None
            ,'level': None
        }))

    # post load
    def c_cast(self, args):
        spell_list = []
        for spell in self.character.spell_list:
            if spell.base != 0:
                spell_list.append(int(spell.level))
        min_level = min(spell_list)
        max_level = max(spell_list)
        spell_level = click.prompt('what level spell?', type=click.IntRange(min_level, max_level))
        Commands.cast(self.character, spell_level)
        self.update()

    def c_heal(self, args):
        if not args:
            heal_value = click.prompt('How much did you heal?', type=int)
        else:
            try:
                heal_value = int(args)
            except:
                self.console.print('please enter an int')
                return()
        if((self.character.hp + heal_value) > self.character.max_hp):
            if not click.confirm('Should this overheal beyond max hp?'):
                self.character.hp = self.character.max_hp
        self.character.hp += heal_value
        self.update()

    def c_harm(self, args):
        if not args:
            harm_value = click.prompt('How much damage did you take?', type=int)
        else:
            try:
                harm_value = int(args)
            except:
                self.console.print('please enter an int')
                return()
        self.character.hp -= harm_value
        self.update()

    def c_modify(self, args):
        if not args:
            modify_option = click.prompt('modifiable elements:', type= click.Choice(['user', 'maxhp', 'skill', 'attribute'], case_sensitive=False))
        else:
            try:
                modify_option = args
            except:
                pass
        if modify_option == 'user':
            Commands.modify_user(self.character, self.loaded_sheet, self.console)
        if modify_option == 'maxhp':
            Commands.modify_maxhp(self.character)
        if modify_option == 'skill':
            Commands.modify_skills(self.character)
        if modify_option == 'attribute':
            Commands.modify_attribute(self.character)
        self.update()

    def c_save(self):
        JsonParser.save_character(self.character)

    def c_level(self, args):
        if not args:
            char_level = click.prompt('What level are you going to?', type=click.IntRange(1,20))
        else:
            try:
                char_level = int(args)
            except:
                self.console.print('please enter an int')
                return()
        Commands.level(self.character, self.console, char_level)
        self.update()
        self.console.print('Remember to add your HP with the modify command')

    def c_item(self, args):
        modify_option = click.prompt('', type=click.Choice(['list', 'add', 'remove', 'equip', 'unequip'], case_sensitive=False))
        if modify_option == 'list':
            Commands.item_list(self.character, self.console)

        if modify_option == 'add':
            Commands.item_add(self.character)

        if modify_option == 'remove':
            Commands.item_remove(self.character, self.console)

        if modify_option == 'equip':
            Commands.item_equip(self.character, self.console)
            self.update()

        if modify_option == 'unequip':
            Commands.item_unequip(self.character, self.console)
            self.update()

    def c_feat(self, args):
        if not args:
            feat_options = click.prompt('add or remove feat?', type= click.Choice(['add', 'remove', 'list'], case_sensitive=False))
        else:
            try:
                feat_options = args
            except:
                pass

        if feat_options == 'add':
            Commands.feat_add(self.loaded_sheet)
            self.console.print(f'[bold green] UPDATED {self.character.name} [/bold green]')

        if feat_options == 'remove':
            Commands.feat_remove(self.loaded_sheet)
            self.console.print(f'[bold green] UPDATED {self.character.name} [/bold green]')
        
        if feat_options == 'list':
            with open (self.loaded_sheet, 'r') as f:
                existing_data = json.load(f)
                grid = Table.grid(expand=True)
                table = Table(box=box.ROUNDED, title='')
                table.add_column('FEATS', justify='center',style='white',no_wrap=True)
                for feat in existing_data['feats']:
                    table.add_row(feat)
                grid.add_row(table)
            self.console.print(grid)

    def c_rest(self, args):
        Commands.rest(self.character)
        self.update()

    # outputs
    def c_user(self, _):
        self.print_loaded_header()
        self.l_usr_output()

    def c_main(self, _):
        self.print_loaded_header()
        self.l_main_output()



@click.command()
def cli():
    set_terminal_title(f'Character Resources In Terminal v{__version__}')
    click_completion.init()
    # os.chdir(os.path.dirname(os.path.abspath(sys.executable)))
    app = TUI()
    app.start()

if __name__ == '__main__':
    cli()
