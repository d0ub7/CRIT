from dataclasses import dataclass

@dataclass
class Save:
    name: None
    total: None
    ability: None
    bonus: None
    base: None
    item: None

    @staticmethod
    def update(character, item_buffs):
        for save in character.save_list:
            save.item = 0
            for buff in item_buffs:
                if buff.stat == save.name:
                    save.item += buff.value
        character.fortitude.total = character.fortitude.base + character.constitution.mod + character.fortitude.bonus + character.fortitude.item
        character.reflex.total = character.reflex.base + character.dexterity.mod + character.reflex.bonus + character.reflex.item
        character.will.total = character.will.base + character.wisdom.mod + character.will.bonus + character.will.item

    @staticmethod
    def setup(character):
        for sav in character.save_list:
            if sav.name == 'fortitude':
                character.fortitude = Save(name = 'fortitude'
                                        , total = sav.total
                                        , ability = sav.ability
                                        , bonus = sav.bonus
                                        , base = sav.base
                                        , item = 0)
            if sav.name == 'reflex':
                character.reflex = Save(name = 'reflex'
                                        , total = sav.total
                                        , ability = sav.ability
                                        , bonus = sav.bonus
                                        , base = sav.base
                                        , item = 0)
            if sav.name == 'will':
                character.will = Save(name = 'will'
                                        , total = sav.total
                                        , ability = sav.ability
                                        , bonus = sav.bonus
                                        , base = sav.base
                                        , item = 0)

                character.save_list = [character.fortitude
                                    , character.reflex
                                    , character.will]