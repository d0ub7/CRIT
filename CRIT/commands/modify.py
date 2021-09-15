from CRIT.commands import Command
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from CRIT.utils import Utils
from CRIT.enums import Enums
from CRIT.validator import NumberValidator, WordValidator


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
            mod_list = ['maxhp', 'skill', 'attribute', 'save', 'cmb_mod', 'size']
            modify_option = prompt('modify > ', 
                    completer=WordCompleter(mod_list), 
                    validator=WordValidator(mod_list)
            )

        else:
            try:
                modify_option = args

            except:
                pass

        if modify_option == 'maxhp':
            self.modify_maxhp(self.character)

        if modify_option == 'skill':
            self.modify_skills(self.character)

        if modify_option == 'attribute':
            self.modify_attribute(self.character)
        
        if modify_option == 'save':
            self.modify_saves(self.character)
        
        if modify_option == 'size':
            new_size = prompt('What size are you now? > ',
                        completer=WordCompleter(Enums.sizes),
                        validator=WordValidator(Enums.sizes)
            )
            self.character.size = new_size
            self.character.changed = True
            
        if modify_option == 'cmb_mod':
            new_cmb_mod = prompt(f'cmb mod is currently {self.character.cmb_mod}, what should it be? > ',
                    completer=WordCompleter(Enums.attributes),
                    validator=WordValidator(Enums.attributes)
            )

            self.character.cmb_mod = new_cmb_mod
            self.self.character.changed = True
        
    def modify_attribute(self, character):
        attr_to_modify = prompt('which attribute? > ', 
                completer=WordCompleter(Enums.attributes), 
                validator=WordValidator(Enums.attributes)
        )

        for attr in character.attr_list:
            if attr.name == attr_to_modify:
                opt_list = ['base', 'bonus']
                attr_option = prompt(f'current attribute base is {attr.base}, bonus is {attr.bonus}, for a total of {attr.total}. change base or bonus? > ', 
                        completer=WordCompleter(opt_list), 
                        validator=WordValidator(opt_list)
                )

                if attr_option == 'base':
                    new_base = Utils.str2int(prompt('what is the new attribute base > ', 
                            validator=NumberValidator()
                    ))

                    attr.base = new_base

                if attr_option == 'bonus':
                    new_bonus = Utils.str2int(prompt('what is the new attribute bonus > ', 
                            validator=NumberValidator()
                    ))

                    attr.bonus = new_bonus

        character.changed = True

    def modify_maxhp(self, character):
        maxhp = Utils.str2int(prompt('new max hp? > ', 
                validator=NumberValidator()
        ))

        character.max_hp = maxhp
        character.changed = True

    def modify_skills(self, character):
        skill_list = []
        for skill in character.skill_list:
            skill_list.append(skill.name)
            
        skill_choice = prompt('modify class skills or an individual one? > ',
                completer=WordCompleter(['class', 'individual']),
                validator=WordValidator(['class', 'individual'])
        )

        if skill_choice == 'class':
            class_skills = []

            for skill in character.skill_list:
                if skill.class_ == True:
                    class_skills.append(skill.name)

            add_or_remove = prompt('add or remove a class skill > ',
                    completer=WordCompleter(['add', 'remove']),
                    validator=WordValidator(['add', 'remove'])
            )

            if add_or_remove == 'add':
                for skill in class_skills:
                    skill_list.remove(skill)
                skill_to_add = prompt('which skill should we add? > ',
                        completer=WordCompleter(skill_list),
                        validator=WordValidator(skill_list)
                )

                for skill in character.skill_list:
                    if skill.name == skill_to_add:
                        skill.class_ = True



            if add_or_remove == 'remove':

                skill_to_remove = prompt('which skill should we remove? > ',
                        completer=WordCompleter(class_skills),
                        validator=WordValidator(class_skills)
                )

                for skill in character.skill_list:
                    if skill.name == skill_to_remove:
                        skill.class_ = False
            
            character.changed = True

        if skill_choice == 'individual':

            skill_to_modify = prompt('what skill? > ', 
                    completer=WordCompleter(skill_list), 
                    validator=WordValidator(skill_list)
            )
            
            for skill in character.skill_list:
                if skill.name == skill_to_modify:
                    opt_list = ['rank', 'bonus']
                    skill_option = prompt(f'current skill rank is {skill.rank}, bonus is {skill.bonus}, for a total of {skill.total}. change rank or bonus? > ', 
                            completer=WordCompleter(opt_list), 
                            validator=WordValidator(opt_list)
                    )

                    if skill_option == 'rank':
                        new_rank = Utils.str2int(prompt('what is the new skill rank? > ', 
                                validator=NumberValidator()
                        ))

                        skill.rank = new_rank

                    if skill_option == 'bonus':
                        new_bonus = Utils.str2int(prompt('what is the new skill bonus? > ', 
                                validator=NumberValidator()
                        ))

                        skill.bonus = new_bonus

            character.changed = True
    
    def modify_saves(self, character):
        saves_list = []
        for sav in character.save_list:
            saves_list.append(sav.name)
        
        save_to_modify = prompt('what save? > ',
                completer=WordCompleter(saves_list),
                validator=WordValidator(saves_list)
        )

        for sav in character.save_list:
            if sav.name == save_to_modify:
                print(f'current save base is {sav.base}, bonus is {sav.bonus}, for a total of {sav.total}')
                new_bonus = Utils.str2int(prompt('what is the new save bonus? > ',
                        validator=NumberValidator()
                ))
                
                sav.bonus = new_bonus

        character.changed = True
