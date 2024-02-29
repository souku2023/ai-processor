import sys
import os
sys.path.append(os.getcwd())
from core.app_logger import AppLogger
from core.utils.unzip import unzip
import exiftool
from core.geo_coordinate import GeoCoordinate

class PreStitchProcessing:
    """
    """

    @staticmethod
    def __unzip_files(path):
        """
        """
        unzip(path_to_zip_file=path, output_dir=os.path.join())


    @staticmethod
    def __find_geo_location_image(image_path:str)->GeoCoordinate|None:
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
                return GeoCoordinate(latitude=float(metadata[0]["Composite:GPSLatitude"]),
                                     longitude=float(metadata[0]["Composite:GPSLongitude"]))
        except Exception as e:
            AppLogger.warn(
                (f"{__class__.__qualname__}, Unable to extract data for,"
                 f"{os.path.join(image_path)}: {e.__class__.__qualname__}:"
                 f": {e}"))
            return None
        

    @staticmethod
    def __find_geo_locations_of_images(image_paths:list[str]):
        """
        """

    
    @staticmethod
    def __get_ms_images(path:str)-> list[str]:
        """
        Walks through the specified path and returns the list of all MS images 
        that have all bands.
        """
        image_files = []
        for dir, subdirs, files in os.walk(path):
            if len(files)>0:
                if len(list(filter(lambda x: 'tif' in x or 'jpg' in x, files)))>0:
                    for file in files:
                        if '_1.tif' in file:
                            a = file
                            b = file.replace('_1.tif', '_2.tif')
                            c = file.replace('_1.tif', '_3.tif')
                            d = file.replace('_1.tif', '_4.tif')
                            e = file.replace('_1.tif', '_5.tif')
                            if ((a in files) and
                                (b in files) and
                                (c in files) and
                                (d in files) and
                                (e in files)):
                                # 
                                im_path = os.path.join(dir, file)
                                image_files.append(im_path)
        return image_files


if __name__ == "__main__":
    path = r"D:\data\11-Feb-2024_120meter_12ac_MS\Zoho WorkDrive (4)"
    # path = os.getcwd()
    
