from django.conf import settings

from evennia.objects.models import ObjectDB
from evennia.utils import create

from utils.format import format_invalid, format_valid
from utils.menu import nodetext_only_formatter, reset_node_formatter, \
    get_user_input, get_user_yesno, wrap_exec
from utils.session import get_session_address

MENU_TEXT_NEWCHAR_NAME = "Enter a character name (blank to abort):"
MENU_TEXT_INITIAL_PASSWORD = "Enter a password (blank to abort):"


def option_start(session):
    reset_node_formatter(session)

    num_chars = _get_num_characters(session)
    max_chars = _get_max_characters(session)
    is_available_slots = session.player.is_superuser or num_chars < max_chars

    selected_character = _get_selected_character(session)
    if selected_character:
        selected_character_name = format_valid(selected_character.key)
    else:
        selected_character_name = format_invalid("Unavailable")

    num_sessions = len(session.player.sessions.all())

    text = _generate_title(session,
                           selected_character_name,
                           num_chars,
                           max_chars,
                           is_available_slots,
                           num_sessions)

    options = _get_option_login(selected_character)
    options += _get_option_select_character(num_chars)
    options += _get_option_create_new_character(num_chars < max_chars)
    options += _get_option_delete_characters(num_chars)
    options += _get_option_view_sessions()
    options += _get_option_quit()
    return text, options


# region Option Login Chain

def option_login(session):
    try:
        character = _get_selected_character(session)
        session.player.puppet_object(session, character)
        session.player.db._last_puppet = character
    except RuntimeError as ex:
        if character:
            session.msg(
                "You cannot login as {0}: {1}".format(character.key, ex))
        else:
            session.msg("You cannot login: {0}", ex)

    return "", None


# endregion

# region Option Select Character

def option_select_character(session):
    text = "Select a character:"
    options = _get_option_select_character_list(session)
    return text, options


# endregion

# region Option Create New Character

# noinspection PyUnusedLocal
def option_create_new_character(session):
    reset_node_formatter(session, nodetext_only_formatter)

    text = "Enter a character name (blank to abort):"
    options = get_user_input(
        "option_start",
        "option_confirm_new_character",
        default_exec=exec_validate_character_name)

    return text, options


def exec_validate_character_name(session, raw_string):
    # TODO Fix the capitalization of multi part name.
    character_name = raw_string
    existing_character = ObjectDB.objects.get_objs_with_key_and_typeclass(
        character_name, settings.BASE_CHARACTER_TYPECLASS)

    if existing_character:
        session.msg(format_invalid(
            "\n{0} is already taken. Try again.\n\n".format(character_name)))
        return "option_create_new_character"

    session.msg(format_valid(character_name))
    _set_new_character_name(session, character_name)


# noinspection PyUnusedLocal
def option_confirm_new_character(session):
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
    _set_selected_character(session, session.ndb._menutree.new_character)


# endregion

# region Option Delete Character

def option_delete_character(session):
    text = "Choose character to delete:"
    options = _get_option_delete_character_list(session)
    return text, options


def option_confirm_delete_character(session):
    reset_node_formatter(session, nodetext_only_formatter)

    text = "Are you sure you want to |r*** PERMANENTLY DELETE {0} ***|n?  " \
           "(|gY|n/|rN|n)?".format(_get_delete_character(session).key.upper())
    options = get_user_yesno("option_start",
                             "option_start",
                             yes_exec=exec_confirm_delete_character(session),
                             no_exec=exec_abort_delete_character(session))
    return text, options


def exec_confirm_delete_character(session):
    delete_character = _get_delete_character(session)
    name = delete_character.key

    player = session.player
    player.db._playable_characters = \
        [character for character in player.db._playable_characters
         if character != delete_character]

    if delete_character == player.db._last_puppet:
        player.db._last_puppet = None

    if delete_character == _get_selected_character(session):
        _set_selected_character(session, None)

    delete_character.delete()
    session.msg(_display_invalid_msg("{0} has been deleted.".format(name)))


