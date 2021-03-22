import logging
import sys

# set the log level here
logging_level = logging.INFO

# change the logging format here
logging.basicConfig(format='%(levelname)s - %(filename)s - %(lineno)d - %(funcName)s - %(asctime)s - %(message)s',
                    level=logging_level,
                    stream=sys.stdout)

# disable matplotlib logs
logging.getLogger('matplotlib.font_manager').disabled = True

# create the logger for other classes to use
logger = logging.getLogger('simulator')
