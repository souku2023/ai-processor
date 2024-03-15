import os
import sys
sys.path.append(os.getcwd())

from core.app_logger import AppLogger

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
            extra_image_search_iteration=1)
        
        os.makedirs(output_dir, exist_ok=True)
        
        if len(images_in_plots)<1:
            AppLogger.critical("Stitching, No images found in plot, check Geo Tagging")
            sys.exit()
        else:
            path = os.path.dirname(images_in_plots[0]["images_path"])
            # WebODM.create_projects_from_folder(path=path, 
            #                                    name=project_name, 
            #                                    description=None, 
            #                                    cleanup_local_images=True)

if __name__ == "__main__":
    day =      input("Enter Day: ")
    date =     input("Enter Date (eg: 12Feb24): ")
    img_type = input("Enter Image Type (RGB or MS): ")
    alt =      input("Enter Altitude (60, 80, 120): ")
    session =  input("Enter Session (Morning, Afternoon, Evening): ")
    speed = "10ms"
    
    name = f"DAY{day}_{date}_{img_type}_{alt}m_{session}"
    
    if speed is not None:
        name = name+"_"+speed
    else:
        name = name+"_5ms"
    
    input_dir = r"G:\BAYER\PHASE-2\VISIT-2\_13-3-24 MS 60m 10ms 41 ac\13-3-24 MS 60m 10ms 41 ac\0000SET\ALL"
    output_dir = r"G:\BAYER\poltwise_and_stitched_images\VISIT-2\day1\{}".format(name)
    
    
    Stitching.stitch_images_by_kml(input_dir=input_dir, output_dir=output_dir, project_name=name)
    
    # input_dir = r"H:\10-Feb-2024_Day_4_multispectral\60meter_12ac_5ms\all"
    # output_dir = r"G:\BAYER\plotwise_ms\day4\60"
    # Stitching.stitch_images_by_kml(input_dir=input_dir, output_dir=output_dir, project_name=name)