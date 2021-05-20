from CRIT.toml_parser import TomlParser
import json
import os
import platform
import sys
from pathlib import Path
import traceback

from prompt_toolkit import HTML, PromptSession, prompt
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.completion.base import Completer
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.completion.word_completer import WordCompleter
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table


from CRIT import __version__
from CRIT.charutils import CharUtils
from CRIT.compat import clear, pause, set_terminal_size, set_terminal_title
from CRIT.config import Config
from CRIT.enums import Enums
from CRIT.toml_parser import TomlParser
from CRIT.validator import WordValidator
from CRIT.utils import Utils
from CRIT.loader import load_commands

if platform.system() == 'Windows':
    from ctypes import windll, wintypes

class DnDCompleter(Completer):
    '''
    Simple autocompletion on a list of words.
    :param base_commands: List of base commands.
    :param ignore_case: If True, case-insensitive completion.
    :param meta_dict: Optional dict mapping words to their meta-information.
    :param WORD: When True, use WORD characters.
    :param sentence: When True, don't complete by comparing the word before the
        cursor, but by comparing all the text before the cursor. In this case,
        the list of words is just a list of strings, where each string can
        contain spaces. (Can not be used together with the WORD option.)
    :param match_middle: When True, match not only the start, but also in the
                         middle of the word.
    '''

    def __init__(
        self,
        commands,
        ignore_case=False,
        meta_dict=None,
        WORD=False,
        sentence=False,
        match_middle=False,
    ):
        assert not (WORD and sentence)
        self.commands = commands
        self.base_commands = sorted(list(commands.keys()))
        self.ignore_case = ignore_case
        self.meta_dict = meta_dict or {}
        self.WORD = WORD
        self.sentence = sentence
        self.match_middle = match_middle

    def get_completions(self, document, complete_event):
        # Get word/text before cursor.
        if self.sentence:
            word_before_cursor = document.text_before_cursor
        else:
            word_before_cursor = document.get_word_before_cursor(WORD=self.WORD)

        if self.ignore_case:
            word_before_cursor = word_before_cursor.lower()

        def word_matcher(word):
            ''' True when the command before the cursor matches. '''
            if self.ignore_case:
                word = word.lower()

            if self.match_middle:
                return word_before_cursor in word
            else:
                return word.startswith(word_before_cursor)

        suggestions = []
        document_text_list = document.text.split(' ')

        if len(document_text_list) < 2:
            suggestions = self.base_commands

        elif document_text_list[0] in self.base_commands:
            command = self.commands[document_text_list[0]]
            suggestions = command.get_suggestions(document_text_list) or []

        for word in suggestions:
            if word_matcher(word):
                display_meta = self.meta_dict.get(word, '')
                yield Completion(
                    word, -len(word_before_cursor), display_meta=display_meta
                )

