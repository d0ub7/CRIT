from CRIT.commands import Command


class Rest(Command):

    keywords = ['rest']
    help_text = '''{keyword}
{divider}
Summary: Increment HP based on level and replenish
spell slots as appropriate

Usage: {keyword}

Examples:

    {keyword}
'''

    def do_command(self, *args):
        self.character.hp += 2*self.character.level
        if self.character.hp > self.character.max_hp:
            self.character.hp = self.character.max_hp
        
        if self.character.spell_list:
            for spell in self.character.spell_list:
                spell.remaining = spell.slots

        self.character.changed = True