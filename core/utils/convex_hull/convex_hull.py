from .ms_convex_hull import extract_ms_boundary_coordinates
from .rgb_convex_hull import extract_rgb_boundary_coordinates

from shapely.geometry import Polygon

import typing
if typing.TYPE_CHECKING:
    from core.app_logger import AppLogger
    from core.orthophoto import Orthophoto
    from core.geo_coordinate import GeoCoordinate

if __name__ == "__main__":
    import os, sys
    sys.path.append(os.getcwd())

from core.app_logger import AppLogger

class ConvexHull:
    """
    """

    def __init__(self, image: 'Orthophoto') -> None:
        """
        """
        self.image = image
        self.coordinates = self.__calculate_convex_hull()
        self.polygon = Polygon((coord.LON, coord.LAT) for coord in self.coordinates)
        # print(self.coordinates)
        

    def __calculate_convex_hull(self)->'list[GeoCoordinate]':
        """
        """

        if self.image.type == self.image.Type.RGB:
            AppLogger.info(f"ConvexHull:{self.image.name}, RGB image")
            return extract_rgb_boundary_coordinates(self.image)
        elif self.image.type == self.image.Type.MS:
            AppLogger.info(f"ConvexHull:{self.image.name}, MS image")
            return extract_ms_boundary_coordinates(self.image)