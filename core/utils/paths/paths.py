import os

class Paths:
    """
    """

    @staticmethod
    def base_path():
        """
        """

        current_path = os.getcwd()
        
        while True:
            if 'ai-processor' == os.path.basename(current_path):
                if 'core' in os.listdir(current_path) and 'resources' in os.listdir(current_path):
                    return current_path
            else:
                current_path = os.path.dirname(current_path)

    @staticmethod
    def kmls_path():
        return os.path.join(Paths.base_path(), 'resources', 'kmls')

    @staticmethod
    def exiftool_path():
        return os.path.join(Paths.base_path(), 'resources', 'exiftool', 'exiftool.exe')

    @staticmethod
    def requirements_path():
        return os.path.join(Paths.base_path(), 'resources', 'requirements.txt')
    
    @staticmethod
    def gdal_wheel_path():
        return os.path.join(Paths.base_path(), 'resources', 'gdal-wheel', 'GDAL-3.8.2-cp312-cp312-win_amd64.whl')
    
    @staticmethod
    def output_path():
        return os.path.join(Paths.base_path(), 'outputs')


if __name__ == "__main__":
    print(Paths.kmls_path())
