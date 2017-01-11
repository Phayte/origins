from evennia.utils import inherits_from

from typeclasses.exits import Exit


def is_exit(obj):
    return inherits_from(obj, Exit)