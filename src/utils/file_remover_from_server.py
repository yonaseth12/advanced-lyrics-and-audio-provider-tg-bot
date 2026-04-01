import os
import logging

logger = logging.getLogger(__name__)


def remove_file_from_server(file_path, basename):
    if os.path.exists(file_path):
        os.remove(file_path)
        logger.info("Removed %s from storage", basename)
    else:
        logger.warning("File %s not found in storage (already removed?)", basename)