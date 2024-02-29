from shapely import Point, Polygon
from core.geo_coordinate import GeoCoordinate
from core.app_logger import AppLogger
from core.exiftool import Exiftool
import os

class RawMSImage:
    """
    """

    def __init__(self, r:str, g:str, b:str, n:str, re:str) -> None:
        """
        """

        self.red_path = r
        self.blue_path = b
        self.green_path = g
        self.nir_path = n
        self.red_edge_path = re

        self.geo_location = self.__find_geo_location_image(self.red_path)
        self.geo_loc_point = Point(self.geo_location.LAT, self.geo_location.LON)
        AppLogger.info(f"RawMSImage, Found raw multispectral image {self.red_path[0:-6]} @ {self.geo_location.LAT}, {self.geo_location.LON}")

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
        return (f"RawMSImage@[{self.geo_location}] "
                f"({os.path.basename(self.red_path)}, "
                f"{os.path.basename(self.green_path)}, "
                f"{os.path.basename(self.blue_path)}, "
                f"{os.path.basename(self.nir_path)}, "
                f"{os.path.basename(self.red_edge_path)})\n"
                )
        

# if __name__ == "__main__":
#     import os
#     p = r""
#     for files in os.listdir(p):
        