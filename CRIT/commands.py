import json
from os import stat
from pathlib import Path
import click

from CRIT.enums import Enums
from CRIT.item import Item
from CRIT.config import Config
from CRIT.spell import Spell

class Commands:
    @staticmethod
    def cast(character, spell_level):
        for spell in character.spell_list:
            if spell.level == spell_level:
                spell.remaining -= 1

    @staticmethod
    def feat_add(loaded_sheet):
        with open (loaded_sheet, 'r') as f:
            existing_data = json.load(f)
            value_to_add = click.prompt('what value should we add', type=click.STRING)
            existing_data['feats'].append(value_to_add)
        with open (loaded_sheet, 'w+') as outfile:
            json.dump(existing_data, outfile, indent=4)

    @staticmethod
    def feat_remove(loaded_sheet):
        with open (loaded_sheet, 'r') as f:
            existing_data = json.load(f)
            feats_list = existing_data['feats']
            value_to_remove = click.prompt('what value should we remove', type=click.Choice(feats_list, case_sensitive=False))
            existing_data['feats'].remove(value_to_remove)
        with open (loaded_sheet, 'w+') as outfile:
            json.dump(existing_data, outfile, indent=4)

    @staticmethod
    def item_add(character):
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
            dex_mod =  click.prompt('what is the max dex bonus (-1 for unlimited or N/A)?', type=click.IntRange(-1,9))
        more = click.prompt('does the item modify anything else?', type=click.Choice(['attribute', 'save', 'skill', 'no'], case_sensitive=False))
        bonus = {}
        while more != 'no':
            if more == 'attribute':
                item_attr = click.prompt(f'what {more} does the item modify?', type=click.Choice(Enums.attributes, case_sensitive=False))
            if more == 'save':
                item_attr = click.prompt(f'what {more} does the item modify?', type=click.Choice(['fortitude', 'reflex', 'will'], case_sensitive=False))
            if more == 'skill':
                skill_list = []
                for skill in character.skill_list:
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
            character.item_list.append(new_item)

    @staticmethod
    def item_equip(character, console):
        item_list = []
        for item in character.item_list:
            if item.equipped == False:
                item_list.append(item.name)

        if item_list == []:
            console.print('no items to equip')
            return()
        
        item_to_equip_name = click.prompt('equip which item?', type=click.Choice(item_list, case_sensitive=False))
        item_to_equip = {}
        for item in character.item_list:
            if item.name == item_to_equip_name:
                item_to_equip = item
        
        if 'slotless' in item_to_equip.slot:
            pass
        else:
            equipped_items = []
            for item in character.item_list:
                if item.equipped == True:
                    equipped_items.append(item)
            
            if (type(item_to_equip.slot) is str):
                for item in equipped_items:
                    if (type(item.slot) is str):
                        if item_to_equip.slot == item.slot:
                            console.print(f'unequip {item} first')
                            return()
                    if (type(item.slot) is list):
                        for slot in item.slot:
                            if item_to_equip.slot == slot:
                                console.print(f'unequip {item} first')
                                return()
            if (type(item_to_equip.slot) is list):
                for item in equipped_items:
                    if (type(item.slot) is str):
                        if item.slot in item_to_equip.slot:
                            console.print(f'unequip {item} first')
                            return()
                    if (type(item.slot) is list):
                        for slot in item.slot:
                            if slot in item_to_equip.slot:
                                console.print(f'unequip {item} first')
                                return()
        
        for item in character.item_list:
            if item.name == item_to_equip.name:
                item.equipped = True

    @staticmethod
    def item_list(character, console):
        for item in character.item_list:
            console.print(item)

    @staticmethod
    def item_remove(character, console):
        item_list = []
        for item in character.item_list:
            item_list.append(item.name)
        
        item_to_remove = click.prompt('remove which item', type=click.Choice(item_list, case_sensitive=False))

        for item in character.item_list:
            if item.name == item_to_remove:
                console.print(f'removing {item_to_remove}')
                character.item_list.remove(item)

    @staticmethod
    def item_unequip(character, console):
        item_list = []
        for item in character.item_list:
            if item.equipped == True:
                item_list.append(item.name)
        
        if item_list == []:
            console.print('no items to unequip')
            return()

        item_to_unequip_name = click.prompt('unequip which item?', type=click.Choice(item_list, case_sensitive=False))
        for item in character.item_list:
            if item.name == item_to_unequip_name:
                item.equipped = False

    @staticmethod
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

    @staticmethod
    def modify_attribute(character):
        character.attr_list = []
        for attr in character.attr_list:
            character.attr_list.append(attr.name)
        attr_to_modify = click.prompt('which attribute?', type=click.Choice(character.attr_list, case_sensitive=False))
        for attr in character.attr_list:
            if attr.name == attr_to_modify:
                attr_option = click.prompt(f'current attribute base is {attr.base}, bonus is {attr.bonus}, for a total of {attr.total}. change base or bonus?', type=click.Choice(['base', 'bonus'], case_sensitive=False))
                if attr_option == 'base':
                    new_base = click.prompt('what is the new attribute base', type=int)
                    attr.base = new_base
                if attr_option == 'bonus':
                    new_bonus = click.prompt('what is the new attribute bonus', type=int)
                    attr.bonus = new_bonus

    @staticmethod
    def modify_maxhp(character):
        maxhp = click.prompt('new max hp?', type=int)
        character.max_hp = maxhp

    @staticmethod
    def modify_skills(character):
        skill_list = []
        for skill in character.skill_list:
            skill_list.append(skill.name)
        skill_to_modify = click.prompt('what skill?', type=click.Choice(skill_list, case_sensitive=False))
        for skill in character.skill_list:
            if skill.name == skill_to_modify:
                skill_option = click.prompt(f'current skill rank is {skill.rank}, bonus is {skill.bonus}, for a total of {skill.total}. change rank or bonus?', type=click.Choice(['rank', 'bonus'], case_sensitive=False))
                if skill_option == 'rank':
                    new_rank = click.prompt('what is the new skill rank?', type=int)
                    skill.rank = new_rank
                if skill_option == 'bonus':
                    new_bonus = click.prompt('what is the new skill bonus?', type=int)
                    skill.bonus = new_bonus

    @staticmethod
    def modify_user(character, loaded_sheet, console):
        user_option = click.prompt('add or modify user element', type=click.Choice(['add', 'modify'], case_sensitive=False))
        if user_option == 'add':
            with open (loaded_sheet, 'r') as f:
                existing_data = json.load(f)
                key_to_add = click.prompt('what to add to user space (Only use if you know what you\'re doing)', type=click.STRING)
                existing_data['usr'][key_to_add] = []
            with open (loaded_sheet, 'w+') as outfile:
                json.dump(existing_data, outfile, indent=4)
            console.print(f'[bold green] UPDATED {character.name} [/bold green]')
        elif user_option == 'modify':
            with open (loaded_sheet, 'r') as f:
                existing_data = json.load(f)
                values = existing_data['usr'].keys()
                attr_to_update = click.prompt('what to update (Only use if you know what you\'re doing)', type=click.Choice(values, case_sensitive=False))
                value_to_add = click.prompt('what value should we add', type=click.STRING)
                existing_data['usr'][attr_to_update].append(value_to_add)
            with open (loaded_sheet, 'w+') as outfile:
                json.dump(existing_data, outfile, indent=4)
            console.print(f'[bold green] UPDATED {character.name} [/bold green]')
        else:
            console.print('enter valid option')

    @staticmethod
    def rest(character):
        character.hp += 2*character.level
        if character.hp > character.max_hp:
            character.hp = character.max_hp
        
        for spell in character.spell_list:
            spell.remaining = spell.slots