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
            extra_image_search_iteration=0)
        
        path = os.path.dirname(images_in_plots[0]["images_path"])
        
        WebODM.create_projects_from_folder(path=path, name=project_name)

if __name__ == "__main__":
    input_dir = r"D:\12-Feb-2024_Day_6_RGB_Images\geotagged_images"
    output_dir = r"D:\test"
    Stitching.stitch_images_by_kml(input_dir=input_dir, output_dir=output_dir, project_name="DAY_X")