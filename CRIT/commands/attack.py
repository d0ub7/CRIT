from CRIT.charutils import CharUtils
from CRIT.commands import Command
from CRIT.enums import Enums
from CRIT.utils import Utils
from CRIT import models
from CRIT.validator import NumberValidator, WordValidator
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.rule import Rule

class Attack(Command):

    keywords = ['attack']
    help_text = '''{keyword}
Summary: Change the character's attacks

Usage: {keyword} <verb>

Examples:

    {keyword} add
    {keyword} remove 
    {keyword} list
    {keyword} use
'''

    def do_command(self, *args): #TODO add proper args support
        mod_options = ['list', 'add', 'remove', 'use']
        modify_option = prompt(f'{mod_options} > ', completer=WordCompleter(mod_options), validator=WordValidator(mod_options))
        if modify_option == 'list':
            self.list_attacks(self.character, self.console)

        if modify_option == 'add':
            self.add(self.character, self.console)

        if modify_option == 'remove':
            self.remove(self.character, self.console)

        if modify_option == 'use':
            self.use(self.character, self.console)
        
    def add(self, character, console):
        weapon_list = []
        for weapon in character.weapon_list:
            weapon_list.append(weapon.name)
        attack_name = prompt(f'Name of Attack? > ')
        weapon_to_use = prompt(f'Attack with which weapon? > ', completer=WordCompleter(weapon_list), validator=WordValidator(weapon_list))

        other_bonus_list = []
        for i in range(-99,99):
                other_bonus_list.append(str(i))

        atk_mod_to_use = prompt(f'Which attack mod should we use? > ', completer=WordCompleter(Enums.attributes), validator=WordValidator(Enums.attributes))
        other_atk_mod_prompt = prompt(f'any other mods to attack? > ', completer=WordCompleter(Enums.attributes + ['no']), validator=WordValidator(Enums.attributes + ['no']))
        other_atk_mod_prompt = other_atk_mod_prompt if other_atk_mod_prompt != 'no' else None
        atk_mod = [atk_mod_to_use, other_atk_mod_prompt] if other_atk_mod_prompt else [atk_mod_to_use]
        other_atk_bonus = prompt(f'any other bonuses to attack? > ', completer=WordCompleter(other_bonus_list), validator=WordValidator(other_bonus_list))

        dmg_mod_to_use = prompt(f'Which damage mod should we use? > ', completer=WordCompleter(Enums.attributes), validator=WordValidator(Enums.attributes))
        other_dmg_mod_prompt =  prompt(f'any other mods to damage? > ', completer=WordCompleter(Enums.attributes + ['no']), validator=WordValidator(Enums.attributes + ['no']))
        other_dmg_mod_prompt = other_dmg_mod_prompt if other_dmg_mod_prompt != 'no' else None
        dmg_mod = [dmg_mod_to_use, other_dmg_mod_prompt] if other_dmg_mod_prompt else [dmg_mod_to_use]
        other_dmg_bonus =  prompt(f'any other bonuses to damage? > ', completer=WordCompleter(other_bonus_list), validator=WordValidator(other_bonus_list))


        new_attack = models.Attack(name = attack_name
                    , weapon = weapon_to_use
                    , attack_mod = atk_mod
                    , bonus_attack = other_atk_bonus
                    , damage_mod = dmg_mod
                    , bonus_damage = other_dmg_bonus
        )
        console.print(new_attack)
        if Utils.str2bool(prompt(f'create? > ', completer=WordCompleter(Enums.bool_choices), validator=WordValidator(Enums.bool_choices))):
            character.attack_list.append(new_attack)

    def list_attacks(self, character, console):
        for attack in character.attack_list:
            console.out(attack) # print stopped working as the object got more complex

    def remove(self, character, console):
        attack_list = []
        for attack in character.attack_list:
            attack_list.append(attack.name)
        
        attack_to_remove = prompt('remove which attack > ', completer=WordCompleter(attack_list), validator=WordValidator(attack_list))

        for attack in character.attack_list:
            if attack.name == attack_to_remove:
                console.print(f'removing {attack_to_remove}')
                character.attack_list.remove(attack)
    
    def use(self, character, console):
        attack_list = []
        for attack in character.attack_list:
            attack_list.append(attack.name)
        attack_to_use = prompt(f'Attack with which weapon? > ', completer=WordCompleter(attack_list), validator=WordValidator(attack_list))
        ## Weapon(name='test', damage={'bludgeoning': {'dice': '1d8'}}, bonus_damage={'acid': {'dice': '1d4'}})
        for attack in character.attack_list:
            if attack_to_use == attack.name:
                attack_to_use = attack
        
        weapon_to_use = None
        for weapon in character.weapon_list:
            if weapon.name == attack_to_use.weapon:
                weapon_to_use = weapon

        base_damage_dice = ''
        base_damage_type = ''
        for k, v in weapon_to_use.damage.items():
            base_damage_dice = v['dice']
            base_damage_type = k
        
        bonus_damage = {}
        for k, v in weapon_to_use.bonus_damage.items():
            bonus_damage[k] = v['dice']





        ## Attack(name='test', weapon='test', attack_mod=['strength'], bonus_attack='5', damage_mod=['strength'], bonus_damage='5')
        final_atk = character.bab
        for attribute in character.attr_list:
            if attribute.name in attack_to_use.attack_mod:
                final_atk += int(attribute.mod)
        final_atk += int(attack_to_use.bonus_attack)

        final_dmg = 0
        for attribute in character.attr_list:
            if attribute.name in attack_to_use.damage_mod:
                final_dmg += int(attribute.mod)
        final_dmg += int(attack_to_use.bonus_damage)

        full_attack_counter = 0
        full_attack_check = character.bab
        self.console.print(Rule(f'[bold green]Attacking with {attack_to_use.name}[/bold green]'))
        while full_attack_check > 0:
            full_attack_check -= 5
            console.print(f'{attack_to_use.name} attack')
            console.print(f'/r 1d20+{final_atk+full_attack_counter}')
            console.print(f'{attack_to_use.name} damage ({base_damage_type})')
            console.print(f'/r {base_damage_dice}+{final_dmg}')
            for k, v in bonus_damage.items():
                console.print(f'{attack_to_use.name} bonus {k} damage')
                console.print(f'/r {v}')
            full_attack_counter -= 5
        self.console.print(Rule(f'[bold red]End of attack string[/bold red]'))
            


        
