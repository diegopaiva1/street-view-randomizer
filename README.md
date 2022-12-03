# Street View Randomizer

![GitHub](https://img.shields.io/github/license/diegopaiva1/street-view-randomizer)
![GitHub repo size](https://img.shields.io/github/repo-size/diegopaiva1/street-view-randomizer)

A Python command-line interface designed to generate random images from [Google Street View](http://maps.google.com).

Generate random Google Street View images from all around the world.

## Requirements

- Python >= 3.6
- [Google Maps Platform](https://developers.google.com/maps) API key

## Install

```
pip install street-view-randomizer
```

## Usage

The basic usage defaults to generating a single image anywhere in the world (equal probabilities with respect to countries sizes):

```
street-view-randomizer --api-key=yourapikeyhere
```

The output will be something like:

```
Searched image in PRI | lon:   -65.99685876172165 lat:    18.08766139664086 | elapsed time:   399.14ms

> Image found in PRI (Puerto Rico) | lon: -66.0217481, lat: 18.1029857 | attempts: 1 | total elapsed time: 0.40s
	(1/1)	Saving to ./images/pri/-66.0217481_18.1029857_h0_p0_f90.jpg...
```

### API key

The script will fallback to the [Google Maps Platform](https://developers.google.com/maps) API key in the `GOOGLE_MAPS_API_KEY` environment variable if the `--api-key` argument is not provided. You can set it in your `.bashrc` or `.zshrc` file:

```
export GOOGLE_MAPS_API_KEY=yourapikeyhere
```

### General options

Here is a list of some useful flags one may pass to customize the behavior of the script.

#### `-k, --api-key`

[Google Maps Platform](https://developers.google.com/maps) API key.

#### `-c, --countries`

Use the `-c` argument together with a list of one or more [ISO3 country codes](https://www.iban.com/country-codes) to narrow the search. For instance, if we are interested in fetching an image from either Brazil, Argentina or Chile:

```
street-view-randomizer -c BRA ARG CHL
```

#### `-l, --list-countries`

Display a list of all available countries (those with some Google Street View Coverage).

#### `-r, --radius`

Defines a radius in meters centered on a latitude and longitude. The default value is 5.000 (5km). This value should only be increased if searching for an image is taking too long.

#### `-a, --use-area`

If the size of the country matters when sampling from a group of countries, passing in the `-a` flag will give bigger countries more chances of being drawn. The following chart shows the odds for each country if we consider the full space search:

![areas_percentage](https://user-images.githubusercontent.com/32985519/204120495-179ce98a-7544-4cd8-a22c-e10ccab81fed.png)

#### `-n, --samples`

To **sample** more than once (this doesn't mean fetching more than one image per country), pass in the `-n` flag with some desired number, e.g.:

```
street-view-randomizer -n 3
```

Note that the maximum number of iterations allowed is **28.000**, which happens to be the maximum number of requests per month one can make without being charged by the Google Maps Platform. Be careful!

#### `-o, --output-dir`

By default all images are saved under the `images` directory from where the script is executed. To change the output directory, pass in the `-o` flag with the desired path, e.g.:

```
street-view-randomizer -o /home/user/images
```

### Image options

Images will be saved to a directory named after the country code (ISO3) where the following naming convention applies:

```
<lon>_<lat>_h<heading>_p<pitch>_f<fov>.jpg
```

Please refer to the [Street View Static API documentation](https://developers.google.com/maps/documentation/streetview/request-streetview) to understand the meaning of `heading`, `pitch` and `fov`.

Anyway, you are allowed to pass a list of each one of these parameters to generate different imagery from the same coordinate.

#### `-H, --headings`

List of headings, e.g., `-H 0 90 180 270`. The default value is 0.

#### `-P, --pitches`

List of pitches, e.g., `-P -35 0 35`. The default value is 0.

#### `-F, --fovs`

List of fovs, e.g., `-F 60 90 120`. The default value is 90.

Note that the total number of images will be the product of the length of each list. For each heading, the algorithm will output an image for each pair of pitch and fov.

#### `-S, --size`

Size of the output image, defaults to 256x256. The maximum size allowed is 640x640. Each dimension must have at least a hundred pixels.

### Putting it all together

The following command will perform 3 weighted samplings of 12 images of size 512x512:

```
street-view-randomizer -n 3 -a -H 0 90 180 270 -P -45 0 35 -S '512x512'
```

## Contributing

The code should be pretty straightforward to understand and modify. Feel free to open an issue or submit a pull request.
