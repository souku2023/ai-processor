from core.geo_coordinate import GeoCoordinate
from core.exiftool import Exiftool
from core.app_logger import AppLogger
from shapely import Point, Polygon
import os
import shutil
class RawRGBImage:
    """
    """

    def __init__(self, path:str, geo_coords:GeoCoordinate=None) -> None:
        """
        """

        self.path = path

        if geo_coords is None:
            self.geo_location = self.__find_geo_location_image(self.path)
        else:
            self.geo_location = geo_coords
        self.geo_loc_point = Point(self.geo_location.LAT, self.geo_location.LON)
       
        AppLogger.info(f"RawRGBImage, Found raw RGB image {self.path} @ {self.geo_location.LAT}, {self.geo_location.LON}")

    
    def __find_geo_location_image(self, image_path:str)->GeoCoordinate|None:
        """
        Gets the latitude and longitude of the image.
        """
        return Exiftool.find_geo_location_image(image_path=image_path)
    
    
    def is_in_polygon(self, polygon:Polygon)->bool:
        """
        """
        if self.geo_location is not None:
            return polygon.contains(Point(self.geo_location.LAT, self.geo_location.LON))
        
    def __repr__(self) -> str:
        return (f"RawRGBImage@[{self.geo_location}] "
                f"({os.path.basename(self.path)}, "
                )
    

    def copy(self, dst):
        """
        """

        shutil.copy(self.path, os.path.join(dst, os.path.basename(self.path)))


        
