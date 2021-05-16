from dataclasses import dataclass
from CRIT.utils import Utils

@dataclass
class Attribute:
    name: None
    total: None
    bonus: None
    base: None
    item: None
    mod: None

    @staticmethod
    def update(character, item_buffs):
        for attr in character.attr_list:
            attr.item = 0
            for buff in item_buffs:
                if buff.stat == attr.name:
                    attr.item += buff.value
            attr.total = attr.base + attr.bonus + attr.item
            attr.mod = Utils.get_mod(attr.total)
    
    @staticmethod
    def setup(character):
        for attribute in character.attr_list:
            if attribute.name == 'strength':
                character.strength = Attribute(name = 'strength'
                                        , total = attribute.total
                                        , bonus = attribute.bonus
                                        , base = attribute.base
                                        , item = 0
                                        , mod = 0)
            if attribute.name == 'dexterity':
                character.dexterity = Attribute(name = 'dexterity'
                                        , total = attribute.total
                                        , bonus = attribute.bonus
                                        , base = attribute.base
                                        , item = 0
                                        , mod = 0)
            if attribute.name == 'constitution':
                character.constitution = Attribute(name = 'constitution'
                                        , total = attribute.total
                                        , bonus = attribute.bonus
                                        , base = attribute.base
                                        , item = 0
                                        , mod = 0)
            if attribute.name == 'intelligence':
                character.intelligence = Attribute(name = 'intelligence'
                                        , total = attribute.total
                                        , bonus = attribute.bonus
                                        , base = attribute.base
                                        , item = 0
                                        , mod = 0)
            if attribute.name == 'wisdom':
                character.wisdom = Attribute(name = 'wisdom'
                                        , total = attribute.total
                                        , bonus = attribute.bonus
                                        , base = attribute.base
                                        , item = 0
                                        , mod = 0)
            if attribute.name == 'charisma':
                character.charisma = Attribute(name = 'charisma'
                                        , total = attribute.total
                                        , bonus = attribute.bonus
                                        , base = attribute.base
                                        , item = 0
                                        , mod = 0)
            character.attr_list = [character.strength
                                , character.dexterity
                                , character.constitution
                                , character.intelligence
                                , character.wisdom
                                , character.charisma]