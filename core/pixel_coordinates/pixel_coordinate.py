class PixelCoordinate:
    """
    Class describing a pixel on an image.

     ------
    ### Args
    - `x` - (Required) 
    - `y` - (Required)   

    """

    class NotPixelCoordinateError(ValueError): pass

    def __init__(self, x:int|float, y:int|float):
        """
        """

        self.__X = x
        self.__Y = y

    def __get_x(self):
        return self.__X
    X = property(fget=__get_x)

    def __get_y(self):
        return self.__Y
    Y = property(fget=__get_y)

    def __repr__(self) -> str:
        return f"PIXEL COORDINATE: {self.__X}, {self.__Y}"
    
    def __add__(self, other):
        if other.__class__.__qualname__ == self.__class__.__qualname__:
            x = self.X + other.X
            y = self.Y + other.Y
        else: 
            raise PixelCoordinate.NotPixelCoordinateError("Added value is not a PixelCoordinate")
        return PixelCoordinate(y=y, x=x)

    def __sub__(self, other):
        if other.__class__.__qualname__ == self.__class__.__qualname__:
            x = self.X - other.X
            y = self.Y - other.Y
        else: 
            raise PixelCoordinate.NotPixelCoordinateError("Subtracted value is not a PixelCoordinate")
        return PixelCoordinate(y=y, x=x)
    
if __name__ == '__main__':
    a = PixelCoordinate(y=0.4235, x=0.6354534)
    b = PixelCoordinate(y=0.94235, x=0.19354534)
    print(a-b)
    