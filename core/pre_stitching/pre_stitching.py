import sys
import os
sys.path.append(os.getcwd())
import json
from concurrent.futures import ThreadPoolExecutor
from core.app_logger import AppLogger
from core.utils.unzip import unzip
from core.raw_ms_image import RawMSImage
from core.raw_rgb_image import RawRGBImage
from core.utils.paths import Paths
from core.geo_coordinate import GeoCoordinate
from core.kml import KML
from shapely import MultiPoint, MultiPolygon, Point, Polygon
from shapely.ops import nearest_points, unary_union
# import geopandas as gpd
import shutil
import matplotlib.pyplot as plt

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
    def __check_for_path_json(path:str)->dict|None:
        """
        Checks ./resources/image_details to check if there is a JSON file 
        corresponsing to `path`. Returns a dict containing the contents as a 
        dict if it does. Returns `None` otherwise.

        ## Args:
        `path` - (Required): Path to image directory.

        ## Returns
        `dict | None`
        """
        os.makedirs(Paths.image_json(), exist_ok=True)
        json_path = os.path.join(Paths.image_json(), 
                                 path.replace("\\", "_").replace('/', '_').replace(":", "").replace(" ", "-")+".json")
        
        if os.path.exists(json_path):
            with open(json_path) as image_details:
                try:
                    image_details_dict = json.load(image_details)
                    image_details.close()
                except json.decoder.JSONDecodeError as e:
                    AppLogger.info(f"PreStitchProcessing, Unable to read file : {e}")
                    return None

            return image_details_dict
        else:
            return None
        

    @staticmethod
    def __write_json(path:str, images_list:list[dict])->None:
        """
        Writes a JSON file to store required image details in the path
        """
        json_path = os.path.join(Paths.image_json(), 
                                 path.replace("\\", "_").replace('/', '_').replace(":", "").replace(" ", "-")+".json")
        
        if len(images_list)>0:
            AppLogger.info(f"PreStitchProcessing, Writing JSON file for path: {path} as {os.path.basename(json_path)}")
            with open(json_path, 'w') as image_details:
                json.dump(images_list, image_details, indent=4) 
                image_details.close()
        else:
            AppLogger.warn("PreStitchProcessing, Cannot write JSON : list size is 0")

    
    @staticmethod
    def __get_images(path:str)-> list[RawRGBImage]|list[RawMSImage]:
        """
        Walks through the specified path and returns the list of all MS images 
        that have all bands.
        """
        executor = ThreadPoolExecutor()
        images = []
        type_ = None
        if PreStitchProcessing.__check_for_path_json(path) is None:
            AppLogger.info(f"PreStitchProcessing, Did not find JSON for {path}")
            AppLogger.info(f"PreStitchProcessing, Reading image metadata using exiftool.")
            images_detail_list = list()
            for dir, subdirs, files in os.walk(path):
                # AppLogger.info(f"PreStitchProcessing, in {dir}")
                if len(files)>0:
                    if len(list(filter(lambda x: '.tif' in x, files)))>0:
                        type_ = PreStitchProcessing.ImageType.MS
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

                                    def append_ms_image(a, b, c, d, e, images:list, images_detail_list:list):
                                        image = RawMSImage(
                                            os.path.join(dir, a),
                                            os.path.join(dir, b),
                                            os.path.join(dir, c),
                                            os.path.join(dir, d),
                                            os.path.join(dir, e)
                                        )
                                        images.append(image)
                                        image_detail = dict()
                                        image_detail["LAT"] = image.geo_location.LAT
                                        image_detail["LON"] = image.geo_location.LON
                                        image_detail["PATH"] = a
                                        image_detail["TYPE"] = PreStitchProcessing.ImageType.MS
                                        images_detail_list.append(image_detail)

                                    executor.submit(append_ms_image, a, b, c, d, e, images, images_detail_list)
                                    
                        
                    if len(list(filter(lambda x:'.JPG' in x, files)))>0:
                        type_ = PreStitchProcessing.ImageType.RGB
                        for file in files:
                            im_path = os.path.join(dir, file)

                            def append_rgb_image(path, images:list, images_detail_list:list):
                                image = RawRGBImage(path)
                                images.append(image)
                                images_detail_list.append(
                                    {
                                        "LAT": image.geo_location.LAT,
                                        "LON": image.geo_location.LON,
                                        "PATH": path,
                                        "TYPE": type_
                                    }
                                )

                            executor.submit(append_rgb_image, im_path, images, images_detail_list)
            executor.shutdown(wait=True)
            PreStitchProcessing.__write_json(path, images_detail_list)
            return (type_, images)
        
        else:
            AppLogger.info(f"Found JSON file for: {path}")
            images_detail = PreStitchProcessing.__check_for_path_json(path)
            for image in images_detail:
                lat = image["LAT"]
                lon = image["LON"]
                image_path = image["PATH"]
                type_ = image["TYPE"]

                if type_ == PreStitchProcessing.ImageType.MS:
                    images.append(
                        RawMSImage(
                            r=image_path,
                            g=image_path.replace('_1.tif', '_2.tif'),
                            b=image_path.replace('_1.tif', '_3.tif'),
                            n=image_path.replace('_1.tif', '_4.tif'),
                            re=image_path.replace('_1.tif', '_5.tif'),
                            geo_coords=GeoCoordinate(latitude=lat, longitude=lon)
                        )
                    )

                elif type_ == PreStitchProcessing.ImageType.RGB:
                    images.append(
                        RawRGBImage(
                            path=image_path,
                            geo_coords=GeoCoordinate(latitude=lat, longitude=lon)
                        )
                    )
            AppLogger.info(f"PreStitchProcessing, Read {len(images)} images")
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
            # print(kml.border_polygon, image.geo_location)
            if image.is_in_polygon(kml.border_polygon):
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
        # print(len(images))
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
        neighboorhood_multipoint = MultiPoint([(image.geo_location.LON, image.geo_location.LAT) for image in images_in_neighboorhood])
        for coord in kml.border_polygon.exterior.coords:
            _, nearest_image_loc = nearest_points(Point(coord), neighboorhood_multipoint)
            lat, lon = nearest_image_loc.y, nearest_image_loc.x
            lats.append(lat)
            lons.append(lon)
        
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)

        new_polygon = Polygon(
                [
                    (min_lat, min_lon),
                    (max_lat, min_lon),
                    (max_lat, max_lon),
                    (min_lat, max_lon),
                    (min_lat, min_lon)
                ]
                )
        for image in images_in_neighboorhood:
            # print(new_polygon, image.geo_loc_point)
            if new_polygon.contains(image.geo_loc_point):
                # AppLogger.info(f"PreStitchProcessing, New image found for {kml}: {image}")
                new_images.append(image)
            else:
                new_neighboorhood_images.append(image)
                
        # plt.fill(*kml.border_polygon.exterior.xy, alpha=0.2, c='r')
        # plt.fill(*new_polygon.exterior.xy, alpha=0.2, c='g')
        # plt.show()

        return new_images, new_neighboorhood_images
    
    @staticmethod
    def __get_images_from_neighborhood_buffered_border_polygon(images_in_neighboorhood:list[RawMSImage], 
                                                               kml:KML|None=None, 
                                                               polygon:Polygon|None=None)->tuple[list[RawMSImage], list[RawMSImage]]:
        """
        """
        # 
        if kml is not None:
            polygon = kml.border_polygon
        elif kml is None and polygon is None:
            raise Exception("At least 1 of polygon on kml must be specified")
        new_images = list()
        new_neighboorhood_images = list()
        lats = []
        euclidean_distances_list = []
        neighboorhood_multipoint = MultiPoint([(image.geo_location.LON, image.geo_location.LAT) for image in images_in_neighboorhood])
        for coord in polygon.exterior.coords:
            origin, nearest_image_loc = nearest_points(Point(coord), neighboorhood_multipoint)
            euclidean_distance = Point(coord).distance(nearest_image_loc)
            euclidean_distances_list.append(euclidean_distance)
            # print(euclidean_distance)
        
        max_euclidean_dist = max(euclidean_distances_list)
        # print(max_euclidean_dist)
        
        new_polygon = polygon.buffer(1*max_euclidean_dist)
            
        for image in images_in_neighboorhood:
            # print(new_polygon, image.geo_loc_point)
            if new_polygon.contains(image.geo_loc_point):
                new_images.append(image)
            else:
                new_neighboorhood_images.append(image)
                
        PreStitchProcessing.__visualise_images_in_polygon(
            polygon=[polygon, new_polygon], 
            points=[im.geo_loc_point for im in new_images], 
            timeout=1
            )

        return new_images, new_neighboorhood_images
    

    @staticmethod
    def __get_images_in_neighborhood_polygon(polygon:Polygon, 
                                             images_in_neighboorhood:list[RawRGBImage]
                                             )->tuple[list[RawMSImage], list[RawMSImage]]:
        """
        """
        new_neighboorhood_images = list()
        new_images = list()
        lats = []
        lons = []
        neighboorhood_multipoint = MultiPoint([(image.geo_location.LON, image.geo_location.LAT) for image in images_in_neighboorhood])
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
                    (max_lat, min_lon),
                    (max_lat, max_lon),
                    (min_lat, max_lon),
                    (min_lat, min_lon)
                ]
                )
        plot_list = [new_polygon]
        for image in images_in_neighboorhood:
            # print(new_polygon, image.geo_loc_point)
            if new_polygon.contains(image.geo_loc_point):
                AppLogger.info(f"PreStitchProcessing, New image found : {image}")
                new_images.append(image)
                plot_list.append(image.geo_loc_point)
            else:
                new_neighboorhood_images.append(image)

        return new_images, new_neighboorhood_images
    
    @staticmethod
    def __sort_images_from_kmls(path_to_images:str,
                                 min_images_per_kml_rgb:int=100,
                                 min_images_per_kml_ms:int=100,
                                 extra_image_search_iteration:int=1
                                 )->list[dict]:
        """
        Iterates through all the images and
        """
        # Read KMLs from the directory ./resources/kmls
        kmls = PreStitchProcessing.__read_kmls()
        
        # Load the images with their Geo locations and paths
        image_type, images = PreStitchProcessing.__get_images(path=path_to_images)
        grouped_image_list = list()

        # Iterate through the KMLs to find images corresponding to them.
        for kml in kmls:
            (images_in_kml, 
             images_in_neighboorhood) = PreStitchProcessing.__get_images_in_kml(kml=kml, images=images)
            k=0
            # If image is Multispectral
            if image_type == PreStitchProcessing.ImageType.MS:
                while len(images_in_kml)<min_images_per_kml_ms and len(images_in_kml)>0:
                    if k>=extra_image_search_iteration:
                        break
                    AppLogger.info(
                        f"PreStitchProcessing, Not enough images in {kml} {len(images_in_kml)} [min: {min_images_per_kml_ms}]")
                    AppLogger.info(
                        f"PreStitchProcessing, Searching for images in neighboorhood k={k} using buffered border polygon.")
                    # Get images in neighborhood using a buffered polygon; i.e. a padded polygon.
                    new_images, images_in_neighboorhood = PreStitchProcessing.__get_images_from_neighborhood_buffered_border_polygon(
                        kml=kml, 
                        images_in_neighboorhood=images_in_neighboorhood
                        )
                    # Append the new images to the list of images
                    for new_image in new_images:
                        images_in_kml.append(new_image)
                    k+=1
            # If imaage is RGB
            if image_type == PreStitchProcessing.ImageType.RGB:
                while len(images_in_kml)<min_images_per_kml_rgb and len(images_in_kml)>0:
                    if k>=extra_image_search_iteration:
                        break
                    AppLogger.info(
                        f"PreStitchProcessing, Not enough images in {kml} {len(images_in_kml)} [min: {min_images_per_kml_rgb}]")
                    AppLogger.info(
                        f"PreStitchProcessing, Searching for images in neighboorhood k={k} using buffered border polygon")
                    new_images, images_in_neighboorhood = PreStitchProcessing.__get_images_from_neighborhood_buffered_border_polygon(
                        kml=kml, 
                        images_in_neighboorhood=images_in_neighboorhood
                        )
                    for new_image in new_images:
                        images_in_kml.append(new_image)
                    k+=1
            # Visualise the images on the kml polygon using matplotlib iff the
            # number of images found is greater than 0 
            if len(images_in_kml)>0:
                PreStitchProcessing.__visualise_images_in_polygon(
                    kml.kml_polygon,
                    points=[image.geo_loc_point for image in images_in_kml],
                    name=f"Images for {kml.name}",
                    timeout=2
                )
                AppLogger.info(
                    f"PreStitchProcessing, Totally Found {len(images_in_kml)} for {kml}")
                AppLogger.info("")
                grouped_image_list.append(
                    {
                        "name": kml.name,
                        "images": images_in_kml,
                        "type": image_type
                    }
                    )
            else:
                AppLogger.warn(
                    f"PreStitchProcessing.__sort_images_from_kmls," 
                    f" Did not find images for {kml}")
        # Visualise all the images on all the KMLs.
        AppLogger.info(f"{len(images)}")
        PreStitchProcessing.__visualise_images_in_polygon(
            polygon=[kml.kml_polygon for kml in kmls],
            points=[image_.geo_loc_point for image_ in images],
            name="All Images in all the plots",
            timeout=60
        )

        return grouped_image_list
    

    @staticmethod
    def __transfer_images(images_dict_list:list[dict], 
                          output_dir:str|None=None):
        """
        Later change to a different library for faster copying speed.
        """
        copied_images_list = list()
        if output_dir is None:
            output_dir = Paths.output_dir()

        for image_dict in images_dict_list:
            plot_name = image_dict["name"]
            images = image_dict["images"]
            type_ = image_dict["type"]
            
            image_dir = os.path.join(output_dir, type_, plot_name)
            os.makedirs(image_dir, exist_ok=True)
            AppLogger.info(f"PreStitchProcessing, saving images to for plot {plot_name} to {image_dir}")
            for image in images:
                image:RawMSImage|RawRGBImage
                copied_image_path = os.path.join(image_dir, os.path.basename(image.path))
                
                try:
                    image.copy(dst=image_dir)
                    if type_ == PreStitchProcessing.ImageType.MS:
                        AppLogger.info(f"PreStitchProcessing, Copied {image.path[0:-6]} -> {copied_image_path[0:-6]}")
                    else:
                        AppLogger.info(f"PreStitchProcessing, Copied {image.path} -> {copied_image_path}")

                
                except Exception as e:
                    AppLogger.warn(
                        f"PreStitchProcessing, failed to copy image {image.path} "
                        f"with exception : {e.__class__.__qualname__}: {e}"
                        )
                    
            copied_images_list.append(
                {
                    "plot_name": plot_name,
                    "images_path": image_dir,
                }
                )
        
        return copied_images_list

        
    @staticmethod
    def __visualise_images_in_polygon(polygon:Polygon|list[Polygon], 
                                      points:list[Point],
                                      timeout:int=5, 
                                      name:str|None=None):
        """
        """
        AppLogger.info(f"PreStitchProcessing, Plotting '{name}' with timeout: {timeout}s")
        
        try:
            # If the input is a list of polygons
            if polygon.__class__.__qualname__ == 'list':
                if len(polygon)>1:
                    fig, axs = plt.subplots()
                    timer = fig.canvas.new_timer(interval = timeout*1000) 
                    timer.add_callback(plt.close)
                    axs.set_aspect('equal', 'datalim')
                    # Plot the polygons
                    for geom in polygon:  
                        # AppLogger.info(f"{poly}. {points[0]}")  
                        xs, ys = geom.exterior.xy    
                        axs.fill(xs, ys,c='r', alpha=0.2, ec='none')
                    for point in points:
                        if point.x == 0 or point.y == 0:
                            continue
                        axs.scatter(point.x, point.y, c='blue') 
                    if name is not None:
                        plt.title(name)
                else:
                    polygon = polygon[0]
                    # AppLogger.info(f"{polygon}")  
                    
                    # If the input is a single Polygon
                    x, y = polygon.exterior.xy
                    fig = plt.figure()
                    timer = fig.canvas.new_timer(interval = timeout*1000) 
                    timer.add_callback(plt.close)
                    plt.fill(x, y, alpha=0.2)
                    for point in points:
                        plt.scatter(point.x, point.y, c='blue')

                    if name is not None:
                        plt.title(name)
            else:
                # If the input is a single Polygon
                x, y = polygon.exterior.xy
                # AppLogger.info(f"{polygon}")
                fig = plt.figure()
                timer = fig.canvas.new_timer(interval = timeout*1000) 
                timer.add_callback(plt.close)
                plt.fill(x, y, alpha=0.2)
                for point in points:
                    plt.scatter(point.x, point.y, c='blue')

                if name is not None:
                    plt.title(name)

            mng = plt.get_current_fig_manager()
            mng.window.state('zoomed') 
        
            timer.start()
            plt.show()
            # AppLogger.info("PreStitchProcessing, closed plot.")
        
        except Exception as e:
            AppLogger.warn(f"Failed to plot with exception : {e.__class__.__qualname__}: {e}")


    @staticmethod
    def sort_images_by_kml(input_dir:str, 
                           output_dir:str|None=None,
                           transfer:bool=True, 
                           extra_image_search_iteration:int=1):
        """
        """
        
        try:
            AppLogger.info(f"PreStitchProcessing, Reading images from dir: {input_dir}")
            # Get the images whose geo locations lie inside the KMLs stored in ./resources/kmls/
            images_dict = PreStitchProcessing.__sort_images_from_kmls(
                path_to_images=input_dir,
                extra_image_search_iteration=extra_image_search_iteration)
            
            # Transfer images if the transfer is True (By default it is).
            if transfer:
                return PreStitchProcessing.__transfer_images(
                    images_dict_list=images_dict,
                    output_dir=output_dir
                    )
            
        except Exception as e:
            AppLogger.warn(f"PreStitchProcessing, Failed with exception : {e.__class__.__qualname__}: {e}")

        

if __name__ == "__main__":
    path = r"C:\Users\sahas\OneDrive\Desktop\Comp\000"
    path = r"C:\Users\Admin\Downloads\13_geotagged)\geotagged_images"
    # path = r"D:\data\11-Feb-2024_120meter_12ac_MS\Zoho WorkDrive (4)"
    # print(list(map(os.path.join, ["C:", "D:", "E:"], ["a", "b", "c"])))
    # Idea: Calculate the direction of the movement of the drone and then 
    # based on that find the images that that will be required to stitch the
    # image
    # PreStitchProcessing.sort_images_by_kml(path, r"D:\test")
    PreStitchProcessing.sort_images_by_kml(input_dir=path, output_dir=r"D:\test", transfer=False, extra_image_search_iteration=0)
    # path = os.getcwd()
    
