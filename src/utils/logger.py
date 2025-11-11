# Disable the Streamlit's overrides
import logging
import streamlit.logger

def setup_logger():
    streamlit.logger.get_logger = logging.getLogger
    streamlit.logger.setup_formatter = None
    streamlit.logger.update_formatter = lambda *a, **k: None
    streamlit.logger.set_log_level = lambda *a, **k: None

    # Reset already created loggers (disabling settings done in streamlit.logger.get_logger)
    for name in streamlit.logger._loggers.keys():
        if name == "root":  # Streamlit aliases "root" -> "streamlit" (See streamlit.logger.get_logger)
            name = "streamlit"
        logger = logging.getLogger(name)
        logger.propagate = True
        logger.handlers.clear()
        logger.setLevel(logging.NOTSET)

    streamlit.logger._loggers = {}

    # Setup the logger in the way I usually do with my crap apps
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(asctime)s %(name)s:%(message)s",
        force=True,
    ) 

    streamlit_handler = logging.getLogger("streamlit")
    streamlit_handler.setLevel(logging.ERROR)