class TUI:
    def __init__(self):
        self.session = PromptSession(reserve_space_for_menu=6, complete_in_thread=True)
        self.console = None
        self.table = None
        self.os = platform.system()
        self.first_update = True
        self.character = None
        self.completer = None
        self.commands = None

    def start(self):
        self.startup_console()
        self.completer = NestedCompleter.from_nested_dict({
            'create': None
            , 'exit': None
            , 'load': None
            , 'help': None
        })
        clear()
        self.console.print(Rule(f'[bold green]Character Resources In Terminal[/bold green] [bold red]v{__version__}[/bold red]'))
        self.console.print('')
        try:
            with open('PermissionTest', 'w') as _:
                pass
            os.remove('PermissionTest')
        except IOError:
            self.console.print('[bold red]Character Resources In Terminal doesn\'t have write rights for the current directory.\n'
                               'Try starting it with administrative privileges.[/bold red]\n')
            pause()
            sys.exit(1)

        while True:
            try:
                command = self.session.prompt(HTML('<ansibrightgreen>CRIT></ansibrightgreen> '), completer=self.completer)
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            else:
                command = command.split(' ', 1)
                if getattr(self, f'c_{command[0].lower()}', False):
                    try:
                        getattr(self, f'c_{command[0].lower()}')(command[1].strip() if len(command) > 1 else False)
                    except Exception as e:
                        self.console.print(e)
                else:
                    self.console.print('Command not found.')

    def startup_console(self):
        if 'WINDIR' in os.environ and 'WT_SESSION' not in os.environ and 'ALACRITTY_LOG' not in os.environ:
            set_terminal_size(250, 75)
            windll.kernel32.SetConsoleScreenBufferSize(windll.kernel32.GetStdHandle(-11), wintypes._COORD(100, 200))
            self.console = Console(width=250)
        else:
            self.console = Console()

    ####  | | ___   __ _  __| | ___  __| |
    ####  | |/ _ \ / _` |/ _` |/ _ \/ _` |
    ####  | | (_) | (_| | (_| |  __/ (_| |
    ####  |_|\___/ \__,_|\__,_|\___|\__,_|

    def update(self):
        # items
        self.console.print('get item buffs')
        item_buffs = CharUtils.get_unique_item_buffs(self.character)

        self.console.print('updating Attributes')
        CharUtils.update_attributes(self.character, item_buffs)
            
        self.console.print('updating modifiers')
        for i in range(len(Enums.sizes)):
            if Enums.sizes[i] == self.character.size:
                self.character.size_mod = Enums.size_mods[i]
        
        self.console.print('updating AC')
        CharUtils.update_ac(self.character)

        self.console.print('updating saves')
        CharUtils.update_saves(self.character, item_buffs)

        # update bab/cmb/cmd
        if self.character.cmb_mod == 'strength':
            self.character.cmb = self.character.bab + self.character.strength.mod + self.character.size_mod
        if self.character.cmb_mod == 'dexterity':
            self.character.cmb = self.character.bab + self.character.dexterity.mod + self.character.size_mod
        self.character.cmd = 10 + self.character.bab + self.character.strength.mod + self.character.dexterity.mod + self.character.size_mod

        self.console.print('updating skills')
        CharUtils.update_skills(self.character, item_buffs)

        self.console.print('updating casting mod')
        if self.character.casting_stat == 'intelligence':
            self.character.casting_mod = self.character.intelligence.mod
        elif self.character.casting_stat == 'wisdom':
            self.character.casting_mod = self.character.wisdom.mod
        elif self.character.casting_stat == 'charisma':
            self.character.casting_mod = self.character.charisma.mod
        else:
            self.character.casting_mod = None

        if self.character.casting_stat:
            # get bonus spell data
            with open(Path(Config.data_path, 'spells', 'bonus.json'), 'r') as f:
                bonus_spells = json.load(f)

            self.console.print('updating spells')
            CharUtils.update_spells(self.character, bonus_spells)
        clear()
        self.console.print(Rule(f'[bold red]{self.character.name}[/bold red] the [bold green]{Utils.get_number_output(self.character.level)}[/bold green] level [bold blue]{self.character.class_}[/bold blue]'))
        self.character.changed = False

    def l_main_output(self):
        attr_table = Table(box=box.ROUNDED, title='ATTRIBUTES')
        save_table = Table(box=box.ROUNDED, title='SAVES')
        grid = Table.grid(expand=True)
        panel_grid = Table.grid()
        panel_grid.add_column(f'', justify='center',style='white',no_wrap=True)
        panel_grid.add_row(Panel.fit(f'[red]{self.character.hp}[/red]/{self.character.max_hp}',title='HP'),
                            Panel.fit(f'{self.character.bab}', title='BAB'), 
                            Panel.fit(f'{self.character.cmb}', title='CMB'), 
                            Panel.fit(f'{self.character.cmd}', title='CMD')
        )
        panel_grid.add_row(Panel.fit(f'{self.character.ac}', title='AC'),
                            Panel.fit(f'{self.character.touchac}', title='Touch AC'),
                            Panel.fit(f'{self.character.ffac}', title='FF AC')
        )

        attr_table.add_column(f'Attribute', justify='center', style='bright_red', no_wrap=True)
        attr_table.add_column(f'Value', justify='center', style='cyan', no_wrap=True)
        attr_table.add_column(f'Mod', justify='center', style='green', no_wrap=True)
        for attr in self.character.attr_list:
            attr_table.add_row(f'{attr.name}', f'{attr.total}', f'{attr.mod}')

        save_table.add_column(f'Save', justify='center', style='bright_red', no_wrap=True)
        save_table.add_column(f'Value', justify='center', style='cyan', no_wrap=True)
        for save in self.character.save_list:
            save_table.add_row(f'{save.name}', f'{save.total}')
        grid.add_column(justify='center')
        grid.add_column(justify='center')
        skill_table = Table(box=box.ROUNDED, title='SKILLS')
        skill_table.add_column('Skill', justify='center', style='bright_red', no_wrap=True)
        skill_table.add_column('Rank', justify='center', style='cyan', no_wrap=True)
        for skill in self.character.skill_list:
            skill_table.add_row(f'{skill.name}', f'{skill.total}')
        if self.character.spell_list:
            spell_table = Table(box=box.ROUNDED, title='SPELLS')
            spell_table.add_column(f'Level', justify='center', style='bright_red', no_wrap=True)
            spell_table.add_column(f'Save', justify='center', style='cyan', no_wrap=True)
            spell_table.add_column(f'Remaining', justify='center', style='green', no_wrap=True)
            for row in self.character.spell_list:
                if row.slots > 0:
                    spell_table.add_row(f'{row.level}', f'{row.save}', f'{row.remaining}/{row.slots}')
            grid.add_column(justify='center')
            grid.add_row(panel_grid, attr_table, save_table, skill_table, spell_table)
        else:
            grid.add_row(panel_grid, attr_table, save_table, skill_table)
        self.console.print(grid)
        self.last_output_state = 'main'

    ####    ___ ___  _ __ ___  _ __ ___   __ _ _ __   __| |___
    ####   / __/ _ \| '_ ` _ \| '_ ` _ \ / _` | '_ \ / _` / __|
    ####  | (_| (_) | | | | | | | | | | | (_| | | | | (_| \__ \
    ####   \___\___/|_| |_| |_|_| |_| |_|\__,_|_| |_|\__,_|___/

    # pre load
    def c_help(self, _):
        self.console.print(f'[bold blue]Press tab to autocomplete options at any menu. you may create or load a sheet, options change after load.[/bold blue]')

    def c_exit(self, _):
        if Utils.str2bool(prompt('Are you sure you want to quit > ', completer=WordCompleter(Enums.bool_choices), validator=WordValidator(Enums.bool_choices))):
            sys.exit(0)

    def c_create(self, _):
        Utils.character_creator(self.console)

    def c_load(self, _):
        if self.first_update == False:
            return
        sheets_path = Utils.get_options_from_dir(Config.sheets_path)
        if sheets_path == []:
            self.console.print('No sheets to load')
            return
        sheet_to_load = prompt('which sheet should we load? > ', completer=WordCompleter(sheets_path), validator=WordValidator(sheets_path))
        sheet_to_load = Path(Config.sheets_path, sheet_to_load, f'CRIT{sheet_to_load}.toml'.replace(' ', '_'))
        self.console.print('get character')
        self.character = TomlParser.load_character(sheet_to_load)
        self.console.print('setup attributes')
        CharUtils.setup_attributes(self.character)
        self.console.print('setup saves')
        CharUtils.setup_saves(self.character)
        self.first_update = False
        self.main_loop()

    #### _ __ ___   __ _(_)_ __   | | ___   ___  _ __
    ####| '_ ` _ \ / _` | | '_ \  | |/ _ \ / _ \| '_ \
    ####| | | | | | (_| | | | | | | | (_) | (_) | |_) |
    ####|_| |_| |_|\__,_|_|_| |_| |_|\___/ \___/| .__/
    ####                                        |_|

    def main_loop(self):
        load_commands(self.character, self.session, self.console)

        while True:
            try:
                if self.character.changed:
                    self.update()
                    self.l_main_output()
                user_input = self.session.prompt(HTML(f'<ansibrightgreen>{self.character.name} > </ansibrightgreen> '),
                completer=DnDCompleter(
                    commands=self.character.commands, ignore_case=True, match_middle=False
                ),
                auto_suggest=AutoSuggestFromHistory(),
                )
                if not user_input:
                    continue
                else:
                    user_input = user_input.split()

                command = self.character.commands.get(user_input[0]) or None
                if not command:
                    self.console.print('Unknown command.')
                    continue

                command.do_command(*user_input[1:])

                self.console.print()
            except (EOFError, KeyboardInterrupt):
                pass
            except Exception as e:
                traceback.print_exc()



if __name__ == '__main__':
    set_terminal_title(f'Character Resources In Terminal v{__version__}')
    os.chdir(os.path.dirname(os.path.abspath(sys.executable)))
    app = TUI()
    app.start()
