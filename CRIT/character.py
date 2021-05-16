class Character:
    def __init__(self) -> None:
        #### CHARACTER
        self.hp = 0
        self.max_hp = 99
        self.char_name = None
        self.char_class = None
        self.char_bab = 0
        self.char_cmb = 0
        self.char_cmd = 0
        self.char_size = None
        self.size_mod = 0
        self.skills_type = None
        self.bonus_spells = None
        self.cmb_mod = 'strength'
        self.acp_mod = 0

        self.casting_stat = None
        self.casting_mod = None
        self.str_mod = 0
        self.dex_mod = 0
        self.con_mod = 0
        self.int_mod = 0
        self.wis_mod = 0
        self.cha_mod = 0

        self.item_list = []
        self.spell_list = []
        self.attr_list = []
        self.skill_list = []
        self.save_list = []

