from django.conf import settings

from evennia.objects.models import ObjectDB

from utils.format import format_invalid, format_valid
from utils.menu import nodetext_only_formatter, reset_node_formatter, \
    get_user_input_option

MENU_TEXT_NEWCHAR_NAME = "Enter a character name (blank to abort):"
MENU_TEXT_INITIAL_PASSWORD = "Enter a password (blank to abort):"

# region Menu Options

def _get_option(desc, goto, error_msg=None):
    return ({
                "desc": format_invalid(desc) if error_msg else desc,
                "goto": goto,
                "exec": lambda caller: _display_invalid_msg(caller, error_msg)
            },)


def _get_option_login(is_valid):
    return _get_option(
        "Login into the universe",
        "option_login" if is_valid else "option_start",
        None if is_valid else "Please select a valid character."
    )


def _get_option_select_character(is_valid):
    return _get_option(
        "Select active character",
        "option_select_character" if is_valid else "option_start",
        None if is_valid else "Please create a character first."
    )


def _get_option_create_character(is_valid):
    return _get_option(
        "Create new character",
        "option_create_character" if is_valid else "option_start",
        None if is_valid else "You cannot create anymore characters."
    )


def _get_option_view_sessions():
    return _get_option(
        "View active sessions",
        "option_view_sessions",
    )


def _get_option_quit():
    return _get_option(
        "Quit",
        "option_quit",
    )


def _get_option_select_active_character(session):
    options = ()
    # noinspection PyProtectedMember
    for character in session.player.db._playable_characters:
        options += ({
                        "desc": character.key,
                        "goto": "option_start",
                        "exec": lambda caller: _select_character(caller,
                                                                 character)
                    },)

    options += ({
                    "desc": "Back",
                    "goto": "option_start"
                },)

    return options

# endregion


# region Menu Selections


def option_start(session):
    reset_node_formatter(session)

    num_chars = _get_num_characters(session)
    max_chars = _get_max_characters(session)
    is_available_slots = session.player.is_superuser or num_chars < max_chars

    selected_puppet = _get_selected_puppet(session)
    if selected_puppet:
        selected_character_name = format_valid(selected_puppet.key)
    else:
        selected_character_name = format_invalid("Unavailable")

    num_sessions = len(session.player.sessions.all())

    text = _generate_title(session,
                           selected_character_name,
                           num_chars,
                           max_chars,
                           is_available_slots,
                           num_sessions)

    options = _get_option_login(selected_puppet)
    options += _get_option_select_character(num_chars)
    options += _get_option_create_character(num_chars < max_chars)
    options += _get_option_view_sessions()
    options += _get_option_quit()
    return text, options


# def option_login(caller):
#     pass


def option_select_character(session):
    text = "Choose your character:"
    options = _get_option_select_active_character(session)
    return text, options


# noinspection PyUnusedLocal
def option_create_character(session):
    reset_node_formatter(session, nodetext_only_formatter)

    text = MENU_TEXT_NEWCHAR_NAME
    options = get_user_input_option("option_start",
                                    "option_validate_character_name")
    return text, options


def option_validate_character_name(session, raw_string):
    character_name = raw_string.capitalize()
    existing_character = ObjectDB.objects.get_objs_with_key_and_typeclass(
        character_name, settings.BASE_CHARACTER_TYPECLASS)

    if existing_character:
        session.msg(format_invalid("\n{0} name already taken.\n\n".format(
            character_name
        )))
        text = MENU_TEXT_NEWCHAR_NAME
        options = get_user_input_option("option_start",
                                        "option_validate_character_name")
    else:
        session.msg(format_valid(character_name))
        session.ndb._menutree.new_character_name = character_name
        text = "Enter a password (enter blank to abort):"
        options = get_user_input_option("option_start",
                                        "option_validate_password")

    return text, options


def option_validate_password(session, raw_string):
    session.ndb._menutree.new_password = raw_string
    text = "Enter password again (enter blank to abort):"
    options = get_user_input_option("option_start",
                                    "option_validate_password2")
    return text, options


def option_validate_password2(session, raw_string):
    if session.ndb._menutree.new_password == raw_string:
        text = "Are you sure you want to create {0}? (|gY|n/|rN|n)".format(
            format_valid(session.ndb._menutree.new_character_name))
        options = (
            {
                "key": ("Yes", "Y"),
                "goto": "nowhere"
            },
            {
                "key": ("No", "N"),
                "goto": "nowhere"
            },
        )
    else:
        session.msg(format_invalid("Passwords do not match!\n"))
        text = MENU_TEXT_INITIAL_PASSWORD
        options = get_user_input_option("option_start",
                                        "option_validate_password")

    return text, options

# endregion


# region Helpers


def _get_selected_puppet(session):
    if not hasattr(session.ndb._menutree, "selected_puppet"):
        session.ndb._menutree.selected_puppet = session.player.db._last_puppet
    return session.ndb._menutree.selected_puppet


def _generate_title(caller, selected_character_name, num_chars, max_chars,
                    is_available_slots, num_sessions):
    text = "Account: {0}  |  Character: {1}  |  Slots: {2}  | Sessions: {3}"
    text = text.format(
        format_valid(caller.player.key),
        selected_character_name,
        _get_slots(num_chars, max_chars, is_available_slots),
        format_valid(num_sessions)
    )
    return text


def _display_invalid_msg(session, error_msg=None):
    if error_msg:
        session.msg("\n{0}\n\n".format(format_invalid(error_msg)))


def _get_num_characters(session):
    # noinspection PyProtectedMember
    return len(session.player.db._playable_characters)


def _get_max_characters(session):
    if session.player.is_superuser:
        return "Unlimited"
    else:
        return settings.MAX_NR_CHARACTERS if settings.MULTISESSION_MODE > 1 \
            else 1


def _get_slots(num_char, max_char, is_available_slots):
    text = "({num_char}/{max_char})".format(num_char=num_char,
                                            max_char=max_char)
    if is_available_slots:
        text = format_valid(text)
    else:
        text = format_invalid(text)
    return text


def _select_character(session, puppet):
    session.player.db._last_puppet = puppet


def _create_new_character(session, raw_string):
    session.msg(raw_string)


def _login(session):
    pass

# def underline_node_formatter(nodetext, optionstext, caller=None):
#     """
#     Draws a node with underlines '_____' around it.
#     """
#     nodetext_width_max = max(m_len(line) for line in nodetext.split("\n"))
#     options_width_max = max(m_len(line) for line in optionstext.split("\n"))
#     total_width = max(options_width_max, nodetext_width_max)
#     separator1 = "_" * total_width + "\n\n" if nodetext_width_max else ""
#     separator2 = "\n" + "_" * total_width + "\n\n" if total_width else ""
#     return separator1 + "|n" + nodetext + "|n" + separator2 + "|n" + optionstext

# endregion
