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

    class NotGeoCoordinateError(ValueError): pass
    

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


    def __repr__(self) -> str:
        return f"GEO COORDINATE: LAT: {self.__lat}, LON: {self.__lon}"
    
    def __add__(self, other):
        if other.__class__.__qualname__ == self.__class__.__qualname__:
            longitude = self.LAT + other.LAT
            latitude = self.LON + other.LON
        else: 
            raise GeoCoordinate.NotGeoCoordinateError("Added value is not a Geocoordinate")
        return (longitude, latitude)

    def __sub__(self, other):
        if other.__class__.__qualname__ == self.__class__.__qualname__:
            longitude = self.LAT - other.LAT
            latitude = self.LON - other.LON
        else: 
            raise GeoCoordinate.NotGeoCoordinateError("Subtracted value is not a Geocoordinate")
        return (longitude, latitude)


if __name__ == '__main__':
    a = GeoCoordinate(latitude=0.4235, longitude=0.6354534)
    b = GeoCoordinate(latitude=0.94235, longitude=0.19354534)
    print(a+b)
    

