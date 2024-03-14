from scipy.spatial import ConvexHull
import time
import numpy as np
from osgeo import gdal, osr, ogr
import sys, os
if __name__ == '__main__':
    sys.path.append(os.getcwd())

from core.app_logger import AppLogger
from core.geo_coordinate import GeoCoordinate

import typing
if typing.TYPE_CHECKING:
    from core.orthophoto import Orthophoto

class Stack:
    def __init__(self):
        self.stack = []
        self.top = -1

    def push(self, element):
        self.stack.append(element)
        self.top = self.top + 1

    def pop(self):
        if self.top == -1:
            AppLogger.info("MSConvesHull, \tStack Underflow")
        else:
            element = self.stack[self.top]
            self.stack.pop(self.top)
            self.top = self.top - 1
            return element

    def isEmpty(self):
        if self.top == -1:
            return True
        return False

    def find_top(self):
        AppLogger.info(f"{self.stack[self.top]}")

class ExtractBoundary:
    def __init__(self):
        self.s = Stack()
        self.visited = None
        self.boundary_list = []
        self.directions = [[-1, -1], [-1, 0], [-1, 1],
                           [0, 1], [1, 1], [1, 0], [1, -1], [0, -1]]
        self.straight_directions = [[-1, 0], [0, 1], [1, 0], [0, -1]]
        self.diagonal_directions = [[-1, -1], [-1, 1], [1, 1], [1, -1]]
        self.farm_land = None
        self.height = None
        self.width = None

    def addBlackPixel(self, band):
        height = len(band)
        width = len(band[0])
        arr = []
        new_boundary = [0 for i in range(width + 2)]

        arr.append(new_boundary)

        for ind in range(len(band)):
            row = list(band[ind])
            row.insert(0, 0)
            row.append(0)
            arr.append(row)

        arr.append(new_boundary)

        return arr

    def addBlackPixelToSingleChannel(self, band):
        added_pixel_band = np.array(self.addBlackPixel(band))
        return added_pixel_band

    def update(self, band):
        self.farm_land = self.addBlackPixelToSingleChannel(band)
        self.height = len(self.farm_land)
        self.width = len(self.farm_land[0])
        self.visited = np.zeros([self.height, self.width], dtype=int)

    def isBlackPixel(self, x, y):
        if self.farm_land[x][y] == 0:
            return True
        return False

    def isColorPixel(self, x, y):
        if not self.isBlackPixel(x, y):
            return True
        return False

    def isPointSafe(self, x, y):
        if x >= 0 and x < self.height and y >= 0 and y < self.width:
            return True
        return False

    def isVisited(self, x, y):
        if self.visited[x][y] == 1:
            return True
        return False

    def isNotVisited(self, x, y):
        if not self.isVisited(x, y):
            return True
        return False

    def makeVisit(self, x, y):
        self.visited[x][y] = 1

    def findFirstBoundary(self):
        ref_x, ref_y = self.height - 1, self.width - 1
        for dir in self.directions:
            new_x, new_y = ref_x, ref_y
            while True:
                new_x, new_y = new_x + dir[0], new_y + dir[1]
                if self.isPointSafe(new_x, new_y):
                    if self.isColorPixel(new_x, new_y):
                        return new_x - dir[0], new_y - dir[1]
                else:
                    break

    def collect_boundaries(self, x, y):
        for dir in self.directions:
            new_x, new_y = x + dir[0], y + dir[1]
            if self.isPointSafe(new_x, new_y):
                if self.isColorPixel(new_x, new_y):
                    if self.isNotVisited(new_x, new_y):
                        self.boundary_list.append([new_x, new_y])
                        self.makeVisit(new_x, new_y)

    def condition(self, x, y):
        if self.isPointSafe(x, y):
            if self.isNotVisited(x, y):
                if self.isBlackPixel(x, y):
                    for dir in self.directions:
                        new_x, new_y = x + dir[0], y + dir[1]
                        if self.isPointSafe(new_x, new_y):
                            if self.isColorPixel(new_x, new_y):
                                return True
        return False

    def findBoundaries(self, x, y):
        while True:
            self.s.push([x, y])
            self.makeVisit(x, y)
            self.collect_boundaries(x, y)

            found_x, found_y = None, None
            for dir in self.straight_directions:
                new_x, new_y = x + dir[0], y + dir[1]
                if self.condition(new_x, new_y):
                    found_x, found_y = new_x, new_y
                    break

            if found_x is None and found_y is None:
                for dir in self.diagonal_directions:
                    new_x, new_y = x + dir[0], y + dir[1]
                    if self.condition(new_x, new_y):
                        found_x, found_y = new_x, new_y
                        break

            if found_x is not None and found_y is not None:
                x, y = found_x, found_y
            else:
                self.s.pop()
                if self.s.isEmpty():
                    break
                coordinate = self.s.pop()
                x, y = coordinate[0], coordinate[1]

    def remove_corner_coordinates(self, boundary):
        new_coordinates = []
        for pt in boundary:
            if pt[0] == 0 or pt[0] == self.height - 1:
                continue
            elif pt[1] == 0 or pt[1] == self.width - 1:
                continue
            else:
                new_coordinates.append([pt[0] - 1, pt[1] - 1])
        return new_coordinates

    def findBoundary(self, band):
        self.update(band)
        x, y = self.findFirstBoundary()
        AppLogger.info("MSConvexHull, \tFinding the Boundary")
        start = time.time()
        self.findBoundaries(x, y)
        end = time.time()
        AppLogger.info(f"MSConvexHull, \tFound boundaries in {end - start} Sec")
        removed_corner_boundary = self.remove_corner_coordinates(self.boundary_list)
        return removed_corner_boundary


