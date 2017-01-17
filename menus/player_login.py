from django.conf import settings

from evennia.objects.models import ObjectDB
from evennia.utils import create

from utils.format import format_invalid, format_valid
from utils.menu import nodetext_only_formatter, reset_node_formatter, \
    get_user_input, get_user_yesno, wrap_exec

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


def _get_option_create_new_character(is_valid):
    return _get_option(
        "Create new character",
        "option_create_new_character" if is_valid else "option_start",
        None if is_valid else "You cannot create anymore characters."
    )


def _get_option_delete_characters(is_valid):
    return _get_option(
        "Delete character",
        "option_delete_character" if is_valid else "option_start",
        None if is_valid else "You have no characters to delete."
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
    # TODO: Loop scoping causing issues
    for character in session.player.db._playable_characters:
        options += ({
                        "desc": character.key,
                        "goto": "option_start",
                        "exec": wrap_exec(session, 
                                          _set_selected_puppet, 
                                          puppet=character)
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
    options += _get_option_create_new_character(num_chars < max_chars)
    options += _get_option_delete_characters(num_chars)
    options += _get_option_view_sessions()
    options += _get_option_quit()
    return text, options


def option_login(session):
    try:
        puppet = _get_selected_puppet(session)
        session.player.puppet_object(session, puppet)
        session.player.db._last_puppet = puppet
    except RuntimeError as ex:
        session.msg("You cannot login as {0}: {1}".format(puppet.key, ex))

    return "", None


def option_select_character(session):
    text = "Choose your character:"
    options = _get_option_select_active_character(session)
    return text, options


# noinspection PyUnusedLocal
def option_create_new_character(session):
    reset_node_formatter(session, nodetext_only_formatter)

    text = "Enter a character name (blank to abort):"
    options = get_user_input(
        "option_start",
        "option_confirm_character",
        default_exec=exec_validate_character_name)

    return text, options


def exec_validate_character_name(session, raw_string):
    # TODO Fix the capitalization of multi part name.
    character_name = raw_string.capitalize()
    existing_character = ObjectDB.objects.get_objs_with_key_and_typeclass(
        character_name, settings.BASE_CHARACTER_TYPECLASS)

    if existing_character:
        session.msg(format_invalid(
            "\n{0} is already taken. Try again.\n\n".format(character_name)))
        return "option_create_new_character"

    session.msg(format_valid(character_name))
    _set_new_character_name(session, character_name)


# noinspection PyUnusedLocal
def option_confirm_character(session):
    text = "Are you sure you want to create {0} (|gY|n/|rN|n)?"
    options = get_user_yesno("option_generate_character", "option_start")
    return text, options


def option_generate_character(session):
    session.ndb._menutree.new_character = _create_new_character(session)

    text = "{0} has been created. Would you like to select this character " \
           "(|gY|n/|rN|n)?".format(session.ndb._menutree.new_character.key)
    options = get_user_yesno("option_start", "option_start",
                             yes_exec=exec_select_new_character)
    return text, options


def exec_select_new_character(session):
    _set_selected_puppet(session, session.ndb._menutree.new_character)


# endregion


# region Helpers

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


def _get_selected_puppet(session):
    if not hasattr(session.ndb._menutree, "selected_puppet"):
        _set_selected_puppet(session, session.player.db._last_puppet)
    return session.ndb._menutree.selected_puppet


def _set_selected_puppet(session, puppet):
    session.ndb._menutree.selected_puppet = puppet


def _get_new_character_name(session):
    return session.ndb._menutree.new_character_name


def _set_new_character_name(session, character_name):
    session.ndb._menutree.new_character_name = character_name


def _create_new_character(session):
    key = _get_new_character_name(session)
    start_location = ObjectDB.objects.get_id(settings.START_LOCATION)
    default_home = ObjectDB.objects.get_id(settings.DEFAULT_HOME)
    permissions = settings.PERMISSION_PLAYER_DEFAULT
    typeclass = settings.BASE_CHARACTER_TYPECLASS
    player = session.player

    new_character = create.create_object(typeclass, key=key,
                                         location=start_location,
                                         home=default_home,
                                         permissions=permissions)

    new_character.locks.add(
        "puppet:id({0}) or pid({1}) or perm(Immortals) or pperm("
        "Immortals)".format(new_character.id, player.id))
    player.db._playable_characters.append(new_character)

    session.msg("{0} has been created.".format(format_valid(key)))

    return new_character

# endregion
