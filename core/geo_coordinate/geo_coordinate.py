class GeoCoordinate:
    """
    Geo Coordinates describing a point on the earth in latitude, longitude and
    height.
    
    ------
    ### Args
    - `latitude` - (Required) 
    - `longitude` - (Required)   
    - `height` - (Optional)
    """

    def __init__(self, latitude: float, longitude: float, height:float=0.0):
        """
        """

        self.__lat = latitude
        self.__lon = longitude

    
    def __return_lat(self):
        return self.__lat
    LAT = property(fget=__return_lat)


    def __return_lon(self):
        return self.__lon
    LON = property(fget=__return_lon)
    

