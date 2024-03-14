import numpy as np
from scipy.spatial import ConvexHull
import cv2
import time 

import typing
if typing.TYPE_CHECKING:
    from core.orthophoto import Orthophoto

if __name__ == '__main__':
    import sys, os
    sys.path.append(os.getcwd())

from core.pixel_coordinates import PixelCoordinate
from core.app_logger import AppLogger

class Stack:
    def __init__(self):
        self.stack = []
        self.top = -1

    def push(self, element):
        self.stack.append(element)
        self.top = self.top + 1

    def pop(self):
        if self.top == -1:
            AppLogger.warn("Stack Underflow")
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
        AppLogger.info(f"RGBConvexHull, self.stack[self.top]")

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

    def addBlackPixel(self, farm_land):
        height = len(farm_land)
        width = len(farm_land[0])
        arr = []
        new_boundary = [0 for i in range(width + 2)]

        arr.append(new_boundary)

        for ind in range(len(farm_land)):
            row = list(farm_land[ind])
            row.insert(0, 0)
            row.append(0)
            arr.append(row)

        arr.append(new_boundary)

        return arr

    def addBlackPixelToThreeChannel(self, img):
        img = np.moveaxis(img, -1, 0)
        blue_channel = img[0]
        green_channel = img[1]
        red_channel = img[2]
        added_pixel_blue_channel = np.array(self.addBlackPixel(blue_channel))
        added_pixel_green_channel = np.array(self.addBlackPixel(green_channel))
        added_pixel_red_channel = np.array(self.addBlackPixel(red_channel))
        img = np.array([added_pixel_blue_channel,
                       added_pixel_green_channel, added_pixel_red_channel])
        return img

    def update(self, farm_land):
        self.farm_land = self.addBlackPixelToThreeChannel(farm_land)
        self.height = len(self.farm_land[0])
        self.width = len(self.farm_land[0][0])
        self.visited = np.zeros([self.height, self.width], dtype=int)

    def isBlackPixel(self, x, y):
        if self.farm_land[0][x][y] == 0 and self.farm_land[1][x][y] == 0 and self.farm_land[2][x][y] == 0:
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

            if found_x == None and found_y == None:
                for dir in self.diagonal_directions:
                    new_x, new_y = x + dir[0], y + dir[1]
                    if self.condition(new_x, new_y):
                        found_x, found_y = new_x, new_y
                        break

            if found_x != None and found_y != None:
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

    def findBoundary(self, farm_land):
        self.update(farm_land)
        x, y = self.findFirstBoundary()
        AppLogger.info("RGBConvexHull, Finding the Boundary")
        start = time.time()
        self.findBoundaries(x, y)
        end = time.time()
        AppLogger.info(f"RGBConvexHull, {end - start} Sec")
        removed_corner_boundary = self.remove_corner_coordinates(self.boundary_list)
        return removed_corner_boundary

def get_boundary_rgb(image_path):
    obj = ExtractBoundary()
    img = cv2.imread(image_path)
    boundary = obj.findBoundary(img)
    AppLogger.info(f"RGBConvexHull, Totally {len(boundary)} extracted coordinates")
    vertices = np.array(boundary)
    hull = ConvexHull(vertices)
    convex_boundary = vertices[hull.vertices]
    AppLogger.info(f"RGBConvexHull, Totally {len(convex_boundary)} convexal coordinates")
    convex_boundary = convex_boundary.tolist()
    rotated_boundary_coordinates = []
    for pt in convex_boundary:
        rotated_boundary_coordinates.append([pt[1], pt[0]])
    rotated_boundary_coordinates.append(rotated_boundary_coordinates[0])
    return rotated_boundary_coordinates


# get_boundary(r"G:\BAYER\PHASE-2\VISIT-1\DAY2_Morning_RGB_120m_5ms_049-062-064-063-50-orthophoto.tif")
def extract_rgb_boundary_coordinates(image: 'Orthophoto'):
        """
        """
        pix_coords = get_boundary_rgb(image.path)
        geo_coords = []
        for coord in pix_coords:
            geo_coord = image.pixel_to_lat_lon(
                pix_coord=PixelCoordinate(x=coord[1], y=coord[0]))
            geo_coords.append(geo_coord)
        
        return geo_coords