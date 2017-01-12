def format_invalid(msg):
    return format_color(msg, "r")


def format_valid(msg):
    return format_color(msg, "g")


def format_color(msg, color_code):
    return "|{color_code}{msg}|n".format(
        color_code=color_code,
        msg=msg
    )
