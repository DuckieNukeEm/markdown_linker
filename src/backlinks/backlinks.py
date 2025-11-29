import backlinks.io as io
import backlinks.logging as logging
import backlinks.markdown as md
import backlinks.path as path

if __name__ == "__main__":
    logging.setup_logging()
    logger = logging.getLogger(__name__)  # Get logger for main module
