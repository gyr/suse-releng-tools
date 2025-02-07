import logging


def logger_setup(name: str,
                 verbose: bool = False,
                 log_file: bool = False):
    logger = logging.getLogger(name)

    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)

    # create console handler with a higher log level
    stream_handler = logging.StreamHandler()
    # stream_handler.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    # formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    stream_handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(stream_handler)

    if log_file:
        # create file handler which logs even debug messages
        file_handler = logging.FileHandler("/tmp/sle_tools.log")
        # file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
