import os
import sys
sys.path.append(os.getcwd())
from core.geo_coordinate import GeoCoordinate
from core.app_logger import AppLogger
import exiftool

class Exiftool:
    """
    """

    @staticmethod
    def find_geo_location_image(image_path:str, print_data:bool=False)->GeoCoordinate|None:
        """
        Gets the latitude and longitude of the image
        """
        # AppLogger.info(f"PreStitchProcessing, {os.path.basename(image_path)}")
        # Exiftool Path
        exiftool_path = os.path.join(os.getcwd(), 'resources', 'exiftool', 'exiftool.exe')
        try:
            # Using exiftool with the executable.
            with exiftool.ExifTool(exiftool_path, win_shell=True) as et:
                metadata = et.execute_json(image_path)
                if print_data:
                    print(metadata)
                return GeoCoordinate(latitude=float(metadata[0]["Composite:GPSLatitude"]),
                                     longitude=float(metadata[0]["Composite:GPSLongitude"]))
        except Exception as e:
            AppLogger.warn(
                (f"{__class__.__qualname__}, Unable to extract data for,"
                 f"{os.path.join(image_path)}: {e.__class__.__qualname__}:"
                 f": {e}"))
            return None
        
if __name__ == '__main__':
    Exiftool.find_geo_location_image()