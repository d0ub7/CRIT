from dataclasses import dataclass

@dataclass
class Skill:
    name: None
    total: None
    ability: None
    rank: None
    bonus: None
    class_: None
    item: None

    @staticmethod
    def update(character, item_buffs):
        # update skills
        for skill in character.skill_list:
            skill.item = 0
            for buff in item_buffs:
                if buff.stat == skill.name:
                    skill.item += buff.value
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
            skill.total += skill.item