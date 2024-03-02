from shapely import Point, Polygon
from core.geo_coordinate import GeoCoordinate
from core.app_logger import AppLogger
from core.exiftool import Exiftool
import os
import shutil

class RawMSImage:
    """
    """

    def __init__(self, r:str, g:str, b:str, n:str, re:str, geo_coords:GeoCoordinate=None) -> None:
        """
        """

        self.red_path = r
        self.blue_path = b
        self.green_path = g
        self.nir_path = n
        self.red_edge_path = re
        self.path = r
        
        if geo_coords is None:
            self.geo_location = self.__find_geo_location_image(self.red_path)
        else:
            self.geo_location = geo_coords
        
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
    
    def copy(self, dst:str):
        """
        """
        shutil.copy(self.red_path, os.path.join(dst, os.path.basename(self.red_path)))
        shutil.copy(self.blue_path, os.path.join(dst, os.path.basename(self.blue_path)))
        shutil.copy(self.green_path, os.path.join(dst, os.path.basename(self.green_path)))
        shutil.copy(self.nir_path, os.path.join(dst, os.path.basename(self.nir_path)))
        shutil.copy(self.red_edge_path, os.path.join(dst, os.path.basename(self.red_edge_path)))

        

# if __name__ == "__main__":
#     import os
#     p = r""
#     for files in os.listdir(p):
        