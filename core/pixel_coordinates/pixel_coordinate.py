class PixelCoordinate:
    """
    Class describing a pixel on an image.

     ------
    ### Args
    - `x` - (Required) 
    - `y` - (Required)   

    """

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