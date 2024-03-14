from osgeo import gdal, osr, ogr
import numpy as np
import os
from shapely.geometry import Polygon, mapping
import rioxarray

if __name__ == '__main__':
    import sys
    sys.path.append(os.getcwd())

from core.app_logger import AppLogger
from core.utils.paths import Paths
from core.pixel_coordinates import PixelCoordinate
from core.geo_coordinate import GeoCoordinate
from core.utils.convex_hull import ConvexHull
import typing
if typing.TYPE_CHECKING:
    from core.kml import KML


class Orthophoto:
    """
    """

    class Type:
        RGB = "RGB"
        MS = "MS"

    BAND_MAPPING = {1: "Blue", 
                    2: "Green", 
                    3: "Red", 
                    4: "NIR",
                    5: "RedEdge"}
    
    RGB_BAND_MAPPING = {1: "Blue", 
                        2: "Green", 
                        3: "Red"}
    
    def __init__(self, path:str) -> None:
        """
        """
        # Load the Orthophoto using GDAL
        if path is not None:
            if os.path.exists(path):
                self.path = path
                self.ds = gdal.Open(path)
                # Get Shape
                self.width = self.ds.RasterXSize
                self.height = self.ds.RasterYSize
                self.gt = self.ds.GetGeoTransform()
                self.gp = self.ds.GetProjection()
                # Read the Orthophoto as a numpy ndarray like opencv 
                self.image_array = np.array(self.ds.ReadAsArray())
                self.name = os.path.basename(path).split('.')[0]
                self.type = None
                self.output_dir = os.path.join(Paths.output_dir(), self.name)
                # self.bands_folder = os.path.join(self.output_dir, 'bands')
            else:
                raise Exception("Please enter valid path")
        else:
            raise Exception("Please Specifiy image path")
        # Initialise properties.
        self.__initialise()
        
    
    def __get_image_type(self):
        """
        If the number of RasterBands is less than 4, the Orthohpoto is RGB 
        Else the Orthohpoto is Multispectral. This works for now
        """
        num_bands = self.ds.RasterCount
        if num_bands < 5:
            self.type = Orthophoto.Type.RGB
        else:
            self.type = Orthophoto.Type.MS 

    def __initialise(self):
        """
        Initialise the properties of coordinate transforms, orthohoto type, 
        and Convex Hull of the Orthophoto.
        """
        # Build Coordinate Transform for Geo Coordinates to Pixel Coordinates
        point_srs = osr.SpatialReference()
        point_srs.ImportFromEPSG(4326)
        point_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        file_srs = osr.SpatialReference()
        file_srs.ImportFromWkt(self.gp)
        self.__ct_lat_lon_to_pixel = osr.CoordinateTransformation(point_srs, 
                                                                  file_srs)
        # Build Coordinate Transform for Pixel Coordinate to Geo Coordinate
        source = osr.SpatialReference(wkt=self.gp)
        target = osr.SpatialReference()
        target.ImportFromEPSG(4326)
        self.__ct_pixel_to_lat_lon = osr.CoordinateTransformation(source, 
                                                                  target)
        # Get image type using GDAL
        self.__get_image_type()
        # Get Convex Hull of the Image
        self.convex_hull = ConvexHull(self)
        self.convex_hull_polygon = self.convex_hull.polygon

    def pixel_to_lat_lon(self, pix_coord:PixelCoordinate)->GeoCoordinate:
        """
        Converts PixelCoordinate to GeoCoordinate.
        """
        pixel_x = pix_coord.X
        pixel_y = pix_coord.Y

        def __pixel_to_world(geo_matrix, x, y):
            ul_x = geo_matrix[0]
            ul_y = geo_matrix[3]
            x_dist = geo_matrix[1]
            y_dist = geo_matrix[5]
            _x = x * x_dist + ul_x
            _y = y * y_dist + ul_y
            return _x, _y

        def __find_spatial_coordinate_from_pixel(transform, x, y):
            world_x, world_y = __pixel_to_world(self.gt, x, y)
            point = ogr.Geometry(ogr.wkbPoint)
            point.AddPoint(world_x, world_y)
            point.Transform(transform)
            return point.GetX(), point.GetY()
        
        coordinates = __find_spatial_coordinate_from_pixel(self.__ct_pixel_to_lat_lon, pixel_x, pixel_y)
        return GeoCoordinate(latitude=coordinates[0], longitude=coordinates[1])
    
    def lat_lon_to_pixel(self, geo_coords:GeoCoordinate)->PixelCoordinate:
        """
        Converts GeoCoordinate to PixelCoordinate.
        """
        lat = geo_coords.LAT
        lon = geo_coords.LON
        mapx, mapy, z = self.__ct_lat_lon_to_pixel.TransformPoint(lon, lat)
        gt_inv = gdal.InvGeoTransform(self.gt)
        pixel_x, pixel_y = gdal.ApplyGeoTransform(gt_inv, mapx, mapy)

        return PixelCoordinate(pixel_x, pixel_y)
    
    def polygon_in_image(self, polygon:Polygon)->bool:
        """
        Checks if the given Polygon is inside the convex hull of the image.
        """
        return self.convex_hull_polygon.contains(polygon)
    
    def crop_image_from_kml(self, kml:'KML', output_path:str|None=None)->bool:
        """
        Crops an image based on given KML object.
        """
        # Save cropped image to the outputs dir if output path is not 
        # explicitly given
        if output_path is None:
            output_path = os.path.join(self.output_dir, f'{self.name}_cropped.tif')
        # Check if the given KML is inside the image it 
        if self.polygon_in_image(kml.border_polygon):
            try:
                # Create the output_dir if it does not exist
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                # Get a GeoJSON like mapping from Polygon
                geom = mapping(kml.border_polygon)
                # Open image with rioxarray
                rds = rioxarray.open_rasterio(self.path, parse_coordinates=True)
                # Crop image from GeoJSON
                masked = rds.rio.clip([geom], "EPSG:4326", drop=True)
                # Save the Cropped image to output_path
                masked.rio.to_raster(output_path)
                AppLogger.info(
                    f"Orthophoto:{self.name}: Cropped image saved to: {output_path}"
                    )
                return True
            except Exception as e:
                AppLogger.warn(
                    f"Orthophoto, Failed to crop with exception: {e.__class__.__qualname__}: {e}"
                    )
                return False
        else: 
            AppLogger.warn(f"Orthophoto:{self.name}, KML not in image")
            return False

        
    
if __name__ == '__main__':
    ms_p = r"c:\Users\USER\Downloads\60Meter_80overlap_5ms_000_STITCHED-orthophoto.tif"
    rgb_p = r"e:\RGB_STITCHED\DAY1\MORN-07-02-2024_DAY_1_TP2_ALT-80m_VEL-5ms_OVERLAP-80-orthophoto.tif"
    a = Orthophoto(ms_p)
    coords = [75.7432796564809, 14.712272003727593]
    geo = GeoCoordinate(latitude=coords[1], longitude=coords[0])
    print(geo)
    pix = a.lat_lon_to_pixel(geo_coords=geo)
    print(pix)
    geo2 = a.pixel_to_lat_lon(pix_coord=pix)
    print(geo2)
    # print(a.convex_hull_polygon)
    import matplotlib.pyplot as plt

    plt.imshow(a.ds.GetRasterBand(1).ReadAsArray())
    for coord in a.convex_hull_polygon.exterior.coords:
        p = a.lat_lon_to_pixel(geo_coords=GeoCoordinate(latitude=coord[1], longitude=coord[0]))
        plt.scatter(p.X, p.Y,  c='red', s=5)
    plt.show()