def exec_abort_delete_character(session):
    session.msg("Aborting delete. Phew.")


# endregion

# region View Sessions

def option_view_sessions(session):
    text = "Select a session to disconnect:"
    options = _get_option_session_list(session)
    return text, options


# endregion

# region Option Quit

def option_quit(session):
    reset_node_formatter(session, nodetext_only_formatter)
    session.sessionhandler.disconnect(
        session, "Thanks for playing! Come back soon! |rDisconnecting.|n")
    return "", None


# endregion

# region Menu Options

def _get_option(desc, goto, error_msg=None):
    return ({
                "desc": format_invalid(desc) if error_msg else desc,
                "goto": goto,
                "exec": lambda caller: _display_invalid_msg(caller, error_msg)
            },)


def _get_option_login(is_valid):
    return _get_option(
        "Login Into Universe",
        "option_login" if is_valid else "option_start",
        None if is_valid else "Please select a valid character."
    )


def _get_option_select_character(is_valid):
    return _get_option(
        "Select Active Character",
        "option_select_character" if is_valid else "option_start",
        None if is_valid else "Please create a character first."
    )


def _get_option_create_new_character(is_valid):
    return _get_option(
        "Create New Character",
        "option_create_new_character" if is_valid else "option_start",
        None if is_valid else "You cannot create anymore characters. Please " \
                              "contact the admin to increase your allowance."
    )


def _get_option_delete_characters(is_valid):
    return _get_option(
        "Delete Character",
        "option_delete_character" if is_valid else "option_start",
        None if is_valid else "You have no characters to delete."
    )


def _get_option_view_sessions():
    return _get_option(
        "View Active Sessions",
        "option_view_sessions",
    )


def _get_option_quit():
    return _get_option(
        "Quit",
        "option_quit",
    )


def _get_option_select_character_list(session):
    options = ()
    for character in session.player.db._playable_characters:
        options += ({
                        "desc": character.key,
                        "goto": "option_start",
                        "exec": wrap_exec(session,
                                          _set_selected_character,
                                          character=character)
                    },)

    options += ({
                    "desc": "Back",
                    "goto": "option_start"
                },)

    return options


def _get_option_delete_character_list(session):
    options = ()
    for character in session.player.db._playable_characters:
        options += ({
                        "desc": character.key,
                        "goto": "option_confirm_delete_character",
                        "exec": wrap_exec(session,
                                          _set_delete_character,
                                          character=character)
                    },)

    options += ({
                    "desc": "Back",
                    "goto": "option_start"
                },)

    return options


def _get_option_session_list(session):
    options = ()
    for i_sess, sess in enumerate(session.player.sessions.all()):
        desc = "{0} ({1})".format(sess.protocol_key,
                                  get_session_address(sess))
        if session.sessid == sess.sessid:
            desc = format_invalid("{0} *".format(desc))

        options += ({
                        "desc": desc,
                        "goto": "option_view_sessions",
                        "exec": wrap_exec(session,
                                          _disconnect_session,
                                          disco_session=sess)
                    },)

    options += ({
                    "desc": "Back",
                    "goto": "option_start"
                },)

    return options


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
        session.msg("\n*** {0} *** \n\n".format(format_invalid(error_msg)))


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


def _get_selected_character(session):
    if not hasattr(session.ndb._menutree, "selected_character"):
        _set_selected_character(session, session.player.db._last_puppet)
    return session.ndb._menutree.selected_character


def _set_selected_character(session, character):
    session.ndb._menutree.selected_character = character


def _get_new_character_name(session):
    return session.ndb._menutree.new_character_name


def _set_new_character_name(session, character_name):
    session.ndb._menutree.new_character_name = character_name


def _get_delete_character(session):
    return session.ndb._menutree.delete_character


def _set_delete_character(session, character):
    session.ndb._menutree.delete_character = character


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


def _disconnect_session(session, disco_session):
    disco_session.sessionhandler.disconnect(disco_session,
                                            "|rDisconnecting.|n")

# endregion
