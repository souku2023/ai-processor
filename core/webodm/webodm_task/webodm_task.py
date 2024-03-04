import requests
import datetime
import time
import glob
import json
import os
from core.webodm.response_codes import ResponseCodes
from core.webodm.status_codes_webodm import StatusCodes
from typing import Any


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from webodm_project import WebODMProject

from core.app_logger import AppLogger

class WebODMTask:
    """
    """

    class ImageDirNorFoundError(Exception):pass

    class Options:
        MIN_NUM_FEATURES = "min-num-features"
        RADIOMETRIC_CALIBRATION = "radiometric-calibration"
        ORTHOPHOTO_CUTLINE = "orthophoto-cutline"
        ORTHOPHOTO_RESOLUTION = "orthophoto-resolution"
        FAST_ORTHOPHOTO = "fast-orthophoto"
        CROP = "crop"
        OPTIMISE_DISK_SPACE = "optimize-disk-space"

    # class 

    def __init__(self, 
                 project_id:int, 
                 images_dir:str, 
                 project_reference: 'WebODMProject',
                 name:str|None=None,
                 data_dict:dict|None=None,
                 options:list[dict]|None=None) -> None:
        """
        """

        self.__project_id = project_id
        self.__images_dir = images_dir
        self.__project_reference = project_reference
        self.__token = project_reference.TOKEN
        self.__options = options
        self.__name = name
        self.__data_dict = data_dict

        # Set Task Options 
        if self.__options is None:
            self.__options = [
                {
                    'name': "orthophoto-resolution", 
                    'value': 1
                    },
            ]
        
        # Add more options
        self.add_option(self.Options.FAST_ORTHOPHOTO, True)
        self.add_option(self.Options.ORTHOPHOTO_CUTLINE, True)
        self.add_option(self.Options.MIN_NUM_FEATURES, 12500)
        # self.add_option(self.Options.CROP, 10)

        # Set Details of task
        if self.__data_dict is None:
            self.__data_dict = { 
                'name': self.__name,
                'auto_processing_node': True,
                # 'resize_to': 2048,
                'options': json.dumps(self.__options)
                }
        
        AppLogger.info(f"WebODMTask, Created Task for {project_reference.NAME}")
        # try:
        #     self.__initialise()
        # except Exception as e:
        #     AppLogger.warn(f"WebODMTask, Failed to initialise task with Exception : {e}")


    def add_option(self, name:str, value):
        """
        """

        self.__options.append(
            {
                "name": name,
                "value": value
                }
            )
        return {
            'name': name,
            'value': value
        }
        

    def start(self, data_dict:dict|None=None)->dict|None:
        """
        """
        AppLogger.info(f"WebODMTask, Starting task under project :{self.__project_reference.NAME}")
        types = ("*.jpg", "*.jpeg", "*.JPG", "*.JPEG", "*.tif", "*.TIF", "*.png", "*.PNG")
        images_list = []
        try:
            if os.path.exists(self.__images_dir):
                for t in types:
                    images_list.extend(glob.glob(os.path.join(self.__images_dir, t)))

                AppLogger.info(f"WebODMTask, Found {len(os.listdir(self.__images_dir))} images in {self.__images_dir}")
                
                # Set name to default one if not set
                if self.__name is None:
                    self.__name = f"Test_Task_{self.__images_dir.replace("\\", "-").replace(":", "")}"
                
                # Get a list of images to be stitched
                images = [('images', (os.path.basename(file), open(file, 'rb'), 'image/jpg')) for file in images_list]
                
                # Post request
                req_url = 'http://localhost:8000/api/projects/{}/tasks/'.format(self.__project_reference.ID)
                auth_header = {'Authorization': 'JWT {}'.format(self.__token)}
                res = requests.post(req_url, 
                                    headers=auth_header,
                                    files=images,
                                    data=self.__data_dict).json()
                
                self.__id = res["id"]
                
                AppLogger.info(f"WebODMTask:{self.__name}@{self.__project_reference.NAME}, Created.")
                return res
            else:
                AppLogger.info(f"WebODMTask:{self.__project_reference.NAME}, Image dir not found.")
        
        except Exception as e:
            AppLogger.warn(f"WebODMTask, Failed to create task, {e.__class__.__qualname__}: {e}")

    
    def wait_complete(self, print_status_logs:bool=True)->bool|None:
        """
        """
        while True:
            status = self.get_status() 
            
            if status[0] == StatusCodes.COMPLETED:
                AppLogger.info(f"WebODMTask:{self.__name}@{self.__project_id}: Completed")
                return True
            
            elif status[0] == StatusCodes.FAILED:
                AppLogger.info(f"WebODMTask:{self.__name}@{self.__project_id}: Failed")
                return False
            
            elif status[0] == StatusCodes.CANCELED:
                AppLogger.info(f"WebODMTask:{self.__name}@{self.__project_id}: Cancelled")
                return False
            
            elif status[0] == StatusCodes.NOT_STARTED:
                return None
            
            else:
                if print_status_logs:
                    seconds = status[1]['processing_time'] / 1000
                    if seconds < 0: 
                        seconds = 0
                    m, s = divmod(seconds, 60)
                    h, m = divmod(m, 60)
                    if h<10:
                        h=f"0{int(round(h))}"
                    else:
                        h=f"{int(round(h))}"
                    if m<10:
                        m=f"0{int(round(m))}"
                    else:
                        m=f"{int(round(m))}"
                    if s<10:
                        s=f"0{int(round(s))}"
                    else:
                        s=f"{int(round(s))}"
                    time_str = f"{h}:{m}:{s}"
                    AppLogger.info(
                        f"WebODMTask:{self.__name}@{self.__project_reference.NAME}"
                        f"[{self.__project_id}], Task Running for {time_str}"
                        )
                time.sleep(5)


    def delete(self):
        """
        """


    def get_status(self)->tuple[int, Any]:
        """
        """
        if not hasattr(self, '_WebODMTask__id'):
            return StatusCodes.NOT_STARTED, False
        else:
            
            try:
                request_url = 'http://localhost:8000/api/projects/{}/tasks/{}'.format(self.__project_id, self.__id)
                res = requests.get(request_url, 
                                   headers={'Authorization': 'JWT {}'.format(self.__token)}).json()
                return (res['status'], res)
            except Exception as e:
                AppLogger.warn(
                    f"WebODMTask:{self.__name}@{self.__project_reference.NAME}, "
                    f"Unable to get status with excpetion: {e}")
                return (0, False)


    def download_assets(self):
        """
        """


    def download_orthophoto(self, path:str|None=None):
        """
        """
        status, res_ = self.get_status()
        if status == StatusCodes.COMPLETED:
            if path is None:
                path = os.path.join(self.__images_dir, self.__name) 
            AppLogger.info(f"WebODMTask:{self.__name}@{self.__project_reference.NAME}, Downloading Orthophoto to {path}")
            try:
                # Configure url and token
                r = "http://localhost:8000/api/projects/{}/tasks/{}/download/orthophoto.tif".format(self.__project_id, self.__id)
                headers = {'Authorization': 'JWT {}'.format(self.__token)}
                
                # Get the Orthophoto
                res = requests.get(r, headers=headers, stream=True)
                
                # Write to orthophoto_path
                orthophoto_path = os.path.join(path, f"{self.__name}-orthophoto.tif")

                os.makedirs(path)

                with open(orthophoto_path, 'wb') as f:
                    for chunk in res.iter_content(chunk_size=1024): 
                        if chunk:
                            f.write(chunk)
            
            except Exception as e:
                AppLogger.warn(f"WebODMTask, Cannot Download Orthophoto: {e.__class__.__qualname__}: {e}")
        else:
            AppLogger.warn("WebODMTask, Cannot Download Orthophoto: Task not completed.")
            


    def wait_upload(self):
        """
        """
        status = self.get_status()


    def __repr__(self) -> str:
        return f"{self.__name}@{self.__project_reference.NAME}"
        


