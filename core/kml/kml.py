import os
import sys
sys.path.append(os.getcwd())
import xml.etree.ElementTree as ET
from shapely.geometry import Polygon
from core.app_logger import AppLogger


class KML:
    """
    A class to extract data from a KML file.

    Will later make it more inclusive instead of just for Farmer.
    """

    def __init__(self, path:str):
        """
        """
        self.path = path
        self.name = os.path.basename(path).split('.')[0]
        AppLogger.info(f"KML, Reading KML {self.name}")
        self.coordinates_string = None
        self.kml_data_dict = self.__extract_data_from_kml()
        self.kml_polygon = self.__return_shapely_polygon()


    def __extract_data_from_kml(self) -> list|None:
        try:
            namespace = {"ns0": "http://www.opengis.net/kml/2.2"}
            kml_file_obj = open(self.path)
            tree = ET.parse(kml_file_obj)
            root = tree.getroot()

            placemarks = root.findall(".//ns0:Placemark", namespaces=namespace)
            kml_datas = []

            for placemark in placemarks:
                farmer_id_elem = placemark.find(".//ns0:SimpleData[@name='FarmId']", namespaces=namespace)
                if farmer_id_elem is not None:
                    self.farm_id = farmer_id_elem.text
                    AppLogger.info(f"KML, Farm ID: {self.farm_id}")
                
                farmer_code_elem = placemark.find(".//ns0:SimpleData[@name='FarmerCode']", namespaces=namespace)
                if farmer_code_elem is not None:
                    farmer_code = farmer_code_elem.text   
                    AppLogger.info(f"KML, Farmer code: {farmer_code}") 

                coordinates_elem = placemark.find(".//ns0:coordinates", namespaces=namespace)
                if coordinates_elem is not None:
                    coordinates = coordinates_elem.text    
                    # AppLogger.info(f"KML, Linear Ring Coords: {coordinates}")
                
                self.coordinates_string = coordinates
                kml_datas.append({
                    "FarmerID": self.farm_id,
                    "FarmerCode": farmer_code,
                    "Coordinates": [(float(coords.split(',')[0]), float(coords.split(',')[1])) for coords in str(coordinates).split(' ')]
                })
                self.list_of_geo_coordinates =  [(float(coords.split(',')[0]), float(coords.split(',')[1])) for coords in str(coordinates).split(' ')]
                # AppLogger.info(f"KML, COORDS{s}")

            return kml_datas
        except Exception as e:
            AppLogger.warn(f"KML, Unable to extract data from {self.path}")
            return None

    
    def __return_shapely_polygon(self) -> Polygon|None:
        """
        """
        
        try:
            poly = Polygon(self.list_of_geo_coordinates)
            AppLogger.info("KML, Successfully created KML Polygon")
            return poly
        except Exception as e:
            AppLogger.info("KML, Failed to create KML Polygon")

if __name__ == "__main__":
    kml_dir_path = os.path.join(os.getcwd(), 'resources', 'kmls')
    for kml_file in os.listdir(kml_dir_path):
        kml_path = os.path.join(kml_dir_path, kml_file)
        kml = KML(kml_path)
        