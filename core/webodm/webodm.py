import requests
import sys
import os
sys.path.append(os.getcwd())
import glob
import json 
import time
import datetime
from typing import TYPE_CHECKING

from core.utils.paths import Paths
from core.app_logger import AppLogger
from core.webodm.webodm_project import WebODMProject
from core.webodm.status_codes_webodm import StatusCodes
from core.webodm.response_codes import ResponseCodes

if TYPE_CHECKING:
    from webodm_task import WebODMTask

class InvalidCredentialsError(Exception):pass

class WebODM:
    """
    A convenience class for the WebODM API.
    """

    class NoImageDirectoriesFoundError(Exception):pass

    token = None
    __username = None
    __password = None
    __token_gen_time = None
    port = 8000

    initialised = False


    @staticmethod
    def __get_credentials():
        """
        """

        with open(Paths.webodm_credentials()) as credentials_file:
            credentials = json.load(credentials_file)

        return credentials

    
    @staticmethod
    def __token_exists():
        """
        """
        if WebODM.token is not None:
            return True
        else:
            return False
    
    
    @staticmethod
    def __get_token():
        """
        """
        # print(WebODM.__password)
        if not WebODM.__token_exists():
            res = requests.post('http://localhost:8000/api/token-auth/', 
                        data={
                            'username': WebODM.__username,
                            'password': WebODM.__password
                            }).json()
            
            
            
            WebODM.__token_gen_time = time.time()
            # AppLogger.info(f"WebODM, {json.dumps(res)}")
            if 'token' in res:
                WebODM.token = res['token']
                AppLogger.info(f"WebODM, Logged in with username: {WebODM.__username}!")
                AppLogger.info(f"{WebODM.token}")
                
            else:
                raise InvalidCredentialsError("Invalid Credentials.")

            
    @staticmethod
    def __project_create(name:str, description:str|None=None):
        """
        Creates a Project in WebODM and returns a WebODMProject object.
        """
        WebODM.__initialise()

        data_dict = {
            'name': name,
        }

        if description is not None:
            data_dict['description'] = description

        res = requests.post('http://localhost:8000/api/projects/', 
                        headers={'Authorization': 'JWT {}'.format(WebODM.token)},
                        data={'name': name}).json()
        
        if 'id' in res:
            AppLogger.info("WebODM, Created project: {}".format(res)) 
            project_id = res['id']
            return WebODMProject(id=project_id, token=WebODM.token, name=name)
        else:
            AppLogger.warn(f"WebODM, Unable to create project : {json.dumps(res)}")
            return None
        

    @staticmethod
    def __initialise():
        """
        """
        # if WebODM.__token_gen_time is not None:
        #     token_time_elapsed = time.time() - WebODM.__token_gen_time
        # else:
        #     token_time_elapsed=0

        if  (WebODM.initialised is False):
            # Get username and password from resources
            credentials = WebODM.__get_credentials()
            WebODM.__username = credentials["username"]
            WebODM.__password = credentials["password"]

            # Get token
            AppLogger.info("WebODM, Getting token...")
            WebODM.__get_token()

    def create_projects_from_folder(path:str, name:str, description:str|None=None, cleanup_local_images:bool=False):
        """
        """

        files_ = os.listdir(path)

        # Check if the path has enough folders
        if len(files_)<1:
            raise WebODM.NoImageDirectoriesFoundError(f"{len(files_)} directories found in path")

        files = list()
        for file in files_:
            files.append(os.path.join(path, file))

        project = WebODM.__project_create(name=name, description=description)
        tasks = list()
        for file in files:
            task_name = f"{name}_{os.path.basename(file)}"
            task_ = project.add_task(file, name=task_name)
            tasks.append(task_)
            AppLogger.info(f"WebODM, Created Task: {task_}")
            
        for task in tasks:
            if task is not None:
                AppLogger.info(f"WebODM, Starting {task}...")
                task:'WebODMTask'
                task.add_option(task.Options.FAST_ORTHOPHOTO, True)
                task.add_option(task.Options.ORTHOPHOTO_CUTLINE, True)
                task.add_option(task.Options.MIN_NUM_FEATURES, 12500)
                task.start()
                task.wait_complete()
                task.download_orthophoto()
                if cleanup_local_images:
                    AppLogger.info("WebODM, Cleaning up local images...")
                    task.cleanup_local_images()
                
            

        
        
        

if __name__ == '__main__':
    # proj = WebODM.project_create("Convenience func test")
    # token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoyLCJlbWFpbCI6IiIsInVzZXJuYW1lIjoicHl0b3JjaG9iaiIsImV4cCI6MTcwOTQ2NjI4OX0.cx0kDs83oNPh8lRlklluba7HyqbjI7pYqqtm1qws1lc"
    images_dir = r"D:\test\RGB"
    WebODM.create_projects_from_folder(path=images_dir, name="DEUS_EX_MACHINA")