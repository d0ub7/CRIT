from CRIT import json_parser
from CRIT import character
from CRIT.json_parser import JsonParser
import json
import math
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
from CRIT.attribute import Attribute
from CRIT.character import Character
from CRIT.compat import (clear, pause, set_terminal_size, set_terminal_title)
from CRIT.config import Config
from CRIT.enums import Enums
from CRIT.item import Item
from CRIT.json_parser import JsonParser
from CRIT.mod import Mod
from CRIT.save import Save
from CRIT.skill import Skill
from CRIT.spell import Spell

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

    def get_number_output(self, number):
        if number == 1:
            return('1st')
        elif number == 2:
            return('2nd')
        elif number == 3:
            return('3rd')
        else:
            return(f'{number}th')

    def get_mod(self, stat):
        return math.floor(((stat-10)/2))

    ####  _                 _          _
    ####  | | ___   __ _  __| | ___  __| |
    ####  | |/ _ \ / _` |/ _` |/ _ \/ _` |
    ####  | | (_) | (_| | (_| |  __/ (_| |
    ####  |_|\___/ \__,_|\__,_|\___|\__,_|

    def get_modifiers(self):
        self.character.str_mod = self.get_mod(self.character.attr_list[0].total)
        self.character.dex_mod = self.get_mod(self.character.attr_list[1].total)
        self.character.con_mod = self.get_mod(self.character.attr_list[2].total)
        self.character.int_mod = self.get_mod(self.character.attr_list[3].total)
        self.character.wis_mod = self.get_mod(self.character.attr_list[4].total)
        self.character.cha_mod = self.get_mod(self.character.attr_list[5].total)
        for i in range(len(Enums.sizes)):
            if Enums.sizes[i] == self.character.char_size:
                self.character.size_mod = Enums.size_mods[i]

    def get_equipped_item_buffs(self):
        unique_item_buffs = []
        item_buffs = []
        for item in self.character.item_list:
            if item.equipped is True:
                for bonus in item.bonus:
                    item_buffs.append(Mod(
                                    stat = item.bonus[bonus]['stat']
                                    , type_ = item.bonus[bonus]['type']
                                    , value = item.bonus[bonus]['value']
                                    ))
        buffdict = {}
        for item in item_buffs:
            if item.stat + item.type_ in buffdict.keys():
                if item.value > buffdict[f'{item.stat}_{item.type}']:
                    buffdict[f'{item.stat}_{item.type_}'] = item.value
                else:
                    pass
            else:
                buffdict[f'{item.stat}_{item.type_}'] = item.value
        for buff, value in buffdict.items():
            unique_item_buffs.append(Mod(stat = buff.split('_')[0]
                                , type_ = buff.split('_')[1]
                                , value = value
                                ))
        return unique_item_buffs

    def update(self):
        # items
        item_buffs = self.get_equipped_item_buffs()

        self.console.print('updating Attributes')
        for attr in self.character.attr_list:
            attr.item = 0
            for buff in item_buffs:
                if buff.stat == attr.name:
                    attr.item += buff.value
            attr.total = attr.base + attr.bonus + attr.item

        self.console.print('updating modifiers')
        self.get_modifiers()

        self.console.print('updating saves')
        for save in self.character.save_list:
            save.item = 0
            for buff in item_buffs:
                if buff.stat == save.name:
                    save.item += buff.value
        self.character.save_list[0].total = self.character.save_list[0].base + self.character.con_mod + self.character.save_list[0].bonus + self.character.save_list[0].item
        self.character.save_list[1].total = self.character.save_list[1].base + self.character.dex_mod + self.character.save_list[1].bonus + self.character.save_list[1].item
        self.character.save_list[2].total = self.character.save_list[2].base + self.character.wis_mod + self.character.save_list[2].bonus + self.character.save_list[2].item

        self.console.print('updating cmb/cmd')
        if self.character.cmb_mod == 'strength':
            self.character.char_cmb = self.character.char_bab + self.character.str_mod + self.character.size_mod
        if self.character.cmb_mod == 'dexterity':
            self.character.char_cmb = self.character.char_bab + self.character.dex_mod + self.character.size_mod
        self.character.char_cmd = 10 + self.character.char_bab + self.character.str_mod + self.character.dex_mod + self.character.size_mod

        self.console.print('updating skills')
        # update skills
        for skill in self.character.skill_list:
            skill.item = 0
            for buff in item_buffs:
                if buff.stat == skill.name:
                    skill.item += buff.value
            skill.total = 0
            if skill.rank > 0:
                skill.total += skill.rank
                if skill.class_:
                    skill.total += 3

            if skill.ability == 'strength':
                skill.total += self.character.str_mod
            if skill.ability == 'dexterity':
                skill.total += self.character.dex_mod
            if skill.ability == 'constitution':
                skill.total += self.character.con_mod
            if skill.ability == 'intelligence':
                skill.total += self.character.int_mod
            if skill.ability == 'wisdom':
                skill.total += self.character.wis_mod
            if skill.ability == 'charisma':
                skill.total += self.character.cha_mod
            
            skill.total += skill.bonus
            skill.total += skill.item

        self.console.print('updating casting mod')
        # get casting mod
        if self.character.casting_stat == 'intelligence':
            self.character.casting_mod = self.character.int_mod
        elif self.character.casting_stat == 'wisdom':
            self.character.casting_mod = self.character.wis_mod
        elif self.character.casting_stat == 'charisma':
            self.character.casting_mod = self.character.cha_mod
        else:
            pass

        # get bonus spell data
        with open(Path(Config.data_path, 'spells', 'bonus.json'), 'r') as f:
            bonus_spells = json.load(f)

        self.console.print('updating spells')
        # Spell stuff
        self.console.print(f'casting mod: {self.character.casting_mod}')
        current_casting_mod = 16 if self.character.casting_mod > 16 else self.character.casting_mod
        if self.character.casting_mod == None or self.character.casting_mod < 0:
            self.character.spell_list = None
            self.console.print(Rule('[bold red]UNABLE TO CAST SPELLS[/bold red]'))
        elif self.character.casting_mod == 0:
            # no bonus spells
            for spel in self.character.spell_list:
                if spel.base != 0:
                    spel.save = 10 + spel.level
                    spel.slots = spel.base
        else:
            # get bonus spells
            for spel in self.character.spell_list:
                if spel.base != 0:
                    spel.save = 10 + spel.level + current_casting_mod
                    spel.slots = bonus_spells[str(current_casting_mod)][spel.level-1] + spel.base
        self.post_update()

    def post_update(self):
        self.print_loaded_header()
        self.l_main_output()

    def print_loaded_header(self):
        clear()
        self.console.print(Rule(f'[bold red]{self.character.char_name}[/bold red] the [bold green]{self.get_number_output(self.character.char_level)}[/bold green] level [bold blue]{self.character.char_class}[/bold blue]'))

    def l_main_output(self):
        attr_table = Table(box=box.ROUNDED, title='ATTRIBUTES')
        save_table = Table(box=box.ROUNDED, title='SAVES')
        grid = Table.grid(expand=True)
        panel_grid = Table.grid()
        panel_grid.add_column(f"", justify='center',style='white',no_wrap=True)
        panel_grid.add_row(Panel.fit(f'[red]{self.character.hp}[/red]/{self.character.max_hp}',title='HP'),
                            Panel.fit(f'{self.character.char_bab}', title='BAB'), 
                            Panel.fit(f'{self.character.char_cmb}', title='CMB'), 
                            Panel.fit(f'{self.character.char_cmd}', title='CMD'))

        attr_table.add_column(f"Attribute", justify='center', style='bright_red', no_wrap=True)
        attr_table.add_column(f"Value", justify='center', style='cyan', no_wrap=True)
        attr_table.add_column(f"Mod", justify='center', style='green', no_wrap=True)
        for attr in self.character.attr_list:
            attr_table.add_row(f"{attr.name}", f"{attr.total}", f"{self.get_mod(attr.total)}")

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

    def l_combat_output(self):
        pass

    def l_downtime_output(self):
        pass

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
        # Get Name
        char_name = click.prompt('What is the character\'s name', type=click.STRING)

        # Get Level
        char_level = click.prompt('What level is the character?', type=click.IntRange(1,20))

        # Get Class
        self.console.print(('[bold blue]Supported Clases[/bold blue]'))
        char_class = click.prompt('What is the character\'s class', type=get_options_from_dir(Path(Config.data_path, 'classes')))
        if not os.path.isfile(Path(Config.data_path, 'classes', f'{char_class}.json')):
            self.console.print(f'[bold red]{char_class} class unsupported. Create it yourself![/bold red]')
            return()

        # Get Attributes
        self.console.print(Rule(f'[bold blue]What are the characters base attributes?,[/bold blue]'))

        char_str = click.prompt('What is the character\'s strength', type=int)
        char_dex = click.prompt('What is the character\'s dexterity', type=int)
        char_con = click.prompt('What is the character\'s constitution', type=int)
        char_int = click.prompt('What is the character\'s intelligence', type=int)
        char_wis = click.prompt('What is the character\'s wisdom', type=int)
        char_cha = click.prompt('What is the character\'s charisma', type=int)
        char_hp =  click.prompt('What is the character\'s maximum HP', type=int)

        char_size = click.prompt('What size are you?', type=click.Choice(Enums.sizes))
        # Get Skills
        skills_type = click.prompt('What skills should we use? (leave blank for default)', type=get_options_from_dir(Path(Config.data_path, 'skills')), default='default')
        if not os.path.isfile(Path(Config.data_path, 'skills', f'{skills_type}.json')):
            self.console.print(f'[bold red]{skills_type} skills unsupported. Create it yourself![/bold red]')
            return()
        self.console.print(f'[bold red]{char_name}[/bold red] the [bold green]{self.get_number_output(char_level)}[/bold green] level [bold blue]{char_class}[/bold blue]')
        char_table = Table(box=box.ROUNDED)

        char_table.add_column("Attribute", justify='center', style='cyan', no_wrap=True)
        char_table.add_column("Value",     justify='center', style='green')
        char_table.add_row('Strength',     f'{char_str}')
        char_table.add_row('Dexterity',    f'{char_dex}')
        char_table.add_row('Constitution', f'{char_con}')
        char_table.add_row('Intelligence', f'{char_int}')
        char_table.add_row('Wisdom',       f'{char_wis}')
        char_table.add_row('Charisma',     f'{char_cha}')

        self.console.print(char_table)

        # Generate Character
        if click.confirm(f'Should we create {char_name}?'):
            with open(Path(Config.data_path, 'classes', f'{char_class}.json'), 'r') as f:
                try: 
                    class_config = json.load(f)
                    char_data = {}
                    char_data['name'] = char_name
                    char_data['class'] = char_class
                    char_data['level'] = char_level
                    char_data['hp'] = char_data['max_hp'] = char_hp
                    char_data['bab'] = class_config['bab'][char_level-1]
                    char_data['casting_stat'] = class_config['casting_stat']
                    char_data['size'] = char_size

                    # Attributes
                    char_attr_list = [char_str, char_dex, char_con, char_int, char_wis, char_cha]
                    char_data['attributes'] = {}
                    for i in range(len(Enums.attributes)):
                        char_data['attributes'][Enums.attributes[i]] = {
                            'total': 0
                            , 'base': char_attr_list[i]
                            , 'bonus': 0
                            }

                    # saves
                    char_data['saves'] = {}
                    char_data['saves']['fortitude'] = {
                        'total': 0
                        , 'ability': 'constitution'
                        , 'bonus': 0
                        , 'base': class_config['fortitude'][char_level-1]
                    }
                    char_data['saves']['reflex'] = {
                        'total': 0
                        , 'ability': 'dexterity'
                        , 'bonus': 0
                        , 'base': class_config['reflex'][char_level-1]
                    }
                    char_data['saves']['will'] = {
                        'total': 0
                        , 'ability': 'wisdom'
                        , 'bonus': 0
                        , 'base': class_config['will'][char_level-1]
                    }

                    # We get skills here because it takes a json load and we want to verify other steps before getting here
                    # also do here because we need this prompt and it's easier here
                    char_data['skills'] = {}
                    if os.path.isfile(Path(Config.data_path, 'skills', f'{skills_type}.json')):
                        self.console.print(Rule('[bold blue]Setting up skills[/bold blue]'))
                        with open(Path(Config.data_path, 'skills', f'{skills_type}.json')) as f:
                            skills_config = json.load(f)
                            char_data['skills_type'] = skills_type
                            for skil in skills_config['skills']:
                                temp_ = click.prompt(f'How many ranks do you have in {skil}?'.replace('_', ' '))
                                class_ = True if skil in class_config['class_skills'] else False
                                char_data['skills'][skil] = {
                                    'total': 0
                                    , 'ability': skills_config['skills'][skil]
                                    , 'rank': int(temp_)
                                    , 'bonus': 0
                                    , 'class_': class_
                                }

                    # spells
                    char_data['spells'] = {}
                    for spell_level in class_config['spells']:
                        char_data['spells'][int(spell_level)] = {
                            'save': 0 # set this on load
                            , 'slots': class_config['spells'][spell_level][char_level-1]
                            , 'remaining': class_config['spells'][spell_level][char_level-1]
                            , 'base': class_config['spells'][spell_level][char_level-1]
                        }

                    # create empty item space
                    char_data['items'] = {}
                    # create empty usr space
                    char_data['usr'] = {}
                    # create empty feats space
                    char_data['feats'] = []

                    really = True
                    if os.path.isfile(Path(Config.sheets_path, f'CRIT{char_name}.json'.replace(' ', '_'))):
                        really = click.confirm(f'sheet for {char_name} exists, overwrite?')
                    if not really:
                        self.console.print(f'[bold red] NOT CREATING {char_name} [/bold red]')
                        return()
                    else:
                        try:
                            os.mkdir(Path(Config.sheets_path))
                        except:
                            pass
                        with open(Path(Config.sheets_path, f'CRIT{char_name}.json'.replace(' ', '_')), 'w+') as outfile:
                            json.dump(char_data, outfile, indent=4)
                        self.console.print(f'[bold green] CREATED {char_name} [/bold green]')
                except Exception as e:
                    self.console.print(e)
                    raise RuntimeError

    def c_load(self, _):
        if self.first_update == False:
            return()
        sheet_to_load = click.prompt('which sheet should we load', type=get_options_from_dir(Config.sheets_path))
        self.character = JsonParser.load_character(Path(Config.sheets_path, f'CRIT{sheet_to_load}.json'.replace(' ', '_')))
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
        modify_option = click.prompt('modifiable elements:', type= click.Choice(['user', 'maxhp', 'skill', 'attribute'], case_sensitive=False))
        if modify_option == 'user':
            user_option = click.prompt('add or modify user element', type=click.Choice(['add', 'modify'], case_sensitive=False))
            if user_option == 'add':
                with open (self.loaded_sheet, 'r') as f:
                    existing_data = json.load(f)
                    key_to_add = click.prompt('what to add to user space (Only use if you know what you\'re doing)', type=click.STRING)
                    existing_data['usr'][key_to_add] = []
                with open (self.loaded_sheet, 'w+') as outfile:
                    json.dump(existing_data, outfile, indent=4)
                self.console.print(f'[bold green] UPDATED {self.character.char_name} [/bold green]')
            elif user_option == 'modify':
                with open (self.loaded_sheet, 'r') as f:
                    existing_data = json.load(f)
                    values = existing_data['usr'].keys()
                    attr_to_update = click.prompt('what to update (Only use if you know what you\'re doing)', type=click.Choice(values, case_sensitive=False))
                    value_to_add = click.prompt('what value should we add', type=click.STRING)
                    existing_data['usr'][attr_to_update].append(value_to_add)
                with open (self.loaded_sheet, 'w+') as outfile:
                    json.dump(existing_data, outfile, indent=4)
                self.console.print(f'[bold green] UPDATED {self.character.char_name} [/bold green]')
            else:
                self.console.print('enter valid option')
        if modify_option == 'maxhp':
            maxhp = click.prompt('new max hp?', type=int)
            self.character.max_hp = maxhp
        if modify_option == 'skill':
            skill_list = []
            for skill in self.character.skill_list:
                skill_list.append(skill.name)
            skill_to_modify = click.prompt('what skill?', type=click.Choice(skill_list, case_sensitive=False))
            for skill in self.character.skill_list:
                if skill.name == skill_to_modify:
                    skill_option = click.prompt(f'current skill rank is {skill.rank}, bonus is {skill.bonus}, for a total of {skill.total}. change rank or bonus?', type=click.Choice(['rank', 'bonus'], case_sensitive=False))
                    if skill_option == 'rank':
                        new_rank = click.prompt('what is the new skill rank?', type=int)
                        skill.rank = new_rank
                    if skill_option == 'bonus':
                        new_bonus = click.prompt('what is the new skill bonus?', type=int)
                        skill.bonus = new_bonus
        if modify_option == 'attribute':
            character.attr_list = []
            for attr in self.character.attr_list:
                character.attr_list.append(attr.name)
            attr_to_modify = click.prompt('which attribute?', type=click.Choice(character.attr_list, case_sensitive=False))
            for attr in self.character.attr_list:
                if attr.name == attr_to_modify:
                    attr_option = click.prompt(f'current attribute base is {attr.base}, bonus is {attr.bonus}, for a total of {attr.total}. change base or bonus?', type=click.Choice(['base', 'bonus'], case_sensitive=False))
                    if attr_option == 'base':
                        new_base = click.prompt('what is the new attribute base', type=int)
                        attr.base = new_base
                    if attr_option == 'bonus':
                        new_bonus = click.prompt('what is the new attribute bonus', type=int)
                        attr.bonus = new_bonus
        self.update()

    def c_save(self, args):
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

        self.character.char_level = char_level
        char_level = char_level-1
        with open(Path(Config.data_path, 'classes', f'{self.character.char_class}.json'), 'r') as f:
            class_config = json.load(f)
            self.character.char_bab = class_config['bab'][char_level]
            # up saves
            for sav in self.character.save_list:
                sav.base = class_config[sav.name][char_level]
            # up spells 
            self.console.print(self.character.spell_list)
            self.console.print(class_config['spells'])
            if self.character.spell_list:
                self.character.spell_list = []
                for level, spell in class_config['spells'].items():
                    self.console.print(f'level {level} spell {spell}')
                    self.character.spell_list.append(Spell(level = int(level)
                                                    , save = 0
                                                    , slots = spell[char_level]
                                                    , remaining = spell[char_level]
                                                    , base = spell[char_level]
                                                    ))

        self.update()
        self.console.print('Remember to add your HP with the modify command')

    def c_item(self, args):
        modify_option = click.prompt('', type=click.Choice(['list', 'add', 'remove', 'equip', 'unequip'], case_sensitive=False))
        if modify_option == 'list':
            for item in self.character.item_list:
                self.console.print(item)
        if modify_option == 'add':
            item_name = click.prompt('what is the item\'s name', type=str)
            acp = 0
            ac_type = None
            dex_mod = 0
            item_slots = []
            item_slot = click.prompt('what slot is the item in?', type=click.Choice(Enums.gear_slots, case_sensitive=False))
            if click.confirm('is there a second slot?'):
                item_slot2 = click.prompt('what second slot is the item in?', type=click.Choice(Enums.gear_slots, case_sensitive=False))
                if item_slot != item_slot2:
                    item_slots.append(item_slot2)
            item_slots.append(item_slot)
            item_ac = click.prompt('how much ac does the item provide', type=int)
            if item_ac != 0:
                acp = click.prompt('what is the acp of the item?', type=click.IntRange(-9,0))
                ac_type = click.prompt('what type of ac bonus?', type=click.Choice(Enums.bonus_types, case_sensitive=False))
                dex_mod =  click.prompt('what is the dexterity modifier?', type=click.IntRange(0,9))
            more = click.prompt('does the item modify anything else?', type=click.Choice(['attribute', 'save', 'skill', 'no'], case_sensitive=False))
            bonus = {}
            while more != 'no':
                if more == 'attribute':
                    item_attr = click.prompt(f'what {more} does the item modify?', type=click.Choice(Enums.attributes, case_sensitive=False))
                if more == 'save':
                    item_attr = click.prompt(f'what {more} does the item modify?', type=click.Choice(['fortitude', 'reflex', 'will'], case_sensitive=False))
                if more == 'skill':
                    skill_list = []
                    for skill in self.character.skill_list:
                        skill_list.append(skill.name)
                    item_attr = click.prompt(f'what {more} does the item modify?', type=click.Choice(skill_list, case_sensitive=False))
                item_attr_value = click.prompt(f'how much?', type=click.IntRange(-99,99))
                item_attr_type = click.prompt('what type of bonus', type=click.Choice(Enums.bonus_types, case_sensitive=False))
                bonus[item_attr] = {'stat': item_attr
                                , 'value':  item_attr_value
                                , 'type': item_attr_type}
                more = click.prompt('does the item modify anything else?', type=click.Choice(['attribute', 'save', 'skill', 'no'], case_sensitive=False))

            new_item = Item(name = item_name
                                    , equipped = False
                                    , slot = item_slots
                                    , ac = item_ac
                                    , acp = acp
                                    , dex_mod = dex_mod
                                    , ac_type = ac_type
                                    , bonus = bonus)
            if click.confirm(f'create {new_item}?'):
                self.character.item_list.append(new_item)
        if modify_option == 'remove':
            item_list = []
            for item in self.character.item_list:
                item_list.append(item.name)
            
            item_to_remove = click.prompt('remove which item', type=click.Choice(item_list, case_sensitive=False))

            for item in self.character.item_list:
                if item.name == item_to_remove:
                    self.console.print(f'removing {item_to_remove}')
                    self.character.item_list.remove(item)
        if modify_option == 'equip':
            item_list = []
            for item in self.character.item_list:
                if item.equipped == False:
                    item_list.append(item.name)

            if item_list == []:
                self.console.print('no items to equip')
                return()
            
            item_to_equip_name = click.prompt('equip which item?', type=click.Choice(item_list, case_sensitive=False))
            item_to_equip = {}
            for item in self.character.item_list:
                if item.name == item_to_equip_name:
                    item_to_equip = item

            equipped_items = []
            for item in self.character.item_list:
                if item.equipped == True:
                    equipped_items.append(item)
            
            if (type(item_to_equip.slot) is str):
                for item in equipped_items:
                    if (type(item.slot) is str):
                        if item_to_equip.slot == item.slot:
                            self.console.print(f'unequip {item} first')
                            return()
                    if (type(item.slot) is list):
                        for slot in item.slot:
                            if item_to_equip.slot == slot:
                                self.console.print(f'unequip {item} first')
                                return()
            if (type(item_to_equip.slot) is list):
                for item in equipped_items:
                    if (type(item.slot) is str):
                        if item.slot in item_to_equip.slot:
                            self.console.print(f'unequip {item} first')
                            return()
                    if (type(item.slot) is list):
                        for slot in item.slot:
                            if slot in item_to_equip.slot:
                                self.console.print(f'unequip {item} first')
                                return()
            
            for item in self.character.item_list:
                if item.name == item_to_equip.name:
                    item.equipped = True
        if modify_option == 'unequip':
            item_list = []
            for item in self.character.item_list:
                if item.equipped == True:
                    item_list.append(item.name)
            
            if item_list == []:
                self.console.print('no items to unequip')
                return()

            item_to_unequip_name = click.prompt('unequip which item?', type=click.Choice(item_list, case_sensitive=False))
            for item in self.character.item_list:
                if item.name == item_to_unequip_name:
                    item.equipped = False
        self.update()

    def c_feat(self, args):
        pass

    # outputs
    def c_user(self, _):
        self.print_loaded_header()
        self.l_usr_output()

    def c_main(self, _):
        self.print_loaded_header()
        self.l_main_output()

def get_options_from_dir(path):
    # returns a click.Choice
    _list = []
    for elem in os.listdir(path):
        _list.append(elem.removesuffix('.json').removeprefix('CRIT'))
    return(click.Choice(_list, case_sensitive=False))

@click.command()
def cli():
    set_terminal_title(f'Character Resources In Terminal v{__version__}')
    click_completion.init()
    os.chdir(os.path.dirname(os.path.abspath(sys.executable)))
    app = TUI()
    app.start()

if __name__ == '__main__':
    cli()
