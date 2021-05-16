from dataclasses import dataclass
from CRIT.mod import Mod, Ac
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

    @staticmethod
    def get_unique_item_buffs(character):
        unique_item_buffs = []
        item_buffs = []
        for item in character.item_list:
            if item.equipped is True:
                for bonus in item.bonus:
                    item_buffs.append(Mod(
                                    stat = item.bonus[bonus]['stat']
                                    , type_ = item.bonus[bonus]['type']
                                    , value = item.bonus[bonus]['value']
                    ))
        buffdict = {}
        for buff in item_buffs:
            if buff.stat + buff.type_ in buffdict.keys():
                if buff.value > buffdict[f'{buff.stat}_{buff.type}']:
                    buffdict[f'{buff.stat}_{buff.type_}'] = buff.value
                else:
                    pass
            else:
                buffdict[f'{buff.stat}_{buff.type_}'] = buff.value
        for buff, value in buffdict.items():
            unique_item_buffs.append(Mod(stat = buff.split('_')[0]
                                , type_ = buff.split('_')[1]
                                , value = value
                                ))
        return unique_item_buffs
    
    @staticmethod
    def get_unique_ac_buffs(character):
        ac_buffs = []
        for item in character.item_list:
            if item.equipped is True:
                if item.ac != 0:
                    ac_buffs.append(Ac(ac = item.ac
                                    , type_ = item.ac_type
                                    , acp = item.acp
                                    , dex_mod = item.dex_mod
                    ))
        acdict = {}
        for buff in ac_buffs:
            if buff.type_ in acdict.keys():
                if buff.ac > acdict[f'{buff.type}']:
                    acdict[f'{buff.type_}'] = buff.ac
                else:
                    pass
            else:
                acdict[f'{buff.type_}'] = buff.ac

        for buff in ac_buffs:
            if buff.type_ in acdict.keys() and buff.ac not in acdict.values():
                ac_buffs.remove(buff)
        
        return ac_buffs