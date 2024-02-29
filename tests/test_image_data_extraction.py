from exif import Image
# from gmplot import gmplot
# from geopy.geocoders import Nominatim
import webbrowser
import os

def decimal_coords(coords, ref):
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == 'S' or ref == 'W':
        decimal_degrees = -decimal_degrees
    return decimal_degrees

input = r'C:\Users\USER\Desktop\GA_WORK\ML\BAYER\codes\ai-processor\IMG_0200_1.tif'
# input = f'{filename}.jpg'
# output = f'{filename}-location.html'

with open(input, 'rb') as src:
    img = Image(src)

lat = decimal_coords(img.gps_latitude, img.gps_latitude_ref)
lon = decimal_coords(img.gps_longitude, img.gps_longitude_ref)

print(lat, lon)

# gmap = gmplot.GoogleMapPlotter(lat, lon, 12)
# gmap.marker(lat, lon, 'red')
# gmap.draw(output)

# address = Nominatim(user_agent='GetLoc')
# location = address.reverse(f'{lat}, {lon}')

# print(location.address)

# webbrowser.open(f'file:///{os.getcwd()}/{output}', new=1)