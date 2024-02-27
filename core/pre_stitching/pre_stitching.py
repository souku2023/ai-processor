import sys
import os
sys.path.append(os.getcwd())
from core.app_logger import AppLogger
from core.utils.unzip import unzip


class PreStitchProcessing:
    """
    """

    @staticmethod
    def __unzip_files(path):
        unzip(path_to_zip_file=path, output_dir=os.path.join())
