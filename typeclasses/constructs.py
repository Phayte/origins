from typeclasses.objects import Object
from utils.is_etype import is_exit


class Construct(Object):
    def at_object_receive(self, moved_obj, source_location):
        """
        Args:
            moved_obj (evennia.objects.objects.DefaultObject):
            source_location (evennia.objects.objects.DefaultObject):
        """
        if is_exit(moved_obj):
            return
        elif source_location == self.location:
            pass  # TODO: Move to default exit
        else:
            moved_obj.move_to(self.location, quiet=True, move_hooks=False)

    def at_cmdset_get(self, **kwargs):
        pass  # self.contents

    def return_appearance(self, looker):
        ""
