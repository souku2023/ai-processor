from core.geo_coordinate import GeoCoordinate
from core.exiftool import Exiftool
from shapely import Point, Polygon
import os
class RawRGBImage:
    """
    """

    def __init__(self, path:str) -> None:
        """
        """

        self.path = path

        self.geo_location = self.__find_geo_location_image(self.path)
        self.geo_loc_point = Point(self.geo_location.LAT, self.geo_location.LON)

    
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