import sys
import os
sys.path.append(os.getcwd())
from concurrent.futures import ThreadPoolExecutor
from core.app_logger import AppLogger
from core.utils.unzip import unzip
from core.raw_ms_image import RawMSImage
from core.raw_rgb_image import RawRGBImage
from core.utils.paths import Paths
from core.kml import KML
from shapely import MultiPoint, MultiPolygon, Point, Polygon
from shapely.ops import nearest_points

class PreStitchProcessing:
    """
    """

    class ImageType:
        RGB  = "RGB"
        MS  = "MS"

    KMLS_PATH = Paths.kmls_path()

    @staticmethod
    def __unzip_files(path):
        """
        """
        unzip(path_to_zip_file=path, output_dir=os.path.join())

    
    @staticmethod
    def __get_images(path:str)-> list[RawRGBImage]|list[RawMSImage]:
        """
        Walks through the specified path and returns the list of all MS images 
        that have all bands.
        """
        executor = ThreadPoolExecutor()
        images = []
        for dir, subdirs, files in os.walk(path):
            if len(files)>0:
                if len(list(filter(lambda x: '.tif' in x, files)))>0:
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

                                def append_ms_image(a, b, c, d, e, images):
                                    image = RawMSImage(
                                        os.path.join(dir, a),
                                        os.path.join(dir, b),
                                        os.path.join(dir, c),
                                        os.path.join(dir, d),
                                        os.path.join(dir, e)
                                    )
                                    images.append(image)

                                executor.submit(append_ms_image, a, b, c, d, e, images)
                                type_ = PreStitchProcessing.ImageType.MS
                
                if len(list(filter(lambda x:'.JPG' in x, files)))>0:
                    type_ = PreStitchProcessing.ImageType.RGB
                    for file in files:
                        im_path = os.path.join(dir, file)

                        def append_rgb_image(path, images):
                            image = RawRGBImage(path)
                            images.append(image)

                        executor.submit(append_rgb_image, im_path, images)
        
        executor.shutdown(wait=True)
        return (type_, images)
    

    @staticmethod
    def __get_images_in_kml(kml:KML, 
                            images:list[RawRGBImage]|list[RawMSImage]
                            )->tuple[list[RawRGBImage]|list[RawMSImage], list[RawRGBImage]|list[RawMSImage]]:
        """
        """
        images_in_kml = list()
        images_in_neighborhood = list()
        AppLogger.info(f"PreStitchProcessing, Finding images in {kml}")
        for image in images:
            if image.is_in_polygon(kml.kml_polygon):
                images_in_kml.append(image)
            else:
                images_in_neighborhood.append(image)

        return images_in_kml, images_in_neighborhood


    @staticmethod
    def __read_kmls()->list[KML]:
        """
        """
        kmls_list = list()

        for kml_file in os.listdir(PreStitchProcessing.KMLS_PATH):
            kml_path = os.path.join(PreStitchProcessing.KMLS_PATH, kml_file)
            kml = KML(kml_path)
            kmls_list.append(kml)

        return kmls_list
    

    @staticmethod
    def __get_images_from_neighborhood_ms(kml:KML, images_in_neighboorhood:list[RawMSImage])->tuple[list[RawMSImage], list[RawMSImage]]:
        """
        """
        # 
        new_images = list()
        new_neighboorhood_images = list()
        lats = []
        lons = []
        neighboorhood_multipoint = MultiPoint([(image.geo_location.LAT, image.geo_location.LON) for image in images_in_neighboorhood])
        for coord in kml.kml_polygon.exterior.coords:
            _, nearest_image_loc = nearest_points(Point(coord), neighboorhood_multipoint)
            lat, lon = nearest_image_loc.x, nearest_image_loc.y
            lats.append(lat)
            lons.append(lon)
        
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)

        new_polygon = Polygon(
            [
                (min_lat, min_lon),
                (min_lat, max_lon),
                (max_lat, min_lon),
                (max_lat, max_lon),
                (min_lat, min_lon)

            ]
        )
        for image in images_in_neighboorhood:
            # print(new_polygon, image.geo_loc_point)
            if new_polygon.contains(image.geo_loc_point):
                AppLogger.info(f"PreStitchProcessing, New image found for {kml}: {image}")
                new_images.append(image)
            else:
                new_neighboorhood_images.append(image)

        return new_images, new_neighboorhood_images
            
    
    @staticmethod
    def __sort_images_from_kmls(path_to_images:str,
                                 min_images_per_kml_rgb:int=10,
                                 min_images_per_kml_ms:int=10
                                 )->list[dict]:
        """
        """

        kmls = PreStitchProcessing.__read_kmls()
        image_type, images = PreStitchProcessing.__get_images(path=path_to_images)
        kmls_dict_list = list()
        for kml in kmls:
            images_in_kml, images_in_neighboorhood = PreStitchProcessing.__get_images_in_kml(kml=kml, images=images)
            k=1
            if image_type == PreStitchProcessing.ImageType.MS:
                while len(images_in_kml)<min_images_per_kml_ms:
                    if k>3:
                        break
                    AppLogger.info(f"Not enough images in {kml} k={k}: {len(images_in_kml)}")
                    new_images, images_in_neighboorhood = PreStitchProcessing.__get_images_from_neighborhood_ms(kml=kml, 
                                                                                                                images_in_neighboorhood=images_in_neighboorhood)
                    for new_image in new_images:
                        images_in_kml.append(new_image)
                    k+=1
            AppLogger.info(f"Found {len(images_in_kml)} for {kml}")
            kmls_dict_list.append(
                {
                    "KML": kml.name,
                    "images": images_in_kml,
                    "type": image_type
                }
                )
        return kmls_dict_list
    

    @staticmethod
    def __transfer_images(images_dict:list[dict]):
        """
        """
        



if __name__ == "__main__":
    path = r"C:\Users\sahas\OneDrive\Desktop\Comp\000"
    # print(list(map(os.path.join, ["C:", "D:", "E:"], ["a", "b", "c"])))
    PreStitchProcessing._PreStitchProcessing__sort_images_from_kmls(path)
    # path = os.getcwd()
    
