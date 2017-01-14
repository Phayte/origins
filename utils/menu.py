def get_user_input_option(blank_goto, default_goto):
    options = ({
                   "key": "",
                   "goto": blank_goto,
               },
               {
                   "key": '_default',
                   "goto": default_goto,
               },)
    return options

def reset_node_formatter(caller, new_formatter=None):
    if not hasattr(caller.ndb._menutree, "_backup_node_formatter"):
        caller.ndb._menutree._backup_node_formatter = None

    restore_node_formatter(caller)
    backup_node_formatter(caller)
    if new_formatter:
        set_node_formatter(caller, new_formatter)


def backup_node_formatter(caller):
    caller.ndb._menutree._backup_node_formatter = get_node_formatter(
        caller)


def restore_node_formatter(caller):
    backup_node_formatter = caller.ndb._menutree._backup_node_formatter
    if backup_node_formatter:
        set_node_formatter(caller,
                           caller.ndb._menutree._backup_node_formatter)
        caller.ndb._menutree._backup_node_formatter = None


def set_node_formatter(caller, formatter):
    caller.ndb._menutree._node_formatter = formatter


def get_node_formatter(caller):
    return caller.ndb._menutree._node_formatter


def nodetext_only_formatter(nodetext, optionstext, caller=None):
    return nodetext
