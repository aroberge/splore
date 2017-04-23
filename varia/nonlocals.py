import sys


def nonlocals():
    '''This function returns a dict containing non-local objects i.e.
       those located between the calling frame and the global (module)
       frame.  Some of these objects may not have been declared as
       nonlocal.
    '''
    nonlocs = {}
    frame = sys._getframe().f_back  # calling frame
    if(frame.f_locals == frame.f_globals):
        return nonlocs
    frame = frame.f_back
    while True:
        if(frame.f_locals == frame.f_globals):
            return nonlocs
        nonlocs.update(frame.f_locals)
        frame = frame.f_back
