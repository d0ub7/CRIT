from .models import Attribute, Mod, Save, Ac
from .enums import Enums
from .utils import Utils


class CharUtils:

    @staticmethod
    def get_unique_ac_buffs(character):
        ''' 
        return a list of `Ac` objects from
        items and buffs as a single list
        '''
        ac_buffs = []
        for item in character.item_list:
            if item.equipped is True:
                for name, ac in item.ac.items():
                    ac_buffs.append(Ac(ac = ac['ac']
                                    , type_ = name
                                    , acp = ac['acp']
                                    , dex_mod = ac['dex_mod']
                    ))

        for buff in character.buff_list:
            if buff.active is True:
                for name, bonus in buff.bonus.items():
                    if name == 'ac':
                        ac_buffs.append(Ac(ac = bonus['value']
                                        , type_ = bonus['type']
                                        , acp = 0
                                        , dex_mod = 0
                        ))

        acdict = {}
        for buff in ac_buffs:
            if buff.type_ in acdict.keys():
                if isinstance(buff.value, str):
                    acdict[f'{buff.type_}'] = buff.ac

                if buff.ac > acdict[f'{buff.type}']:
                    acdict[f'{buff.type_}'] = buff.ac

                else:
                    pass

            else:
                acdict[f'{buff.type_}'] = buff.ac

        for buff in ac_buffs:
            if buff.type_ in acdict.keys() and buff.ac not in acdict.values():
                ac_buffs.remove(buff)
        
        print(ac_buffs)
        return ac_buffs

    @staticmethod
    def get_unique_buffs(character):
        '''
        return a lit of `Mod` objects from both
        items and buffs as a single list
        '''
        unique_buffs = []
        item_buffs = []
        for item in character.item_list:
            if item.equipped is True:
                for name, bonus in item.bonus.items():
                    item_buffs.append(Mod(
                                    stat = name
                                    , type_ = bonus['type']
                                    , value = bonus['value']
                    ))

        for buff in character.buff_list:
            if buff.active is True:
                for name, bonus in buff.bonus.items():
                    item_buffs.append(Mod(
                                    stat = name
                                    , type_ = bonus['type']
                                    , value = bonus['value']
                    ))

        buffdict = {}
        mod_buffdict = {}
        for buff in item_buffs:
            if buff.stat + buff.type_ in buffdict.keys():
                if isinstance(buff.value, str):
                    mod_buffdict[f'{buff.stat}_{buff.type}'] = buff.value

                if buff.value > buffdict[f'{buff.stat}_{buff.type}']:
                    buffdict[f'{buff.stat}_{buff.type_}'] = buff.value

                else:
                    pass

            else:
                buffdict[f'{buff.stat}_{buff.type_}'] = buff.value

        for buff, value in buffdict.items():
            unique_buffs.append(Mod(stat = buff.split('_')[0]
                                , type_ = buff.split('_')[1]
                                , value = value
                                ))

        return unique_buffs

    @staticmethod
    def setup_attributes(character):
        '''
        create the attr_list in the character class as a
        list of `Attribute` objects
        '''
        for attribute in character.attr_list:
            if attribute.name == 'strength':
                character.strength = Attribute(name = 'strength'
                                        , total = attribute.total
                                        , bonus = attribute.bonus
                                        , base = attribute.base
                                        , buff = 0
                                        , mod = 0
                )

            if attribute.name == 'dexterity':
                character.dexterity = Attribute(name = 'dexterity'
                                        , total = attribute.total
                                        , bonus = attribute.bonus
                                        , base = attribute.base
                                        , buff = 0
                                        , mod = 0
                )

            if attribute.name == 'constitution':
                character.constitution = Attribute(name = 'constitution'
                                        , total = attribute.total
                                        , bonus = attribute.bonus
                                        , base = attribute.base
                                        , buff = 0
                                        , mod = 0
                )

            if attribute.name == 'intelligence':
                character.intelligence = Attribute(name = 'intelligence'
                                        , total = attribute.total
                                        , bonus = attribute.bonus
                                        , base = attribute.base
                                        , buff = 0
                                        , mod = 0
                )

            if attribute.name == 'wisdom':
                character.wisdom = Attribute(name = 'wisdom'
                                        , total = attribute.total
                                        , bonus = attribute.bonus
                                        , base = attribute.base
                                        , buff = 0
                                        , mod = 0
                )

            if attribute.name == 'charisma':
                character.charisma = Attribute(name = 'charisma'
                                        , total = attribute.total
                                        , bonus = attribute.bonus
                                        , base = attribute.base
                                        , buff = 0
                                        , mod = 0
                )

            character.attr_list = [character.strength
                                , character.dexterity
                                , character.constitution
                                , character.intelligence
                                , character.wisdom
                                , character.charisma]

    @staticmethod
    def setup_saves(character):
        '''
        create the save_list in the character class
        as a list of `save` objects
        '''
        for sav in character.save_list:
            if sav.name == 'fortitude':
                character.fortitude = Save(name = 'fortitude'
                                        , total = sav.total
                                        , ability = sav.ability
                                        , bonus = sav.bonus
                                        , base = sav.base
                                        , buff = 0
                )

            if sav.name == 'reflex':
                character.reflex = Save(name = 'reflex'
                                        , total = sav.total
                                        , ability = sav.ability
                                        , bonus = sav.bonus
                                        , base = sav.base
                                        , buff = 0
                )

            if sav.name == 'will':
                character.will = Save(name = 'will'
                                        , total = sav.total
                                        , ability = sav.ability
                                        , bonus = sav.bonus
                                        , base = sav.base
                                        , buff = 0
                )

                character.save_list = [character.fortitude
                                    , character.reflex
                                    , character.will]

    @staticmethod
    def update_ac(character):
        '''
        set ac, ffac, and touchac members of character
        '''
        ac_buffs = CharUtils.get_unique_ac_buffs(character)
        total_buff_ac = 0
        total_buff_touch_ac = 0
        total_buff_ff_ac = 0
        for buff in ac_buffs:
            if isinstance(buff.ac, str):
                if buff.ac == 'strength':
                    total_buff_ac += character.strength.mod
                    total_buff_touch_ac += character.strength.mod
                    total_buff_ff_ac += character.strength.mod
                    continue

                if buff.ac == 'dexterity':
                    total_buff_ac += character.dexterity.mod
                    total_buff_touch_ac += character.dexterity.mod
                    total_buff_ff_ac += character.dexterity.mod
                    continue

                if buff.ac == 'constitution':
                    total_buff_ac += character.constitution.mod
                    total_buff_touch_ac += character.constitution.mod
                    total_buff_ff_ac += character.constitution.mod
                    continue

                if buff.ac == 'intelligence':
                    total_buff_ac += character.intelligence.mod
                    total_buff_touch_ac += character.intelligence.mod
                    total_buff_ff_ac += character.intelligence.mod
                    continue

                if buff.ac == 'wisdom':
                    total_buff_ac += character.wisdom.mod
                    total_buff_touch_ac += character.wisdom.mod
                    total_buff_ff_ac += character.wisdom.mod
                    continue

                if buff.ac == 'charisma':
                    total_buff_ac += character.charisma.mod
                    total_buff_touch_ac += character.charisma.mod
                    total_buff_ff_ac += character.charisma.mod
                    continue

            if buff.type_ in Enums.touchac_types:
                total_buff_touch_ac += buff.ac

            if buff.type_ in Enums.ffac_types:
                total_buff_ff_ac += buff.ac

            if buff.dex_mod != -1:
                character.dex_mod = buff.dex_mod if character.dex_mod > buff.dex_mod else character.dex_mod

            character.acp = buff.acp if character.acp > buff.acp else character.acp
            total_buff_ac += buff.ac
        

        dex_to_ac = character.dexterity.mod if character.dex_mod > character.dexterity.mod else character.dex_mod
        character.ac = 10 - character.size_mod + dex_to_ac + total_buff_ac
        character.ffac = 10 - character.size_mod + total_buff_ff_ac
        character.touchac = 10 - character.size_mod + dex_to_ac + total_buff_touch_ac

    @staticmethod
    def update_cmx(character, item_buffs):
        '''
        update cmd and cmd members of character
        '''
        for attr in character.attr_list:
            if character.cmb_mod == attr.name:
                character.cmb = character.bab + attr.mod + character.size_mod
        character.cmd = 10 + character.bab + character.strength.mod + character.dexterity.mod + character.size_mod

        for buff in item_buffs:
            if buff.stat == 'cmb':
                if isinstance(buff.value, str):
                    for attr in character.attr_list:
                        if buff.value == attr.name:
                            character.cmb += attr.mod
                if isinstance(buff.value, int):
                    character.cmb += buff.value

            if buff.stat == 'cmd':
                if isinstance(buff.value, str):
                    for attr in character.attr_list:
                        if buff.value == attr.name:
                            character.cmd += attr.mod

                if isinstance(buff.value, int):
                    character.cmd += buff.value

    @staticmethod
    def update_attributes(character, item_buffs):
        '''
        update all attribute members of character
        from the buffs member of the attribute class
        '''
        for attr in character.attr_list:
            attr.buff = 0
            for buff in item_buffs:
                if buff.stat == attr.name:
                    if isinstance(buff.value, str):
                        for attr in character.attr_list:
                            if buff.value == attr.name:
                                attr.buff += attr.mod

                    if isinstance(buff.value, int):
                        attr.buff += buff.value

            attr.total = attr.base + attr.bonus + attr.buff
            attr.mod = Utils.get_mod(attr.total)

    @staticmethod
    def update_skills(character, item_buffs):
        '''
        update skills in skill_list from applicable
        attributes as well as the buffs and bonuses
        of each skill
        '''
        for skill in character.skill_list:
            skill.buff = 0
            for buff in item_buffs:
                if buff.stat == skill.name:
                    if isinstance(buff.value, str):
                        for attr in character.attr_list:
                            if buff.value == attr.name:
                                skill.buff += attr.mod

                    if isinstance(buff.value, int):
                        skill.buff += buff.value

            skill.total = 0
            if skill.rank > 0:
                skill.total += skill.rank
                if skill.class_:
                    skill.total += 3

            if skill.ability == 'strength':
                skill.total += character.strength.mod
                skill.total += character.acp

            if skill.ability == 'dexterity':
                skill.total += character.dexterity.mod
                skill.total += character.acp

            if skill.ability == 'constitution':
                skill.total += character.constitution.mod

            if skill.ability == 'intelligence':
                skill.total += character.intelligence.mod

            if skill.ability == 'wisdom':
                skill.total += character.wisdom.mod

            if skill.ability == 'charisma':
                skill.total += character.charisma.mod
            
            skill.total += skill.bonus
            skill.total += skill.buff

    @staticmethod
    def update_spells(character, bonus_spells):
        '''
        update spells based on your casting stat
        mod and the saves associated with each
        spell level
        '''
        current_casting_mod = 16 if character.casting_mod > 16 else character.casting_mod
        if character.casting_mod == None or character.casting_mod < 0:
            character.spell_list = None

        elif character.casting_mod == 0:
            # no bonus spells
            for spel in character.spell_list:
                if spel.base != 0:
                    spel.save = 10 + spel.level
                    spel.slots = spel.base

        else:
            # get bonus spells
            for spel in character.spell_list:
                if spel.base != 0:
                    spel.save = 10 + spel.level + current_casting_mod
                    spel.slots = bonus_spells[str(current_casting_mod)][spel.level-1] + spel.base
    
    @staticmethod
    def update_saves(character, item_buffs):
        '''
        update saves in save_list from applicable
        attributes as well as the buffs and bonuses
        of each save
        '''
        for save in character.save_list:
            save.buff = 0
            for buff in item_buffs:
                if buff.stat == save.name:
                    if isinstance(buff.value, str):
                        for attr in character.attr_list:
                            if buff.value == attr.name:
                                save.buff += attr.mod

                    if isinstance(buff.value, int):
                        save.buff += buff.value

        character.fortitude.total = character.fortitude.base + character.constitution.mod + character.fortitude.bonus + character.fortitude.buff
        character.reflex.total = character.reflex.base + character.dexterity.mod + character.reflex.bonus + character.reflex.buff
        character.will.total = character.will.base + character.wisdom.mod + character.will.bonus + character.will.buff