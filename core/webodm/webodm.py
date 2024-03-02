import requests
import sys
import os
import glob
import json 
import time
import datetime

from core.utils.paths import Paths
from core.app_logger import AppLogger

class InvalidCredentialsError(Exception):pass

class WebODM:
    """
    A convenience class for the WebODM API.
    """

    class StatusCodes:
        QUEUED = 10
        RUNNING = 20
        FAILED = 30
        COMPLETED = 40
        CANCELED = 50

    class Options:
        MIN_NUM_FEATURES = "min-num-features"

    token = None
    username = None
    password = None
    token_gen_time = None
    port = 8000

    initialised = False


    @staticmethod
    def __get_credentials():
        """
        """

        with open(Paths.webodm_credentials) as credentials_file:
            credentials = json.load(credentials_file)

        return credentials

    
    @staticmethod
    def __check_token():
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
        if WebODM.__check_token() is None:
            res = requests.post('http://localhost:8000/api/token-auth/', 
                        data={
                            'username': WebODM.username,
                            'password': WebODM.password
                            }).json()
            
            if 'token' in res:
                print("Logged-in!")
                WebODM.token = res['token']
                AppLogger.info("WebODM, Logged in.")
            else:
                raise InvalidCredentialsError("Invalid Credentials.")

            
    @staticmethod
    def create_project(name:str):
        """
        """
        WebODM.__get_token()
        res = requests.post('http://localhost:8000/api/projects/', 
                        headers={'Authorization': 'JWT {}'.format(WebODM.token)},
                        data={'name': name}).json()
        
        if 'id' in res:
            AppLogger.info("WebODM, Created project: {}".format(res)) 
            project_id = res['id']
            return project_id
        else:
            AppLogger.warn("WebODM, Unable to create project")
            return None
        

    @staticmethod
    def __initialise():
        """
        """
        # Get username and password from resources
        credentials = WebODM.__get_credentials()
        WebODM.username = credentials["username"]
        WebODM.password = credentials["password"]

        WebODM.__get_token()
        