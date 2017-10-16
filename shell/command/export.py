from .constants import *

def export(args):
    if len(args) > 0:
        env = args[0].split("=")
        os.environ[env[0]] = env[1]

    return RUN
