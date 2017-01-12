from django.conf import settings
from evennia.objects.models import ObjectDB

from utils.format import format_invalid, format_valid


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


def _get_option_select_active_character(caller):
    options = ()
    # noinspection PyProtectedMember
    for character in caller.db._playable_characters:
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


def _get_option_get_character_name():
    options = ({
                   "key": "_default",
                   "goto": "option_validate_character_name"
               },)
    return options


def _get_option_get_character_password():
    options = ({
                   "key": "_default",
                   "goto": "option_validate_character_password"
               },)
    return options


# endregion


# region Menu Selections


def option_start(caller):
    num_chars = _get_num_characters(caller)
    max_chars = _get_max_characters(caller)
    is_available_slots = caller.is_superuser or num_chars < max_chars

    # noinspection PyProtectedMember
    last_puppet = caller.db._last_puppet
    if last_puppet:
        selected_character_name = format_valid(last_puppet.key)
    else:
        selected_character_name = format_invalid("Unavailable")

    num_sessions = len(caller.sessions.all())

    text = _generate_title(caller,
                           selected_character_name,
                           num_chars,
                           max_chars,
                           is_available_slots,
                           num_sessions)

    options = _get_option_login(last_puppet)
    options += _get_option_select_character(num_chars)
    options += _get_option_create_character(num_chars < max_chars)
    options += _get_option_view_sessions()
    options += _get_option_quit()
    return text, options


# def option_login(caller):
#     pass


def option_select_character(caller):
    text = "Choose your character:"
    options = _get_option_select_active_character(caller)
    return text, options


# noinspection PyUnusedLocal
def option_create_character(caller):
    text = "Enter a character name: (enter blank to abort)"
    options = _get_option_get_character_name()
    return text, options


def option_validate_character_name(caller, raw_string):
    existing_character = ObjectDB.objects.get_objs_with_key_and_typeclass(
        raw_string, settings.BASE_CHARACTER_TYPECLASS)
    if existing_character:
        text = "Character name already used. Please try again: (enter " \
               "blank to cancel)"
        options = _get_option_get_character_name()
        # noinspection PyProtectedMember
        caller.ndb._menutree.new_character_name = raw_string
    else:
        text = "Enter a password: (enter blank to abort)"
        options = _get_option_get_character_password()
    return text, options


def option_validate_character_password(caller, raw_string):
    text = "Done",
    options = ()

    return text, options


# endregion


# region Helpers


def _generate_title(caller, selected_character_name, num_chars, max_chars,
                    is_available_slots, num_sessions):
    text = "Account: {0}  |  Character: {1}  |  Slots: {2}  | Sessions: {3}"
    text = text.format(
        format_valid(caller.key),
        selected_character_name,
        _get_slots(num_chars, max_chars, is_available_slots),
        format_valid(num_sessions)
    )
    return text


def _display_invalid_msg(caller, error_msg=None):
    if error_msg:
        caller.msg("\n{0}\n\n".format(format_invalid(error_msg)))


def _get_num_characters(caller):
    # noinspection PyProtectedMember
    return len(caller.db._playable_characters)


def _get_max_characters(caller):
    if caller.is_superuser:
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


def _select_character(caller, puppet):
    caller.db._last_puppet = puppet


def _create_new_character(caller, raw_string):
    caller.msg(raw_string)

    # endregion
