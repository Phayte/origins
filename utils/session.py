def get_session_address(session):
    return isinstance(session.address, tuple) \
           and str(session.address[0]) \
           or str(session.address)