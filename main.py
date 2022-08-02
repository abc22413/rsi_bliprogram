#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from datetime import datetime
import logging
from error_definitions import LogfileNotMade
from admin import get_settings
from gui_program import *

if __name__ == "__main__":
    try:
        # If appdata folder does not exist
        if os.path.exists("appdata") == False:
            raise LogfileNotMade

    except LogfileNotMade:
        os.mkdir("appdata")

    finally:
        # Initialise logging file handler
        logging.basicConfig(filename="appdata/Log.log",
                            filemode="a", format="%(asctime)s - %(levelname)s - %(message)s",
                            level=logging.WARNING)

        #Set user's preferred logging level
        level = logging.getLevelName(get_settings()["Loglevel"])
        logging.getLogger().setLevel(level)

        logging.debug("Application started.")

        run_app("COM9")
        
        logging.debug("Application shut down.")
        logging.shutdown()