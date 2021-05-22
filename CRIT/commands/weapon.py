from CRIT.commands import Command
from CRIT import models
from CRIT.enums import Enums
from CRIT.utils import Utils
from CRIT.validator import NumberValidator, WordValidator
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

class Weapon(Command):

    keywords = ['weapon']
    help_text = '''{keyword}
{divider}
Summary: Change the character's weapons

Usage: {keyword} <verb>

Examples:

    {keyword} add
    {keyword} remove 
    {keyword} list
'''

    def do_command(self, *args): #TODO add proper args support
        mod_options = ['list', 'add', 'remove']
        modify_option = prompt(f'{mod_options} > ', completer=WordCompleter(mod_options), validator=WordValidator(mod_options))
        if modify_option == 'list':
            self.list_weapons(self.character, self.console)

        if modify_option == 'add':
            self.add(self.character, self.console)

        if modify_option == 'remove':
            self.remove(self.character, self.console)
        
    def add(self, character, console):
        base_damage = {}
        weapon_name = prompt('what is the weapon\'s name > ')
        weapon_roll = Utils.str2int(prompt('How many die in the weapons\'s base damage? > ', validator=NumberValidator()))
        die_types = ['2', '3', '4', '6', '8', '10', '12', '20']
        weapon_die = Utils.str2int(prompt('What kind of die? > ', completer=WordCompleter(die_types), validator=WordValidator(die_types)))
        
        damage_types = Enums.weapon_damage_types + Enums.energy_damage_types
        weapon_type = prompt('what type of damage does the weapon do? > ', completer=WordCompleter(damage_types), validator=WordValidator(damage_types))
        base_damage[weapon_type] = {'dice': f'{weapon_roll}d{weapon_die}'}
       
        more_damage_list = damage_types + ['no']
        more_damage = prompt('does the weapon do any additional damage? > ', completer=WordCompleter(more_damage_list), validator=WordValidator(more_damage_list))
        bonus_damage = {}
        while more_damage != 'no':
            weapon_roll = Utils.str2int(prompt('How many die in the weapons\'s base damage? > ', validator=NumberValidator()))
            die_types = ['2', '3', '4', '6', '8', '10', '12', '20']
            weapon_die = Utils.str2int(prompt('What kind of die?', completer=WordCompleter(die_types), validator=WordValidator(die_types)))
            
            bonus_damage[more_damage] = {'dice': f'{weapon_roll}d{weapon_die}'}
            more_damage = prompt('does the weapon do any additional damage? > ', completer=WordCompleter(more_damage_list), validator=WordValidator(more_damage_list))

        new_weapon = models.Weapon(name = weapon_name
                    , damage = base_damage
                    , bonus_damage = bonus_damage
        )
        console.print(new_weapon)
        if Utils.str2bool(prompt(f'create? > ', completer=WordCompleter(Enums.bool_choices), validator=WordValidator(Enums.bool_choices))):
            character.weapon_list.append(new_weapon)

    def list_weapons(self, character, console):
        for weapon in character.weapon_list:
            console.out(weapon) # print stopped working as the object got more complex

    def remove(self, character, console):
        weapon_list = []
        for weapon in character.weapon_list:
            weapon_list.append(weapon.name)
        
        weapon_to_remove = prompt('remove which weapon > ', completer=WordCompleter(weapon_list), validator=WordValidator(weapon_list))

        for weapon in character.weapon_list:
            if weapon.name == weapon_to_remove:
                console.print(f'removing {weapon_to_remove}')
                character.weapon_list.remove(weapon)