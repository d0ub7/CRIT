from prompt_toolkit.shortcuts.prompt import E
from CRIT.commands import Command
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from CRIT.utils import Utils
from CRIT.enums import Enums
from CRIT.validator import NumberValidator, WordValidator
import json


class Modify(Command):

    keywords = ['modify']
    help_text = '''{keyword}
{divider}
Summary: Change the character's items

Usage: {keyword} <verb>

Examples:

    {keyword} maxhp
    {keyword} skill 
    {keyword} attribute
'''

    def do_command(self, *args): #TODO add proper args support
        if not args:
            mod_list = ['maxhp', 'skill', 'attribute', 'user']
            modify_option = prompt('modify > ', completer=WordCompleter(mod_list), validator=WordValidator(mod_list))
        else:
            try:
                modify_option = args
            except:
                pass
        if modify_option == 'user':
            self.modify_user(self.character, self.console)
        if modify_option == 'maxhp':
            self.modify_maxhp(self.character)
        if modify_option == 'skill':
            self.modify_skills(self.character)
        if modify_option == 'attribute':
            self.modify_attribute(self.character)
        
    def modify_attribute(self, character):
        attr_to_modify = prompt('which attribute? > ', completer=WordCompleter(Enums.attributes), validator=WordValidator(Enums.attributes))
        for attr in character.attr_list:
            if attr.name == attr_to_modify:
                opt_list = ['base', 'bonus']
                attr_option = prompt(f'current attribute base is {attr.base}, bonus is {attr.bonus}, for a total of {attr.total}. change base or bonus? > ', completer=WordCompleter(opt_list), validator=WordValidator(opt_list))
                if attr_option == 'base':
                    new_base = Utils.str2int(prompt('what is the new attribute base > ', validator=NumberValidator()))
                    attr.base = new_base
                if attr_option == 'bonus':
                    new_bonus = Utils.str2int(prompt('what is the new attribute bonus > ', validator=NumberValidator()))
                    attr.bonus = new_bonus
        self.character.changed = True

    def modify_maxhp(self, character):
        maxhp = Utils.str2int(prompt('new max hp? > ', validator=NumberValidator()))
        character.max_hp = maxhp
        self.character.changed = True

    def modify_skills(self, character):
        skill_list = []
        for skill in character.skill_list:
            skill_list.append(skill.name)
        skill_to_modify = prompt('what skill? > ', completer=WordCompleter(skill_list), validator=WordValidator(skill_list))
        for skill in character.skill_list:
            if skill.name == skill_to_modify:
                opt_list = ['rank', 'bonus']
                skill_option = prompt(f'current skill rank is {skill.rank}, bonus is {skill.bonus}, for a total of {skill.total}. change rank or bonus? > ', completer=WordCompleter(opt_list), validator=WordValidator(opt_list))
                if skill_option == 'rank':
                    new_rank = Utils.str2int(prompt('what is the new skill rank? > ', validator=NumberValidator()))
                    skill.rank = new_rank
                if skill_option == 'bonus':
                    new_bonus = Utils.str2int(prompt('what is the new skill bonus? > ', validator=NumberValidator()))
                    skill.bonus = new_bonus
        self.character.changed = True

    def modify_user(self, character, console):
        opt_list = ['add', 'modify', 'list']
        user_option = prompt('add, modify, or list user element > ', completer=WordCompleter(opt_list), validator=WordValidator(opt_list))
        if user_option == 'add':
            with open (character.sheet, 'r') as f:
                existing_data = json.load(f)
                key_to_add = prompt('what to add to user space > ')
                existing_data['usr'][key_to_add] = []
            with open (character.sheet, 'w+') as outfile:
                json.dump(existing_data, outfile, indent=4)
            console.print(f'[bold green] UPDATED {character.name} [/bold green]')
        elif user_option == 'modify':
            with open (character.sheet, 'r') as f:
                existing_data = json.load(f)
                values = existing_data['usr'].keys()
                attr_to_update = prompt('what to update > ', completer=WordCompleter(values), validator=WordValidator(values))
                value_to_add = prompt('what value should we add > ')
                existing_data['usr'][attr_to_update].append(value_to_add)
            with open (character.sheet, 'w+') as outfile:
                json.dump(existing_data, outfile, indent=4)
            console.print(f'[bold green] UPDATED {character.name} [/bold green]')
        elif user_option == 'list':
            Utils.user_output(character, console)
        else:
            console.print('enter valid option')