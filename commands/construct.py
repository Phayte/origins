from evennia.utils.evmenu import EvMenu

from commands.command import Command


class CmdEngineer(Command):
    key = "engineer"
    help_category = "Constructs"

    def func(self):
        EvMenu(
            self.caller,
            "menus.constructs",
            startnode="start")
