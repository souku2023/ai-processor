import os
from shapely.geometry import Polygon
from shapely.affinity import translate, rotate
import matplotlib.pyplot as plt
if __name__ == '__main__':
    import sys
    sys.path.append(os.getcwd())

from core.kml import KML
from core.utils.paths import Paths
from core.orthophoto import Orthophoto
from core.pixel_coordinates import PixelCoordinate
from core.geo_coordinate import GeoCoordinate

from osgeo import gdal
gdal.UseExceptions()

import typing

    

class PostStitchProcessing:
    """
    """
    @staticmethod
    def __read_kmls()->list[KML]:
        """
        """
        kmls_list = list()

        for kml_file in os.listdir(Paths.kmls_path()):
            kml_path = os.path.join(Paths.kmls_path(), kml_file)
            kml = KML(kml_path)
            kmls_list.append(kml)

        return kmls_list

    KMLS_LIST = __read_kmls()

    @staticmethod
    def offest_kml_polygon(kml:KML, 
                           offset:list[float, float]|tuple[float, float]):
        """
        Translate the polygon from the KML by `offset` units
        """
        return translate(kml.border_polygon, xoff=offset[0], yoff=offset[1])
    
    @staticmethod
    def rotate_kml_polygon(kml:KML, 
                           angle:list[float]|tuple[float]|float):
        """
        Rotate the polygon described from the KML by `angle` degrees
        """
        return rotate(kml.border_polygon, angle=angle)
    
    @staticmethod
    def rectify_kml_border_polygon(orthophoto:Orthophoto, kml:KML):
        """
        """


    @staticmethod
    def get_corrected_polygon(orthophoto:Orthophoto, kml:KML):
        """
        """
        polygon = kml.border_polygon
        # Plot the Grayscale Orthophoto 
        plt.imshow(orthophoto.ds.GetRasterBand(1).ReadAsArray())
        pixel_coords = list()
        # Get the pixel coordinates of the geo coordinates from Orthophoto
        geo_coords = polygon.exterior.coords
        for coord in geo_coords:
            # print(pixel_coords)
            geo_coord = GeoCoordinate(longitude=coord[0], latitude=coord[1])
            pix_coord = orthophoto.lat_lon_to_pixel(geo_coords=geo_coord)
            pixel_coords.append(pix_coord)
        # Plot the original Geo Coordinates on the orthophoto to visualise
        polygon_fill = plt.fill([p.X for p in pixel_coords], 
                                [p.Y for p in pixel_coords], 
                                c='r', 
                                alpha=0.2
                                )[0]
        # Make Plot fullscreen
        mng = plt.get_current_fig_manager()
        mng.window.state('zoomed') 
        # Plot the first pixel of the border_polygon
        first_geo_coordinate = GeoCoordinate(longitude=geo_coords[0][0], latitude=geo_coords[0][1])
        first_pixel_coord = orthophoto.lat_lon_to_pixel(first_geo_coordinate)
        first_pixel_plot = plt.scatter(first_pixel_coord.X, 
                                       first_pixel_coord.Y,
                                       c='orange', s=5)
        # Get User input to place the new pixel coordinate in place
        rectified_polygon_fill = None
        plt.title("Mark the Yellow point to the right place")
        while True:
            new_first_pixel_coords = plt.ginput(1, 
                                               timeout=60.0, 
                                               show_clicks=True, 
                                               mouse_add=1, 
                                               mouse_stop=3)
            if not new_first_pixel_coords:
                break
            # Remove any rectified polygons if they exist
            if rectified_polygon_fill is not None:
                rectified_polygon_fill.remove()
            
            new_first_pixel_coord = new_first_pixel_coords[0]
            first_pixel_plot.remove()
            first_pixel_plot = plt.scatter(new_first_pixel_coord[0], 
                                           new_first_pixel_coord[1], 
                                           c='orange', s=5)    
            first_pixel_coordinate = PixelCoordinate(new_first_pixel_coord[0], 
                                                     new_first_pixel_coord[1])   
            new_first_geo_coordinate = orthophoto.pixel_to_lat_lon(first_pixel_coordinate)     
            offset = first_geo_coordinate - new_first_geo_coordinate 
            new_border_polygon = PostStitchProcessing.offest_kml_polygon(
                kml=kml, offset=offset
                )
            new_geo_coords = new_border_polygon.exterior.coords
            for coord in new_geo_coords:
                geo_coord = GeoCoordinate(longitude=coord[0], latitude=coord[1])
                print(geo_coord)
                pix_coord = orthophoto.lat_lon_to_pixel(geo_coords=geo_coord)
                pixel_coords.append(pix_coord)
            # Plot the new Geo Coordinates on the orthophoto to visualise
            rectified_polygon_fill = plt.fill(
                [p.Y for p in pixel_coords], 
                [p.X for p in pixel_coords], 
                c='yellow', 
                alpha=0.2)[0]           
            plt.scatter(pixel_coords[0].X, pixel_coords[0].Y)              
        # Get the 
        a = 0 
        plt.close()
        return polygon, new_border_polygon

        
        
        plt.show()
        
        

        
    

if __name__ == '__main__':
    ms_p = r"c:\Users\USER\Downloads\60Meter_80overlap_5ms_000_STITCHED-orthophoto.tif"
    rgb_p = r"e:\RGB_STITCHED\DAY1\MORN-07-02-2024_DAY_1_TP2_ALT-80m_VEL-5ms_OVERLAP-80-orthophoto.tif"
    a = Orthophoto(ms_p)
    kml = PostStitchProcessing.KMLS_LIST[0]
    poly, new_poly = PostStitchProcessing.get_corrected_polygon(orthophoto=a, kml=kml)
    # import matplotlib.pyplot as plt
    original_poly_x, original_poly_y = poly.exterior.xy
    plt.fill(original_poly_x, original_poly_y, c='red', alpha=0.2)
    # print(new_poly)
    new_poly_x, new_poly_y = new_poly.exterior.xy
    plt.fill(new_poly_x, new_poly_y, c='blue', alpha=0.2)
    plt.show()
        