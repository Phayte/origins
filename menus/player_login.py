from django.conf import settings


def _invalid_selection(caller, error_msg=None):
    if error_msg:
        caller.msg("|r{0}|n".format(error_msg))


def _invalid_format(msg):
    return "|r{0}|n".format(msg)


def _get_num_characters(caller):
    return len(caller.db._playable_characters)


def _get_max_characters(caller):
    if caller.is_superuser:
        return "Unlimited"
    else:
        return settings.MAX_NR_CHARACTERS if settings.MULTISESSION_MODE > 1 \
            else 1


def _get_login_option(caller):
    desc = "Login into the universe (Current: {0})"

    if caller.db._last_puppet:
        desc = desc.format(caller.db._last_puppet.key)
        goto = "login"
        error_msg = None
    else:
        desc = _invalid_format(desc.format("Unavailable"))
        goto = "start"
        error_msg = "\nNo character currently selected. Please select " \
                    "another option.\n\n"

    return ({
                "desc": desc,
                "goto": goto,
                "exec": lambda caller: _invalid_selection(caller, error_msg)
            },)


def _get_select_character_option(caller):
    num_characters = _get_num_characters(caller)
    max_characters = _get_max_characters(caller)
    desc = "Select active character ({0}/{1})".format(num_characters,
                                                      max_characters)

    error_msg = None
    if num_characters:
        goto = "select_character"
    else:
        desc = _invalid_format(desc)
        error_msg = "You must create a character before you select one. " \
                    "Please select another option."
        goto = "start"

    return ({
                "desc": desc,
                "goto": goto,
                "exec": lambda caller: _invalid_selection(caller, error_msg)
            },)


def _get_create_character_option(caller):
    num_characters = _get_num_characters(caller)
    max_characters = _get_max_characters(caller)
    desc = "Create new character ({0}/{1})".format(num_characters,
                                                   max_characters)

    error_msg = None
    if caller.is_superuser or num_characters < max_characters:
        goto = "new_character"
    else:
        desc = _invalid_format(desc)
        goto = "start"
        error_msg = "\nYou cannot create anymore characters. Please " \
                    "select another option.\n\n"

    return ({
                "desc": desc,
                "goto": goto,
                "exec": lambda caller: _invalid_selection(caller, error_msg)
            },)


def _get_view_sessions_option(caller):
    num_sessions = len(caller.sessions.all())
    desc = "View active connections ({0} Session{1})".format(
        num_sessions, "s" if num_sessions > 1 else "")
    goto = "view_sessions"

    return ({
                "desc": desc,
                "goto": goto,
                "exec": lambda caller: _invalid_selection(caller, None)
            },)


def start(caller):
    text = "Account: |g{0}|n".format(caller.key)
    options = ()

    options += _get_login_option(caller)
    options += _get_select_character_option(caller)
    options += _get_create_character_option(caller)
    options += _get_view_sessions_option(caller)
    return text, options
    # options += _get_create_option(caller)

    # desc = "Login into the universe (Current: {0})"
    # error_msg = None
    # if caller.db._last_puppet:
    #     desc = desc.format(caller.db._last_puppet.key)
    #     goto = "login"
    # else:
    #     desc = desc.format("Unavailable")
    #     goto = "start"
    # options += ({
    #                 "desc": desc,
    #                 "goto": goto,
    #                 "exec": lambda caller: _invalid_selection(caller,
    #                                                           error_msg)
    #             },)
    #
    # desc = "Test"
    # options += ({
    #                 "desc": desc,
    #                 "goto": goto,
    #                 "exec": lambda caller: _invalid_selection(caller,
    #                                                           error_msg)
    #             },)

    # num_characters = len(caller.db._playable_characters)
    # if caller.is_superuser:
    #     max_characters = "Unlimited"
    # elif settings.MULTISESSION_MODE > 1:
    #     max_characters = settings.MAX_NR_CHARACTERS
    # else:
    #     max_characters = 1
    #
    # desc2 = "Create new character ({0}/{1})".format(num_characters,
    #                                                 max_characters)
    #


    #
    # elif
    # max_chars = settings.MAX_NR_CHARACTERS if \
    #     settings.MULTISESSION_MODE > 1 else 1
    # desc2 = "Create new character ({0}/{1})"
    # if caller.is_superuser:
    #     desc2 = desc2.format(len(characters), "Unlimited")
    #     goto2 = ""
    # else:
    #     desc2 = desc2.format(len(characters),
    #                          settings.MAX_NR_CHARACTERS if
    #                          settings.MULTISESSION_MODE > 1 else 1)
    #     goto2 = ""



    # options += ({
    #     "desc": "Log"
    # })
    # options = (
    #     {
    #         "key": "1",
    #         "desc": "Login into the world. (Current: )",
    #         "goto": "quit"
    #     },
    #     {
    #         "key": "2",
    #         "desc": "Enter World",
    #         "goto": "quit"
    #     },
    #     {
    #         "key": "3",
    #         "desc": "Delete character",
    #         "goto": "quit"
    #     },
    #     {
    #         "key": "4",
    #         "desc": "View logged in sessions",
    #         "goto": "quit"
    #     },
    #     {
    #         "key": "5",
    #         "desc": "Quit",
    #         "goto": "quit"
    #     }
    # )


def create_new_character(caller):
    text = "Please enter a new character name:"
    options = ()
    return text, options


def delete_character(caller):
    text = "Select a character to delete:"
    options = ()
    return text, options


def select_character(caller):
    text = "Select a character:"
    options = ()
    return text, options


def view_sessions(caller):
    text = "Select a session to disconnect:"
    options = ()

    options += (
        {
            "desc": "Main Menu",
            "goto": "start"
        }
    )
    pass


def quit(caller):
    text = "Come back soon, |g{0}|n.".format(caller.key)
    options = ()
    return text, options
