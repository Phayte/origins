

def format_invalid(msg):
    return format_color(msg, "r")


def format_valid(msg):
    return format_color(msg, "g")


def format_color(msg, color_code):
    return "|{color_code}{msg}|n".format(
        color_code=color_code,
        msg=msg
    )


def menu_set_node_formatter(caller, formatter):
    caller.ndb._menutree._node_formatter = formatter


def menu_get_node_formatter(caller):
    return caller.ndb._menutree._node_formatter


def menu_nodetext_only_formatter(nodetext, optionstext, caller=None):
    return nodetext