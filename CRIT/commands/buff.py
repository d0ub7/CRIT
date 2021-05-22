from CRIT import models
from CRIT.commands import Command
from CRIT.enums import Enums
from CRIT.utils import Utils
from CRIT.validator import WordValidator
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter


class Buff(Command):

    keywords = ['buff', 'debuff']
    help_text = '''{keyword}
{divider}
Summary: Change the character's buffs

Usage: {keyword} <verb>

Examples:

    {keyword} add
    {keyword} remove 
    {keyword} list
    {keyword} activate
    {keyword} deactivate
'''

    def do_command(self, *args): #TODO add proper args support
        mod_options = ['list', 'add', 'remove', 'activate', 'deactivate']
        modify_option = prompt(f'{mod_options} > ', 
                completer=WordCompleter(mod_options), 
                validator=WordValidator(mod_options)
        )

        if modify_option == 'list':
            self.list_buffs(self.character, self.console)

        if modify_option == 'add':
            self.add(self.character, self.console)

        if modify_option == 'remove':
            self.remove(self.character, self.console)

        if modify_option == 'activate':
            self.activate(self.character, self.console)

        if modify_option == 'deactivate':
            self.deactivate(self.character, self.console)
        
    def add(self, character, console):
        buff_name = prompt('what is the buff\'s name > ')
        mod_list = ['attribute', 'save', 'skill', 'ac', 'cmb', 'cmd']
        more = prompt('what does the buff modify? > ', 
                completer=WordCompleter(mod_list), 
                validator=WordValidator(mod_list)
        )

        buff_type = prompt('what type of bonus > ', 
                completer=WordCompleter(Enums.bonus_types), 
                validator=WordValidator(Enums.bonus_types)
        )

        bonus = {}

        while more != 'no':
            if more == 'ac':
                buff_attr = 'ac'

            if more == 'cmb':
                buff_attr = 'cmb'

            if more == 'cmd':
                buff_attr = 'cmd'

            if more == 'attribute':
                buff_attr = prompt(f'what {more} does the buff modify? > ', 
                        completer=WordCompleter(Enums.attributes), 
                        validator=WordValidator(Enums.attributes)
                )

            if more == 'save':
                sav_list = ['fortitude', 'reflex', 'will']
                buff_attr = prompt(f'what {more} does the buff modify? > ', 
                        completer=WordCompleter(sav_list), 
                        validator=WordValidator(sav_list)
                )

            if more == 'skill':
                skill_list = []
                for skill in character.skill_list:
                    skill_list.append(skill.name)
                buff_attr = prompt(f'what {more} does the buff modify? > ', 
                        completer=WordCompleter(skill_list), 
                        validator=WordValidator(skill_list)
                )

            howmuch_list = []
            for i in range(-99,99):
                howmuch_list.append(str(i))

            number_or_int = prompt('should we add a number or a mod? > ', 
                        completer=WordCompleter(['number', 'mod']), 
                        validator=WordValidator(['number', 'mod'])
            )

            if number_or_int == 'mod':
                buff_value = prompt(f'what mod to {more}? > ', 
                        completer=WordCompleter(Enums.attributes), 
                        validator=WordValidator(Enums.attributes)
                )

            if number_or_int == 'number':
                buff_value = Utils.str2int(prompt(f'how much? > ', 
                        completer=WordCompleter(howmuch_list), 
                        validator=WordValidator(howmuch_list)
                ))

            bonus[buff_attr] = {'value':  buff_value
                            , 'type': buff_type
            }

            more_list = ['attribute', 'save', 'skill', 'ac', 'cmb', 'cmd', 'no']
            more = prompt('does the buff modify anything else? > ', 
                    completer=WordCompleter(more_list), 
                    validator=WordValidator(more_list)
            )

        new_buff = models.Buff(name = buff_name
                    , active = False
                    , bonus = bonus
        )

        console.print(new_buff)
        if Utils.str2bool(prompt(f'create? > ', 
                completer=WordCompleter(Enums.bool_choices), 
                validator=WordValidator(Enums.bool_choices)
        )):

            character.buff_list.append(new_buff)

    def list_buffs(self, character, console):
        for buff in character.buff_list:
            console.out(buff) # print stopped working as the object got more complex

    def remove(self, character, console):
        buff_list = []
        for buff in character.buff_list:
            buff_list.append(buff.name)
        
        buff_to_remove = prompt('remove which buff > ', 
                        completer=WordCompleter(buff_list), 
                        validator=WordValidator(buff_list)
        )

        for buff in character.buff_list:
            if buff.name == buff_to_remove:
                console.print(f'removing {buff_to_remove}')
                character.buff_list.remove(buff)

    def activate(self, character, console):
        buff_list = []
        for buff in character.buff_list:
            if buff.active == False:
                buff_list.append(buff.name)

        if buff_list == []:
            console.print('no buffs to activate')
            return
        
        buff_to_activate_name = prompt('activate which buff? > ', 
                completer=WordCompleter(buff_list), 
                validator=WordValidator(buff_list)
        )

        buff_to_activate = {}
        for buff in character.buff_list:
            if buff.name == buff_to_activate_name:
                buff_to_activate = buff

        for buff in character.buff_list:
            if buff.name == buff_to_activate.name:
                buff.active = True
                self.character.changed = True

    def deactivate(self, character, console):
        buff_list = []
        for buff in character.buff_list:
            if buff.active == True:
                buff_list.append(buff.name)
        
        if buff_list == []:
            console.print('no buffs to deactivate')
            return

        buff_to_deactivate_name = prompt('deactivate which buff? > ', 
                completer=WordCompleter(buff_list), 
                validator=WordValidator(buff_list)
        )

        for buff in character.buff_list:
            if buff.name == buff_to_deactivate_name:
                buff.active = False
                self.character.changed = True
