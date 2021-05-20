import json
import os
import sys
from pathlib import PurePath
from prompt_toolkit import prompt

from CRIT.models import Attribute, Character, Item, Save, Skill, Spell
from CRIT.config import Config

#### DEPRECATED
#### USE TOML PARSER
class JsonParser:
    @staticmethod
    def load_character(sheet_to_load):
        with open(sheet_to_load, 'r') as f:
            char_data = json.load(f)
            character = Character()
            character.hp = char_data['hp']
            character.max_hp = char_data['max_hp']
            character.name = char_data['name']
            character.class_ = char_data['class']
            character.level = char_data['level']
            character.bab = char_data['bab']
            character.size = char_data['size']
            character.skills_type = char_data['skills_type']
            character.casting_stat = char_data['casting_stat'] if char_data['casting_stat'] else None
            
            if char_data['feats']:
                for feat in char_data['feats']:
                    character.feat_list.append(feat) 
                # if 'agile maneuvers' in (feat.lower() for feat in char_data['feats']): TODO: move this to update
                #     character.cmb_mod = 'dexterity'

            for name, attr in char_data['attributes'].items():
                character.attr_list.append(Attribute(name = name
                                                , total = attr['total']
                                                , bonus = attr['bonus']
                                                , base = attr['base']
                                                , item = 0
                                                , mod = 0))

            for name, itm in char_data['items'].items():
                character.item_list.append(Item(name = name
                                                , equipped = itm['equipped']
                                                , slot = itm['slot']
                                                , ac = itm['ac']
                                                , acp = itm['acp']
                                                , dex_mod = itm['dex_mod']
                                                , ac_type = itm['ac_type']
                                                , bonus = itm['bonus']))

            for name, sav in char_data['saves'].items():
                character.save_list.append(Save(name = name 
                                                , total = sav['total']
                                                , ability = sav['ability']
                                                , bonus = sav['bonus']
                                                , base = sav['base']
                                                , item = 0))


            for name, skil in char_data['skills'].items():
                character.skill_list.append(Skill(name = name
                                                , total = skil['total']
                                                , ability = skil['ability']
                                                , rank = skil['rank']
                                                , bonus = skil['bonus']
                                                , class_ = skil['class_']
                                                , item = 0))

            for level, spel in char_data['spells'].items():
                character.spell_list.append(Spell(level = int(level)
                                                , save = spel['save']
                                                , slots = spel['slots']
                                                , remaining = spel['remaining']
                                                , base = spel['base']))

        return character

    @staticmethod
    def save_character(character): #TODO make character completely json serializable
        try: 
            char_data = {}
            char_data['name'] = character.name
            char_data['class'] = character.class_
            char_data['level'] = character.level
            char_data['hp'] = character.hp
            char_data['max_hp'] = character.max_hp
            char_data['bab'] = character.bab
            char_data['casting_stat'] = character.casting_stat
            char_data['size'] = character.size
            char_data['skills_type'] = character.skills_type

            char_data['attributes'] = {}
            for attr in character.attr_list:
                char_data['attributes'][attr.name] = {
                    'total': attr.total
                    , 'bonus': attr.bonus
                    , 'base': attr.base
                }

            char_data['saves'] = {}
            for save in character.save_list:
                char_data['saves'][save.name] = {
                    'total': save.total
                    , 'ability': save.ability
                    , 'bonus': save.bonus
                    , 'base': save.base
                }

            char_data['items'] = {}
            for item in character.item_list:
                char_data['items'][item.name] = {
                        'name': item.name
                        , 'equipped': item.equipped
                        , 'slot': item.slot
                        , 'ac': item.ac
                        , 'acp': item.acp
                        , 'dex_mod': item.dex_mod
                        , 'ac_type': item.ac_type
                        , 'bonus': item.bonus
                }

            char_data['skills'] = {}
            for skill in character.skill_list:
                char_data['skills'][skill.name] = {
                    'total': skill.total
                    , 'ability': skill.ability
                    , 'rank': skill.rank
                    , 'bonus': skill.bonus
                    , 'class_': skill.class_
                }

            char_data['spells'] = {}
            if character.spell_list:
                for spell in character.spell_list:
                    char_data['spells'][spell.level] = {
                        'save': spell.save
                        , 'slots': spell.slots
                        , 'remaining': spell.remaining
                        , 'base': spell.base
                    }
            
            char_data['feats'] = character.feat_list

            char_file = PurePath(f'{Config.sheets_path}', character.name, f'CRIT{character.name}.json'.replace(' ', '_'))
            really = True
            if os.path.isfile(char_file):
                really = prompt(f'sheet for {character.name} exists, overwrite? > ')
            if not really:
                return
            else:
                with open(char_file, 'r+') as f:
                    existing_data = json.load(f)
                    char_data['usr'] = existing_data['usr']
                    char_data['feats'] = existing_data['feats']
                with open(char_file, 'w') as outfile:
                    json.dump(char_data, outfile, indent=4)
                    print(f'UPDATED {character.name}')
                sys.exit(0)
        except Exception as e:
            raise RuntimeError