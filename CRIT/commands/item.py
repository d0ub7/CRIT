from CRIT import models
from CRIT.commands import Command
from CRIT.enums import Enums
from CRIT.utils import Utils
from CRIT.validator import NumberValidator, WordValidator
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

class Item(Command):

    keywords = ['item']
    help_text = '''{keyword}
Summary: Change the character's items

Usage: {keyword} <verb>

Examples:

    {keyword} add
    {keyword} remove 
    {keyword} list
    {keyword} equip
    {keyword} unequip
'''

    def do_command(self, *args): #TODO add proper args support
        mod_options = ['list', 'add', 'remove', 'equip', 'unequip']
        modify_option = prompt(f'{mod_options} > ', completer=WordCompleter(mod_options), validator=WordValidator(mod_options))
        if modify_option == 'list':
            self.list_items(self.character, self.console)

        if modify_option == 'add':
            self.add(self.character)

        if modify_option == 'remove':
            self.remove(self.character, self.console)

        if modify_option == 'equip':
            self.equip(self.character, self.console)

        if modify_option == 'unequip':
            self.unequip(self.character, self.console)
        
    def add(self, character):
        item_name = prompt('what is the item\'s name > ')
        acp = 0
        ac_type = None
        dex_mod = 0
        item_slots = []
        item_slot = prompt('what slot is the item in? > ', completer=WordCompleter(Enums.gear_slots), validator=WordValidator(Enums.gear_slots))
        if Utils.str2bool(prompt('is there a second slot? > ', completer=WordCompleter(Enums.bool_choices), validator=WordValidator(Enums.bool_choices))):
            item_slot2 = prompt('what second slot is the item in? > ', completer=WordCompleter(Enums.gear_slots), validator=WordValidator(Enums.gear_slots))
            if item_slot != item_slot2:
                item_slots.append(item_slot2)
        item_slots.append(item_slot)
        item_ac = Utils.str2int(prompt('how much ac does the item provide > ', validator=NumberValidator()))
        ac = {}
        if item_ac != 0:
            acp_list = ['0','-1','-2','-3','-4','-5','-6','-7','-8','-9']
            acp = Utils.str2int(prompt('what is the acp of the item? > ', completer=WordCompleter(acp_list), validator=WordValidator(acp_list)))
            ac_type = prompt('what type of ac bonus? > ', completer=WordCompleter(Enums.bonus_types), validator=WordValidator(Enums.bonus_types))
            dex_list = ['-1','0','1','2','3','4','5','6','7','8','9']
            dex_mod =  Utils.str2int(prompt('what is the max dex bonus (-1 for unlimited or N/A)? > ', completer=WordCompleter(dex_list), validator=WordValidator(dex_list)))
            ac[ac_type] = {'ac': item_ac
                        , 'acp': acp
                        , 'dex_mod': dex_mod
            }
        mod_list = ['attribute', 'save', 'skill', 'no']
        more = prompt('does the item modify anything else? > ', completer=WordCompleter(mod_list), validator=WordValidator(mod_list))
        bonus = {}
        while more != 'no':
            if more == 'attribute':
                item_attr = prompt(f'what {more} does the item modify? > ', completer=WordCompleter(Enums.attributes), validator=WordValidator(Enums.attributes))
            if more == 'save':
                sav_list = ['fortitude', 'reflex', 'will']
                item_attr = prompt(f'what {more} does the item modify? > ', completer=WordCompleter(sav_list), validator=WordValidator(sav_list))
            if more == 'skill':
                skill_list = []
                for skill in character.skill_list:
                    skill_list.append(skill.name)
                item_attr = Utils.str2int(prompt(f'what {more} does the item modify? > ', completer=WordCompleter(skill_list), validator=WordValidator(skill_list)))
                # , type=clik.IntRange(-99,99)
            howmuch_list = []
            for i in range(-99,99):
                howmuch_list.append(str(i))
            item_attr_value = Utils.str2int(prompt(f'how much? > ', completer=WordCompleter(howmuch_list), validator=WordValidator(howmuch_list)))
            item_attr_type = prompt('what type of bonus > ', completer=WordCompleter(Enums.bonus_types), validator=WordValidator(Enums.bonus_types))
            bonus[item_attr] = {'value':  item_attr_value
                            , 'type': item_attr_type}
            more_list = ['attribute', 'save', 'skill', 'no']
            more = prompt('does the item modify anything else? > ', completer=WordCompleter(more_list), validator=WordValidator(more_list))

        new_item = models.Item(name = item_name
                    , equipped = False
                    , slot = item_slots
                    , ac = ac
                    , bonus = bonus
        )
        console.print(new_item)
        if Utils.str2bool(prompt(f'create?', completer=WordCompleter(Enums.bool_choices), validator=WordValidator(Enums.bool_choices))):
            character.item_list.append(new_item)

    def list_items(self, character, console):
        for item in character.item_list:
            console.out(item) # print stopped working as the object got more complex

    def remove(self, character, console):
        item_list = []
        for item in character.item_list:
            item_list.append(item.name)
        
        item_to_remove = prompt('remove which item > ', completer=WordCompleter(item_list), validator=WordValidator(item_list))

        for item in character.item_list:
            if item.name == item_to_remove:
                console.print(f'removing {item_to_remove}')
                character.item_list.remove(item)

    def equip(self, character, console):
        item_list = []
        for item in character.item_list:
            if item.equipped == False:
                item_list.append(item.name)

        if item_list == []:
            console.print('no items to equip')
            return
        
        item_to_equip_name = prompt('equip which item? > ', completer=WordCompleter(item_list), validator=WordValidator(item_list))
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
                            return
                    if (type(item.slot) is list):
                        for slot in item.slot:
                            if item_to_equip.slot == slot:
                                console.print(f'unequip {item} first')
                                return
            if (type(item_to_equip.slot) is list):
                for item in equipped_items:
                    if (type(item.slot) is str):
                        if item.slot in item_to_equip.slot:
                            console.print(f'unequip {item} first')
                            return
                    if (type(item.slot) is list):
                        for slot in item.slot:
                            if slot in item_to_equip.slot:
                                console.print(f'unequip {item} first')
                                return

        for item in character.item_list:
            if item.name == item_to_equip.name:
                item.equipped = True
                self.character.changed = True

    def unequip(self, character, console):
        item_list = []
        for item in character.item_list:
            if item.equipped == True:
                item_list.append(item.name)
        
        if item_list == []:
            console.print('no items to unequip')
            return

        item_to_unequip_name = prompt('unequip which item? > ', completer=WordCompleter(item_list), validator=WordValidator(item_list))
        for item in character.item_list:
            if item.name == item_to_unequip_name:
                item.equipped = False
                self.character.changed = True
