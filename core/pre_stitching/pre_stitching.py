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
        type_ = None
        for dir, subdirs, files in os.walk(path):
            # AppLogger.info(f"PreStitchProcessing, in {dir}")
            if len(files)>0:
                if len(list(filter(lambda x: '.tif' in x, files)))>0:
                    for file in files:
                        if '_1.tif' in file:
                            im_path = os.path.join(dir, file)
                            a = im_path
                            b = im_path.replace('_1.tif', '_2.tif')
                            c = im_path.replace('_1.tif', '_3.tif')
                            d = im_path.replace('_1.tif', '_4.tif')
                            e = im_path.replace('_1.tif', '_5.tif')
                            if ((os.path.basename(a) in files) and
                                (os.path.basename(b) in files) and
                                (os.path.basename(c) in files) and
                                (os.path.basename(d) in files) and
                                (os.path.basename(e) in files)):
                                # 
                                
                                # AppLogger.info(f"PreStitchProcessing, {a}")

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
    def __get_images_in_polygon(polygon:Polygon, 
                                images:list[RawRGBImage]|list[RawMSImage]
                                )->tuple[list[RawRGBImage]|list[RawMSImage], list[RawRGBImage]|list[RawMSImage]]:
        """
        """
        images_in_polygon = list()
        images_in_neighborhood = list()
        for image in images:
            if image.is_in_polygon(polygon):
                images_in_polygon.append(image)
            else:
                images_in_neighborhood.append(image)

        return (images_in_polygon, images_in_neighborhood)


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
    def __get_images_from_neighborhood_ms_kml(kml:KML, images_in_neighboorhood:list[RawMSImage])->tuple[list[RawMSImage], list[RawMSImage]]:
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
    def __get_images_in_neighborhood_polygon(polygon:Polygon, images_in_neighboorhood:list[RawRGBImage])->tuple[list[RawMSImage], list[RawMSImage]]:
        """
        """
        new_neighboorhood_images = list()
        new_images = list()
        lats = []
        lons = []
        neighboorhood_multipoint = MultiPoint([(image.geo_location.LAT, image.geo_location.LON) for image in images_in_neighboorhood])
        for coord in polygon.exterior.coords:
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
                AppLogger.info(f"PreStitchProcessing, New image found : {image}")
                new_images.append(image)
            else:
                new_neighboorhood_images.append(image)

        return new_images, new_neighboorhood_images

            
    
    @staticmethod
    def __sort_images_from_kmls(path_to_images:str,
                                 min_images_per_kml_rgb:int=100,
                                 min_images_per_kml_ms:int=10
                                 )->list[dict]:
        """
        """

        kmls = PreStitchProcessing.__read_kmls()
        image_type, images = PreStitchProcessing.__get_images(path=path_to_images)
        grouped_image_list = list()
        # If found images are Multispectral
        if image_type == PreStitchProcessing.ImageType.MS:
            for kml in kmls:
                images_in_kml, images_in_neighboorhood = PreStitchProcessing.__get_images_in_kml(kml=kml, images=images)
                k=1
            
                while len(images_in_kml)<min_images_per_kml_ms:
                    if k>3:
                        break
                    AppLogger.info(f"Not enough images in {kml} k={k}: {len(images_in_kml)}")
                    new_images, images_in_neighboorhood = PreStitchProcessing.__get_images_from_neighborhood_ms_kml(kml=kml, 
                                                                                                                images_in_neighboorhood=images_in_neighboorhood)
                    for new_image in new_images:
                        images_in_kml.append(new_image)
                    k+=1
            AppLogger.info(f"Found {len(images_in_kml)} for {kml}")
            grouped_image_list.append(
                {
                    "KML": kml.name,
                    "images": images_in_kml,
                    "type": image_type
                }
                )
        # If found images are RGB
        if image_type == PreStitchProcessing.ImageType.RGB:
            group1 = [
                "ECO_KA_HAV_RAN_BEL_046_1",
                "ECO_KA_HAV_RAN_BEL_078_1",
                "ECO_KA_HAV_RAN_BEL_060_3",
                "ECO_KA_HAV_RAN_BEL_005_5",
                "ECO_KA_HAV_RAN_BEL_009_1"
                ]
            group2 = [
                "ECO_KA_HAV_RAN_BEL_050_1",
                "ECO_KA_HAV_RAN_BEL_062_1",
                "ECO_KA_HAV_RAN_BEL_063_1",
                "ECO_KA_HAV_RAN_BEL_064_1",
                "ECO_KA_HAV_RAN_BEL_049_1"
            ]

            group1_polygons = []
            group2_polygons = []

            for kml in kmls:
                if kml.name in group1:
                    group1_polygons.append(kml.kml_polygon)
                elif kml.name in group2:
                    group2_polygons.append(kml.kml_polygon)

            multipolygons = [MultiPolygon(group1_polygons), MultiPolygon(group2_polygons)]

            for multipolygon in multipolygons:
                min_lat, min_lon, max_lat, max_lon = multipolygon.bounds
                AppLogger.info(multipolygon)
                new_polygon = Polygon(
                [
                    (min_lat, min_lon),
                    (min_lat, max_lon),
                    (max_lat, min_lon),
                    (max_lat, max_lon),
                    (min_lat, min_lon)
                ]
                )
                images_in_polygon, images_in_neighboorhood = PreStitchProcessing.__get_images_in_polygon(new_polygon, images)

            while len(images_in_polygon)<min_images_per_kml_rgb:
                new_images, new_neighboorhood_images = PreStitchProcessing.__get_images_in_neighborhood_polygon(polygon=new_polygon, 
                                                                         images_in_neighboorhood=images_in_neighboorhood)
                    
                for new_im in new_images:
                    images_in_polygon.append(new_im)

            

        return grouped_image_list
    

    @staticmethod
    def __transfer_images(images_dict:list[dict]):
        """
        """
        



if __name__ == "__main__":
    path = r"D:\data\13-Feb-2024_Day_7_ RGB_Images\DCIM\geotagged_images"
    # path = r"D:\data\11-Feb-2024_120meter_12ac_MS\Zoho WorkDrive (4)"
    # print(list(map(os.path.join, ["C:", "D:", "E:"], ["a", "b", "c"])))
    PreStitchProcessing._PreStitchProcessing__sort_images_from_kmls(path)
    # path = os.getcwd()
    
