import string
import random
from rich.terminal_theme import TerminalTheme

__version__ = '0.4.1'
__license__ = 'GPLv3'
__copyright__ = '2020, d0ub7'
__docformat__ = 'restructuredtext en'

HEADERS = {'User-Agent': f'CRIT-{"".join(random.choices(string.ascii_uppercase + string.digits, k=10))}/{__version__}'}
HEADLESS_TERMINAL_THEME = TerminalTheme(
    (0, 0, 0),
    (255, 255, 255),
    [
        (0, 0, 0),
        (128, 0, 0),
        (0, 128, 0),
        (128, 128, 0),
        (0, 0, 128),
        (128, 0, 128),
        (0, 128, 128),
        (192, 192, 192),
    ],
    [
        (128, 128, 128),
        (255, 0, 0),
        (0, 255, 0),
        (255, 255, 0),
        (0, 0, 255),
        (255, 0, 255),
        (0, 255, 255),
        (255, 255, 255),
    ],
)