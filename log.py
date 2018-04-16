import logging, sys

# Create the Logger
L = logging.getLogger('pokernerd')
L.setLevel(logging.DEBUG)

# Create the Handler for logging to STDERR
logger_handler = logging.StreamHandler(sys.stderr)
logger_handler.setLevel(logging.DEBUG)

# Create a Formatter for formatting the log messages
logger_formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s')

# Add the Formatter to the Handler
logger_handler.setFormatter(logger_formatter)

# Add the Handler to the Logger
L.addHandler(logger_handler)

