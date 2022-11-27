import argparse
from countries import countries_codes

class IntRange(object):
    def __init__(self, start, stop):
        self.start, self.stop = start, stop

    def __call__(self, value):
        value = int(value)

        if value < self.start or value >= self.stop:
            raise argparse.ArgumentTypeError(f'value outside of range [{self.start}-{self.stop}]')

        return value

class ArgParser():
    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser()
        max_free_api_calls = 28_000
        max_radius_m = 1_000_000

        parser.add_argument(
            '-c', '--countries',
            help='list of countries (ISO3 codes) to search images for, defaults to all countries available',
            nargs='+',
            type=str,
            default=countries_codes['iso3']
        )

        parser.add_argument(
            '-l', '--list-countries',
            help='list all available countries',
            action='store_true',
        )

        parser.add_argument(
            '-a', '--use-area',
            help='when this option is enabled, countries with bigger areas will have more chances of being selected',
            action='store_true',
        )

        parser.add_argument(
            '-n', '--iterations',
            help='number of iterations, defaults to 1',
            type=IntRange(1, max_free_api_calls),
            default=1,
        )

        parser.add_argument(
            '-H', '--headings',
            help='list of headings, defaults to [0]',
            nargs='+',
            type=int,
            default=[0]
        )

        parser.add_argument(
            '-P', '--pitches',
            help='list of pitches, defaults to [0]',
            nargs='+',
            type=int,
            default=[0]
        )

        parser.add_argument(
            '-F', '--fovs',
            help='list of fovs, defaults to [90]',
            nargs='+',
            type=int,
            default=[90],
        )

        parser.add_argument(
            '-R', '--radius',
            help='radius (in meters) to search for images, defaults to 5.000 (5km)',
            type=IntRange(1, max_radius_m),
            default=5000,
        )

        return parser.parse_args()
        