from CRIT.commands import Command
from prompt_toolkit import prompt
from CRIT.validator import NumberValidator
from CRIT.utils import Utils
from pathlib import Path
from CRIT.models import Spell
from CRIT.config import Config
import json

class Level(Command):

    keywords = ['level']
    help_text = '''{keyword}
Summary: Modify level of character

Usage: {keyword} <integer> between 1-20

Examples:
    {keyword} 20
'''

    def do_command(self, *args):
        if not args:
            # , type=clik.IntRange(1,20)
            char_level = -1
            while char_level not in range(1,21):
                char_level = Utils.str2int(prompt('What level are you going to? > ', validator=NumberValidator()))
                self.console.print('not in levels 1-20')
        else:
            try:
                char_level = int(args[0])
            except:
                self.console.print('please enter an int')
                return
        self.level(self.character, self.console, char_level)
        self.console.print('Remember to add your HP with the modify command')
    
    def level(character, console, char_level):
        character.level = char_level
        char_level = char_level-1
        with open(Path(Config.data_path, 'classes', f'{character.class_}.json'), 'r') as f:
            class_config = json.load(f)
            character.bab = class_config['bab'][char_level]
            # up saves
            for sav in character.save_list:
                sav.base = class_config[sav.name][char_level]
            # up spells 
            if character.spell_list:
                console.print(character.spell_list)
                console.print(class_config['spells'])
                if character.spell_list:
                    character.spell_list = []
                    for level, spell in class_config['spells'].items():
                        console.print(f'level {level} spell {spell}')
                        character.spell_list.append(Spell(level = int(level)
                                                        , save = 0
                                                        , slots = spell[char_level]
                                                        , remaining = spell[char_level]
                                                        , base = spell[char_level]
                    ))
        character.changed = True