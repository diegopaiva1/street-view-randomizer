import re
import argparse
from street_view_randomizer.countries import countries_codes


class IntRangeType(object):
    def __init__(self, start, stop):
        self.start, self.stop = start, stop

    def __call__(self, value):
        value = int(value)

        if value < self.start or value >= self.stop:
            raise argparse.ArgumentTypeError(f"value outside of range [{self.start}-{self.stop}]")

        return value


class RegexpType(object):
    def __init__(self, regexp):
        self.regexp = regexp

    def __call__(self, value):
        if not re.match(self.regexp, value):
            raise argparse.ArgumentTypeError(f"invalid value {value}")

        return value


class ArgParser:
    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser()

        max_free_api_calls = 28_000
        max_radius_m = 1_000_000

        parser.add_argument("-k", "--api-key", help="Google Street View Static API key", type=str)

        parser.add_argument(
            "-c",
            "--countries",
            help="List of countries (ISO3 codes) to search images for, defaults to all countries available.",
            nargs="+",
            type=str,
            default=countries_codes["iso3"],
        )

        parser.add_argument(
            "-r",
            "--radius",
            help="Radius in meters to search for images, defaults to 5.000 (5km).",
            type=IntRangeType(1, max_radius_m),
            default=5000,
        )

        parser.add_argument(
            "-l",
            "--list-countries",
            help="List all available countries.",
            action="store_true",
        )

        parser.add_argument(
            "-a",
            "--use-area",
            help="When this option is enabled, countries with bigger areas will have more chances of being selected.",
            action="store_true",
        )

        parser.add_argument(
            "-n",
            "--samples",
            help="Number of samples to get, defaults to 1.",
            type=IntRangeType(1, max_free_api_calls),
            default=1,
        )

        parser.add_argument(
            "-o",
            "--output-dir",
            help="Directory to save images to, defaults to images/ under the directory where the script is executed. If the directory does not exist, the script will try to create it.",
            type=str,
            default="./images/",
        )

        parser.add_argument(
            "-H", "--headings", help="List of headings, defaults to [0].", nargs="+", type=int, default=[0]
        )

        parser.add_argument(
            "-P", "--pitches", help="List of pitches, defaults to [0].", nargs="+", type=int, default=[0]
        )

        parser.add_argument(
            "-F",
            "--fovs",
            help="List of fovs, defaults to [90].",
            nargs="+",
            type=int,
            default=[90],
        )

        parser.add_argument(
            "-S",
            "--size",
            help="Image size in pixels, defaults to 640x640 (max allowed by Google). At least a hundred pixels in each dimension is required.",
            type=RegexpType(r"^[1-9]\d\dx[1-9]\d\d$"),
            default="640x640",
        )

        return parser.parse_args()
