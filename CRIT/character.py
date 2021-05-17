from CRIT.attribute import Attribute
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
    