import time
import inspect


def log(*objects, sep=' ', end='\n'):
    """Function used to log activities to console. 
    
    Basically print() on steroids."""

    callerframerecord = inspect.stack()[1]
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)

    filename = info.filename.split('/')[len(info.filename.split('/')) - 1]
    func = info.function
    lineno = info.lineno

    msg = time.strftime("%H:%M:%S") + "\t"
    msg += filename + ": " + func + ": " + str(lineno) + ":\t"

    for obj in objects:
        msg += str(obj) + sep

    msg = msg.rstrip(sep)

    print(msg, end=end)