def pix_to_geo(gdal_dataset):
    cv2_image = np.array(gdal_dataset.GetRasterBand(1).ReadAsArray())
    pixel_coordinates = get_boundary(cv2_image)
    ds = gdal_dataset
    old_cs = osr.SpatialReference()
    old_cs.ImportFromWkt(ds.GetProjectionRef())

    new_cs = osr.SpatialReference()
    new_cs.ImportFromEPSG(4326)  # EPSG code for WGS 84

    transform = osr.CoordinateTransformation(old_cs, new_cs)

    new_boundary = []
    for point in pixel_coordinates:
        x, y = point[0], point[1]
        xoff, a, b, yoff, d, e = ds.GetGeoTransform()
        lon = a * x + b * y + xoff
        lat = d * x + e * y + yoff
        lon, lat, _ = transform.TransformPoint(lon, lat)
        new_boundary.append(GeoCoordinate(longitude=lat, latitude=lon))
    
    return new_boundary

def get_boundary(cv2_image):
    """Requires grayscale image."""
    obj = ExtractBoundary()
    img = cv2_image
    AppLogger.info("MSConvexHull, Finding boundary Coords...")
    boundary = obj.findBoundary(img)
    AppLogger.info(f"MSConvexHull, Totally {len(boundary)} extracted coordinates")
    vertices = np.array(boundary)
    hull = ConvexHull(vertices)
    convex_boundary = vertices[hull.vertices]
    AppLogger.info(f"MSConvexHull, Totally {len(convex_boundary)} convexal coordinates")
    convex_boundary = convex_boundary.tolist()
    rotated_boundary_coordinates = []
    for pt in convex_boundary:
        rotated_boundary_coordinates.append([pt[1], pt[0]])
    rotated_boundary_coordinates.append(rotated_boundary_coordinates[0])
    return rotated_boundary_coordinates


def extract_ms_boundary_coordinates(image: 'Orthophoto'):
    """
    """
    return pix_to_geo(image.ds)
    
    

if __name__ == '__main__':
    p = r"e:\STITCHED_IMAGES\DAY_1\TP1\07-02-2024_DAY1_MS_TP1_ALT-120m_VEL-5ms_OVERLAP-80_ODM-MNF15K-FASTORTHOPHOTO-orthophoto.tif"
    ds = gdal.Open(p)
   

    print(pix_to_geo(ds))