import datetime
import requests
from core.webodm.response_codes import ResponseCodes
from core.webodm.status_codes_webodm import StatusCodes
from core.webodm.webodm_task import WebODMTask

from core.app_logger import AppLogger

class WebODMProject:
    """
    """

    def __init__(self, id:int, token:str, name:str|None) -> None:
        """
        """

        self.__id = id
        self.__token = token
        if name is not None:
            self.__name = name
        try:
            self.__initialise()
        except Exception as e:
            AppLogger.warn(
                f"WebODMProject:{self.__name}, Failed to initialise Project with Exception : {e}")

    
    def __initialise(self):
        """
        """
        # project_dict = {'id': self.__id, 
        #  'tasks': [], 
        #  'owned': True, 
        #  'created_at': '2024-03-03T05:44:49.368145Z', 
        #  'permissions': ['add', 'change', 'delete', 'view'], 
        #  'tags': [], 
        #  'name': 'Convenience func test', 
        #  'description': ''
        #  }
        res = requests.get(f'http://localhost:8000/api/projects/{self.__id}', 
                           headers={'Authorization': 'JWT {}'.format(self.__token)}).json()
        
        self.project_dict = res

        if self.__name is None: 
            self.__name = res['name']
        self.__created_time = datetime.datetime.fromisoformat(res['created_at'])

        AppLogger.info(f"WebODMProject:{self.__name}, Initialised.")
    
    # Property: NAME
    def __return_name(self):
        return self.__name
    NAME=property(fget=__return_name)

    # Property: ID
    def __return_id(self):
        return self.__id
    ID=property(fget=__return_id)

    # Property: TOKEN
    def __return_token(self):
        return self.__token
    TOKEN=property(fget=__return_token)
        
    def add_task(self,
                 images_dir:str, 
                 name:str|None=None,
                 options:list[dict]|None=None)->WebODMTask|None:
        """
        """
        AppLogger.info(f"WebODMProject:{self.__name}, Creating Task...")
        try:
            return WebODMTask(project_id=self.__id, 
                              images_dir=images_dir, 
                              project_reference=self,
                              options=options,
                              name=name)
        except Exception as e:
            AppLogger.warn(f"WebODMProject:{self.__name}, Failed to create task with Exception : {e}")

if __name__ == "__main__":
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoyLCJlbWFpbCI6IiIsInVzZXJuYW1lIjoicHl0b3JjaG9iaiIsImV4cCI6MTcwOTQ2NjI4OX0.cx0kDs83oNPh8lRlklluba7HyqbjI7pYqqtm1qws1lc"
    WebODMProject()