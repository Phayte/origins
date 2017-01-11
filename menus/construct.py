def start(caller):
    option1 = True
    option2 = False
    text = "Welcome to Origins Foundation Dock. How can I help you today?"
    options = (
        {
            "desc": "I would like to purchase a new ship.",
            "goto": "start",
            "exec": new_ship
        },
        {
            "desc": "I would like to modify my ship.",
            "goto": "start",
        },
        {
            "desc": "I would like to repair my ship.",
            "goto": "start",
        },
        {
            "desc": "Exit",
            "goto": "exit"
        }

    )
    return text, options


def exit(caller):
    text = "Goodbye for now!"
    return text, None


def new_ship(caller):
    caller.msg("Making ship!")
