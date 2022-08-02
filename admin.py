import os
import logging
import pickle
import math
from error_definitions import LogfileNotMade

def get_settings():
    '''
    Get User settings stored locally in appdata
    Can be expanded for networked program in future
    '''
    try:
        if os.path.exists("appdata/settings") == False:
            raise LogfileNotMade
    except LogfileNotMade:
        logging.warning("Settings file does not exist. Creating default settings.")
        # Default user settings
        default_settings = {
            "Loglevel": 'WARNING',
            "Startup": {
                "X": math.nan,
                "Y": math.nan
            }
        }
        with open("appdata/settings", "wb") as f:
            pickle.dump(default_settings, f, protocol=pickle.HIGHEST_PROTOCOL)
    finally:
        with open("appdata/settings", "rb") as f:
            settings = pickle.load(f)
        logging.debug("get_settings returned settings")
        return settings
