import os
import random
import geopandas as gpd
from io import BytesIO
from PIL import Image
from street_view_static_api import StreetViewStaticApi
from coordinate import Coordinate
from countries import countries_codes
from timeit import default_timer as timer
from arg_parser import ArgParser


def main():
    gdf = gpd.read_file("TM_WORLD_BORDERS-0.3/TM_WORLD_BORDERS-0.3.shp")

    if args.list_countries:
        available_countries_gdf = gdf.query(f'ISO3 in {countries_codes["iso3"]}').reset_index()
        print('Available countries:\n')
        print(available_countries_gdf[['ISO3', 'NAME']].to_string(index_names=False))
        return

    for country in args.countries:
        if country.upper() not in countries_codes['iso3']:
            print(f'Bad country format: "{country}"')
            print('Run with option -l to list all available countries')
            return

    gdf = gdf.query(f"ISO3 in {args.countries}")

    if args.use_area:
        print('--use-area option is enabled, countries with bigger areas are more likely to be selected\n')
        gdf = compute_area(gdf)

    avg_attempts = 0
    avg_elapsed_time_ms = 0

    for i in range(args.samples):
        if i > 0:
            print(f'\n-------------------------------- Sampling {i + 1}/{args.samples} --------------------------------\n')

        coord, country, attempts, total_elapsed_time_ms = find_available_image(gdf)
        country_iso3 = country['ISO3'].values[0]
        country_name = country['NAME'].values[0]
        total_elapsed_seconds = total_elapsed_time_ms / 1000
        avg_attempts += attempts
        avg_elapsed_time_ms += total_elapsed_time_ms

        print(
            f'\n> Image found in {country_iso3} ({country_name}) | lon: {coord.lon}, lat: {coord.lat} | attempts: {attempts} | total elapsed time: {total_elapsed_seconds:.2f}s'
        )

        save_image(country_iso3, coord)

    if args.samples > 1:
        print(f'\n-------------------------------- Summary --------------------------------')
        print(f'Average number of attempts: {avg_attempts / args.samples:.2f}')
        print(f'Average elapsed time: {(avg_elapsed_time_ms / 1000) / args.samples:.2f}s')


def compute_area(gdf: gpd.GeoDataFrame):
    gdf = gdf.eval("AREA = geometry.to_crs('esri:54009').area")
    gdf = gdf.sort_values(by='AREA', ascending=False)

    # Antarctica is huge, but its Google Street View coverage is very small.
    # Thus, we reduce its area so as to avoid picking it too often.
    gdf.loc[gdf['ISO3'] == 'ATA', 'AREA'] = gdf['AREA'].min()

    gdf = gdf.eval('AREA_PERCENTAGE = AREA / AREA.sum()')
    gdf = gdf.sort_values(by='AREA_PERCENTAGE', ascending=False)
    gdf = gdf.reset_index(drop=True)

    return gdf


def find_available_image(gdf: gpd.GeoDataFrame):
    coord = None
    country = None
    attempts = 0
    total_elapsed_time_ms = 0
    image_found = False

    while not image_found:
        start = timer()
        attempts += 1
        country = get_random_country(gdf)
        min_lon, min_lat, max_lon, max_lat = country.total_bounds
        random_lat = random.uniform(min_lat, max_lat)
        random_lon = random.uniform(min_lon, max_lon)
        coord = Coordinate(random_lat, random_lon)

        if coord.within(country.geometry.values[0]):
            image_found, coord = api.hasImage(coord, args.radius)

        end = timer()
        elapsed_ms = (end - start) * 1000
        total_elapsed_time_ms += elapsed_ms

        print(
            f'Searched image in {country["ISO3"].values[0]} | lon: {random_lon:20} lat: {random_lat:20} | elapsed time: {elapsed_ms:8.2f}ms'
        )

        if image_found:
            break

    return (coord, country, attempts, total_elapsed_time_ms)


def get_random_country(gdf: gpd.GeoDataFrame):
    return gdf.sample(n=1, weights='AREA_PERCENTAGE' if 'AREA_PERCENTAGE' in gdf.columns else None)


def save_image(iso3_code: str, coord: Coordinate):
    dir = f'{args.output_dir}/{iso3_code.lower()}'

    if not os.path.exists(dir):
        os.makedirs(dir)

    headings = args.headings
    pitches = args.pitches
    fovs = args.fovs

    count = 0
    total = len(headings) * len(pitches) * len(fovs)

    for h in headings:
        for p in pitches:
            for f in fovs:
                count += 1
                img = api.getImage(coord, args.size, heading=h, pitch=p, fov=f)
                img = Image.open(BytesIO(img))
                img_name = f'{dir}/{coord.lon}_{coord.lat}_h{h}_p{p}_f{f}.jpg'
                print(f'\t({count}/{total})\tSaving {img_name}...')
                img.save(img_name)


if __name__ == '__main__':
    try:
        args = ArgParser.parse_args()
        api_key = args.api_key if args.api_key else os.environ.get('GOOGLE_MAPS_API_KEY')
        api = StreetViewStaticApi(api_key)
        main()
    except Exception as e:
        print(e)
        exit(1)