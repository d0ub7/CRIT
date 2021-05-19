from dataclasses import dataclass

@dataclass
class Ac:
    ac: None
    type_: None
    acp: None
    dex_mod: None

@dataclass
class Attribute:
    name: None
    total: None
    bonus: None
    base: None
    item: None
    mod: None

class Character:
    def __init__(self) -> None:
        #### CHARACTER
        self.hp = 0
        self.max_hp = 99
        self.name = None
        self.class_ = None
        self.bab = 0
        self.cmb = 0
        self.cmd = 0
        self.size = None
        self.size_mod = 0
        self.skills_type = None
        self.bonus_spells = None
        self.cmb_mod = 'strength'

        self.ac = 0
        self.ffac = 0
        self.touchac = 0
        self.acp = 0
        self.dex_mod = 99

        self.sheet = None

        self.casting_stat = None
        self.casting_mod = None

        self.strength = None
        self.dexterity = None
        self.constitution = None
        self.intelligence = None
        self.wisdom = None
        self.charisma = None

        self.fortitude = None
        self.dexterity = None
        self.will = None

        self.item_list = []
        self.spell_list = []
        self.attr_list = []
        self.skill_list = []
        self.save_list = []
        self.feat_list = []
    
        self.commands = {}

        self.changed = True

@dataclass
class Item:
    name: None
    equipped: False
    slot: None
    ac: None
    acp: None
    dex_mod: None
    ac_type: None
    bonus: None

@dataclass
class Mod:
    stat: None
    type_: None
    value: None

@dataclass
class Save:
    name: None
    total: None
    ability: None
    bonus: None
    base: None
    item: None

@dataclass
class Skill:
    name: None
    total: None
    ability: None
    rank: None
    bonus: None
    class_: None
    item: None

@dataclass
class Spell:
    level: None
    save: None
    slots: None
    remaining: None
    base: None

@dataclass
class Weapon:
    name: None
    equipped: False
    ddice: None
    dtype: None
    bonus: None