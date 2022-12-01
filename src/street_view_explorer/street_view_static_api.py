import os
import requests
from dotenv import load_dotenv
from coordinate import Coordinate

load_dotenv()


class StreetViewStaticApi:
    def __init__(self):
        self.endpoint = 'https://maps.googleapis.com/maps/api/streetview'

        if (os.getenv('API_KEY') is None):
            raise Exception('Missing API_KEY environment variable. Please set it in your .env file.')

        self.api_key = os.getenv('API_KEY')

    def hasImage(self, coord: Coordinate, radius_m: int) -> tuple((bool, Coordinate)):
        """
        Check if the location has an image.

        :param `coord`: Coordinate.
        :param `radius_m`: Radius (in meters) to search for an image.
        :return: Tuple containing a boolean indicating if an image was found and the coordinate.
        """
        response = requests.get(
            f'{self.endpoint}/metadata',
            params={
                'location': f'{coord.lat},{coord.lon}',
                'key': self.api_key,
                'radius': radius_m,
            }
        ).json()

        image_found = response['status'] == 'OK'

        if 'location' in response:
            lat = response['location']['lat']
            lon = response['location']['lng']
            coord = Coordinate(lat, lon)

        return image_found, coord

    def getImage(self, coord: Coordinate, size: str, heading=0, pitch=0, fov=90) -> bytes:
        """
        Get an image from Google Street View Static API.

        :param `coord`: Coordinate.
        :param `size`: Image size.
        :param `heading`: Heading, defaults to 0.
        :param `pitch`: Pitch, defaults to 0.
        :param `fov`: Field of view, defaults to 90.
        :return: Image in bytes.
        """

        response = requests.get(
            self.endpoint,
            params={
                'location': f'{coord.lat},{coord.lon}',
                'size': size,
                'heading': heading,
                'pitch': pitch,
                'fov': fov,
                'key': self.api_key,
            }
        )

        return response.content
