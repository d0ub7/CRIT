from dataclasses import dataclass
from os import stat

@dataclass
class Spell:
    level: None
    save: None
    slots: None
    remaining: None
    base: None

    @staticmethod
    def update(character, bonus_spells):
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