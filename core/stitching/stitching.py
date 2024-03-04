import os
import sys
sys.path.append(os.getcwd())

from core.webodm import WebODM
from core.pre_stitching import PreStitchProcessing

class Stitching:
    """
    """

    @staticmethod
    def stitch_images_by_kml(input_dir:str, output_dir:str, project_name:str):
        """
        """

        images_in_plots = PreStitchProcessing.sort_images_by_kml(
            input_dir=input_dir,
            output_dir=output_dir,
            extra_image_search_iteration=2)
        
        path = os.path.dirname(images_in_plots[0]["images_path"])
        
        WebODM.create_projects_from_folder(path=path, name=project_name)

if __name__ == "__main__":
    day = input("Enter Day: ")
    date = input("Enter Date (eg: 12Feb24): ")
    img_type = input("Enter Image Type (RGB or MS): ")
    alt = input("Enter Altitude (60, 80, 120): ")
    session = input("Enter Session (Morning, Afternoon, Evening): ")
    
    name = f"DAY{day}_{date}_{img_type}_{alt}m_{session}"
    
    input_dir = r"G:\BAYER\PHASE-2\VISIT-1\11-Feb-2024_Day_5_RGB_Images\11-Feb-2024_60meter_42ac_RGB\geotagged_images"
    output_dir = r"G:\BAYER\poltwise_and_stitched_images\day5\60"
    Stitching.stitch_images_by_kml(input_dir=input_dir, output_dir=output_dir, project_name=name)
    
    # input_dir = r"H:\10-Feb-2024_Day_4_multispectral\60meter_12ac_5ms\all"
    # output_dir = r"G:\BAYER\plotwise_ms\day4\60"
    # Stitching.stitch_images_by_kml(input_dir=input_dir, output_dir=output_dir, project_name=name)