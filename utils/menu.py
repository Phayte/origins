def get_user_input(blank_goto, default_goto, blank_exec=None,
                          default_exec=None):
    options = ({
                   "key": "",
                   "goto": blank_goto,
                   "exec": blank_exec,
               },
               {
                   "key": '_default',
                   "goto": default_goto,
                   "exec": default_exec,
               },)
    return options


def get_user_yesno(yes_goto, no_goto, yes_exec=None, no_exec=None):
    options = ({
                   "key": ('y', 'yes',),
                   "goto": yes_goto,
                   "exec": yes_exec,
               },
               {
                   "key": ('n', 'no',),
                   "goto": no_goto,
                   "exec": no_exec,
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
