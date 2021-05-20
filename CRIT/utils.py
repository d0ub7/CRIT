import math
import os
from pathlib import Path
import toml
import json

from prompt_toolkit.completion.word_completer import WordCompleter
from prompt_toolkit import prompt

from .config import Config
from .enums import Enums
from .validator import NumberValidator, WordValidator

from rich import box
from rich.rule import Rule
from rich.table import Table

from CRIT import validator

class Utils:
    @staticmethod
    def get_number_output(number):
        if number == 1:
            return('1st')
        elif number == 2:
            return('2nd')
        elif number == 3:
            return('3rd')
        else:
            return(f'{number}th')

    @staticmethod
    def get_mod(stat):
        return math.floor(((stat-10)/2))
        
    @staticmethod
    def get_options_from_dir(path):
        _list = []
        if not os.path.exists(path):
            os.mkdir(path)
        for elem in os.listdir(path):
            _list.append(elem.removesuffix('.toml').removesuffix('.json').removeprefix('CRIT'))
        return(_list)

    @staticmethod
    def character_creator(console):
        # Get Name
        char_name = prompt('What is the character\'s name > ')

        # Get Level
        #, type=clik.IntRange(1,20)
        lvl_list = [str(i+1) for i in range(20)]
        char_level = Utils.str2int(prompt('What level is the character? > ', completer=WordCompleter(lvl_list), validator=WordValidator(lvl_list)))

        # Get Class
        class_list = Utils.get_options_from_dir(Path(Config.data_path, 'classes'))
        char_class = prompt('What is the character\'s class > ', completer=WordCompleter(class_list), validator=WordValidator(class_list))

        # Get Attributes
        console.print(Rule(f'[bold blue]What are the characters base attributes?,[/bold blue]'))

        char_str = Utils.str2int(prompt('What is the character\'s strength > ', validator=NumberValidator()))
        char_dex = Utils.str2int(prompt('What is the character\'s dexterity > ', validator=NumberValidator()))
        char_con = Utils.str2int(prompt('What is the character\'s constitution > ', validator=NumberValidator()))
        char_int = Utils.str2int(prompt('What is the character\'s intelligence > ', validator=NumberValidator()))
        char_wis = Utils.str2int(prompt('What is the character\'s wisdom > ', validator=NumberValidator()))
        char_cha = Utils.str2int(prompt('What is the character\'s charisma > ', validator=NumberValidator()))
        char_hp =  Utils.str2int(prompt('What is the character\'s maximum HP > ', validator=NumberValidator()))

        char_size = prompt('What size are you? > ', completer=WordCompleter(Enums.sizes), validator=WordValidator(Enums.sizes))
        # Get Skills
        skills_list = Utils.get_options_from_dir(Path(Config.data_path, 'skills'))
        skills_type = prompt('What skills should we use? > ', completer=WordCompleter(skills_list), validator=WordValidator(skills_list))
        if not os.path.isfile(Path(Config.data_path, 'skills', f'{skills_type}.json')):
            console.print(f'[bold red]{skills_type} skills unsupported. Create it yourself![/bold red]')
            return
        console.print(f'[bold red]{char_name}[/bold red] the [bold green]{Utils.get_number_output(char_level)}[/bold green] level [bold blue]{char_class}[/bold blue]')
        char_table = Table(box=box.ROUNDED)

        char_table.add_column("Attribute", justify='center', style='cyan', no_wrap=True)
        char_table.add_column("Value",     justify='center', style='green')
        char_table.add_row('Strength',     f'{char_str}')
        char_table.add_row('Dexterity',    f'{char_dex}')
        char_table.add_row('Constitution', f'{char_con}')
        char_table.add_row('Intelligence', f'{char_int}')
        char_table.add_row('Wisdom',       f'{char_wis}')
        char_table.add_row('Charisma',     f'{char_cha}')

        console.print(char_table)

        # Generate Character
        if Utils.str2bool(prompt(f'Should we create {char_name}? > ')):
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
                        console.print(Rule('[bold blue]Setting up skills[/bold blue]'))
                        with open(Path(Config.data_path, 'skills', f'{skills_type}.json')) as f:
                            skills_config = json.load(f)
                            char_data['skills_type'] = skills_type
                            for skil in skills_config['skills']:
                                temp_ = prompt(f'How many ranks do you have in {skil}? > '.replace('_', ' '), validator=NumberValidator())
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
                        char_data['spells'][str(spell_level)] = {
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
                    if os.path.isfile(Path(Config.sheets_path, f'CRIT{char_name}.toml'.replace(' ', '_'))):
                        really = Utils.str2bool(prompt(f'sheet for {char_name} exists, overwrite? > '))
                    if not really:
                        console.print(f'[bold red] NOT CREATING {char_name} [/bold red]')
                        return
                    else:
                        try:
                            os.mkdir(Path(Config.sheets_path))
                        except:
                            pass
                        with open(Path(Config.sheets_path, f'CRIT{char_name}.toml'.replace(' ', '_')), 'w+') as outfile:
                            toml.dump(char_data, outfile)
                        console.print(f'[bold green] CREATED {char_name} [/bold green]')
                except Exception as e:
                    console.print(e)
                    raise RuntimeError

    @staticmethod
    def str2bool(v):
        return v.lower() in ("yes", "true", "t", "1", "y")

    @staticmethod
    def str2int(v):
        return int(v)

    @staticmethod
    def user_output(character, console):
        with open (character.sheet, 'r') as f:
            existing_data = toml.load(f)
            grid = Table.grid(expand=True)
            for key in existing_data['usr'].keys():
                temp = Table(box=box.ROUNDED, title='')
                temp.add_column(key, justify='center',style='white',no_wrap=True)
                for value in existing_data['usr'][key]:
                    temp.add_row(value)
                grid.add_row(temp)
        console.print(grid)