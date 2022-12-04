import sys
import os
import random
from io import BytesIO
from timeit import default_timer as timer
import geopandas as gpd
from PIL import Image
from street_view_randomizer.countries import countries_codes
from street_view_randomizer.street_view_static_api import StreetViewStaticApi
from street_view_randomizer.coordinate import Coordinate
from street_view_randomizer.arg_parser import ArgParser


def run(args):
    global API
    API = StreetViewStaticApi(args.api_key)

    gdf = gpd.read_file("TM_WORLD_BORDERS-0.3/TM_WORLD_BORDERS-0.3.shp")

    if args.list_countries:
        available_countries_gdf = gdf.query(f'ISO3 in {countries_codes["iso3"]}').reset_index()
        available_countries_gdf.index += 1
        print("Available countries:\n")
        print(available_countries_gdf[["ISO3", "NAME"]].to_string())
        return

    for country in args.countries:
        if country.upper() not in countries_codes["iso3"]:
            print(f'Bad country ISO3 code: "{country}"')
            print("Run with option -l to list all available countries")
            return

    gdf = gdf.query(f"ISO3 in {args.countries}")
    gdf = gdf.assign(IMAGES=0)

    if args.use_area:
        print("--use-area option is enabled, countries with bigger areas are more likely to be selected")
        gdf = compute_area(gdf)

    total_images_per_country = len(args.headings) * len(args.pitches) * len(args.fovs)
    total_attempts = 0
    total_elapsed_time_ms = 0

    for i in range(args.samples):
        print(f"\n{'-' * 40} Sampling {i + 1}/{args.samples} {'-' * 40}\n")

        coord, country_df, attempts, elapsed_time_ms = find_available_image(gdf, args.radius)
        total_attempts += attempts
        total_elapsed_time_ms += elapsed_time_ms

        country_iso3 = country_df["ISO3"].values[0]
        country_name = country_df["NAME"].values[0]
        gdf.loc[gdf["ISO3"] == country_iso3, "IMAGES"] += total_images_per_country

        print(
            f"\n> Image found in {country_iso3} ({country_name}) | lon: {coord.lon}, lat: {coord.lat} | attempts: {attempts} | total elapsed time: {elapsed_time_ms / 1000:.2f}s"
        )

        total_elapsed_time_ms += save_images(
            country_iso3, coord, args.output_dir, args.size, args.headings, args.pitches, args.fovs
        )

    if args.samples > 1:
        print(f"\n{'-' * 40} Summary {'-' * 40}\n")

        picked_countries_df = gdf.query("IMAGES > 0")
        picked_countries_df = picked_countries_df[["ISO3", "NAME", "IMAGES"]]
        picked_countries_df = picked_countries_df.sort_values(by="IMAGES", ascending=False).reset_index()
        picked_countries_df = picked_countries_df.eval("IMAGES_PERCENTAGE = (IMAGES / IMAGES.sum()) * 100.0")
        picked_countries_df.index += 1
        picked_countries_df.loc["TOTAL"] = picked_countries_df[["IMAGES", "IMAGES_PERCENTAGE"]].sum()

        print(
            picked_countries_df.to_string(
                columns=["ISO3", "NAME", "IMAGES", "IMAGES_PERCENTAGE"],
                header=["ISO3", "NAME", "IMAGES", "%"],
                show_dimensions=False,
                col_space=10,
                na_rep="",
                formatters={
                    "IMAGES": "{:n}".format,
                    "IMAGES_PERCENTAGE": "{:.2f}".format,
                },
            )
        )

        print(f"\nTotal attempts: {total_attempts}")
        print(f"Average number of attempts per sampling: {total_attempts / args.samples:.2f}")

        print(f"\nTotal elapsed time: {total_elapsed_time_ms / 1000:.2f}s")
        print(f"Average elapsed time per sampling: {(total_elapsed_time_ms / 1000) / args.samples:.2f}s")


def compute_area(gdf: gpd.GeoDataFrame):
    gdf = gdf.eval("AREA = geometry.to_crs('esri:54009').area")
    gdf = gdf.sort_values(by="AREA", ascending=False)

    # Antarctica is huge, but its Google Street View coverage is very small.
    # Thus, we reduce its area so as to avoid picking it too often.
    gdf.loc[gdf["ISO3"] == "ATA", "AREA"] = gdf["AREA"].min()

    gdf = gdf.eval("AREA_PERCENTAGE = AREA / AREA.sum()")
    gdf = gdf.sort_values(by="AREA_PERCENTAGE", ascending=False)
    gdf = gdf.reset_index(drop=True)

    return gdf


def find_available_image(gdf: gpd.GeoDataFrame, radius_m):
    coord = None
    country_df = None
    attempts = 0
    total_elapsed_time_ms = 0
    image_found = False

    while not image_found:
        start = timer()
        attempts += 1
        country_df = get_random_country(gdf)
        min_lon, min_lat, max_lon, max_lat = country_df.total_bounds
        random_lat = random.uniform(min_lat, max_lat)
        random_lon = random.uniform(min_lon, max_lon)
        coord = Coordinate(random_lat, random_lon)

        if coord.within(country_df.geometry.values[0]):
            image_found, coord = API.has_image(coord, radius_m)

        end = timer()
        elapsed_ms = (end - start) * 1000
        total_elapsed_time_ms += elapsed_ms

        print(
            f'Searched image in {country_df["ISO3"].values[0]} | lon: {random_lon:20} lat: {random_lat:20} | elapsed time: {elapsed_ms:8.2f}ms'
        )

        if image_found:
            break

    return (coord, country_df, attempts, total_elapsed_time_ms)


def get_random_country(gdf: gpd.GeoDataFrame):
    return gdf.sample(n=1, weights="AREA_PERCENTAGE" if "AREA_PERCENTAGE" in gdf.columns else None)


def save_images(iso3_code: str, coord: Coordinate, output_dir, size, headings, pitches, fovs):
    if output_dir.endswith("/"):
        output_dir = output_dir[:-1]

    output_dir += f"/{iso3_code.lower()}"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    count = 0
    total_images_per_country = len(headings) * len(pitches) * len(fovs)
    start = timer()

    for h in headings:
        for p in pitches:
            for f in fovs:
                count += 1
                img = API.get_image(coord, size, heading=h, pitch=p, fov=f)
                img = Image.open(BytesIO(img))
                img_path = f"{output_dir}/{coord.lon}_{coord.lat}_h{h}_p{p}_f{f}.jpg"
                print(f"\t({count}/{total_images_per_country})\tSaving to {img_path}...")
                img.save(img_path)

    end = timer()
    total_elapsed_time_ms = (end - start) * 1000

    return total_elapsed_time_ms


def main():
    try:
        args = ArgParser.parse_args()
        run(args)
    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
