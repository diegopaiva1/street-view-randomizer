# Street View Explorer

A Python command-line interface designed to generate random images from [Google Street View](http://maps.google.com).

## Requirements

- Python >= 3.5
- [Google Maps Platform](https://developers.google.com/maps) API key

## Install

Install dependencies:

```
pip3 install python-dotenv
pip3 install geopandas
pip3 install shapely
```

Copy `.env.example` contents to `.env`:

```
cp .env.example .env
```

Insert you API key into the newly created `.env` file.

## Usage

Running with no arguments defaults to generating a single image anywhere in the world (equal probabilities with respect to countries sizes):

```
python3 main.py
```

Output:

```
Searched image in LSO | lat:  -29.718921255685007 lon:    27.61507311464558 | elapsed time:   448.36ms

> Image found in LSO (Lesotho) | lat: -29.72434941923827, lon: 27.62813570641534 | attempts: 1 | total elapsed time: 0.45s

Saving images/lso/-29.72434941923827_27.62813570641534_h0_p0.jpg...
```

### General options

#### `-c`

Use the `-c` argument together with a list of one or more [ISO3 country codes](https://www.iban.com/country-codes) to narrow the search. For instance, if we are interested in fetching an image from either Brazil, Argentina or Chile:

```
python3 main.py -c BRA ARG CHL
```

#### `-l`

Display a list of all available countries (those with some Google Street View Coverage).

#### `-r`

Defines a radius in meters centered on a latitude and longitude. The default value is 5.000 (5km). This value should only be increased if searching for an image is taking too long. 

#### `-a`

If the size of the country matters when sampling from a group of countries, passing in the `-a` flag will give bigger countries more chances of being drawn. The following chart shows the odds for each country if we consider the full space search:

![areas_percentage](https://user-images.githubusercontent.com/32985519/204120495-179ce98a-7544-4cd8-a22c-e10ccab81fed.png)

#### `-n`

To **sample** more than once (this doesn't mean fetching more than one image per country), pass in the `-n` flag with some desired number, e.g.:

```
python3 main.py -n 3
```

Note that the maximum number of iterations allowed is **28.000**, which happens to be the maximum number of requests per month one can make without being charged by the Google Maps Platform. Be careful!

### Image options

Images are saved under the `images/<country-iso3-code>` directory from where you run the script. Images names follow the convention:

```
<lat>_<lon>_h<heading>_p<pitch>_f<fov>.jpg
```

Please refer to the [Street View Static API documentation](https://developers.google.com/maps/documentation/streetview/request-streetview) to understand the meaning of `heading`, `pitch` and `fov`.

Anyway, you are allowed to pass a list of each one of these parameters to generate different imagery from the same coordinate.

#### `-H`

List of headings, e.g., `-H 0 90 180 270`. The default value is 0.

#### `-P`

List of pitches, e.g., `-P -35 0 35`. The default value is 0.

#### `-F`

List of fovs, e.g., `-F 60 90 120`. The default value is 90.

Note that the total number of images will be the product of the length of each list. For each heading, the algorithm will output an image for each pair of pitch and fov.

#### `-S`

Size of the output image, defaults to 256x256. The maximum size allowed is 640x640. Each dimension must have at least a hundred pixels.

### Putting it all together

The following command will perform 3 weighted samplings of 12 images of size 512x512:

```
python3 main.py -n 3 -a -H 0 90 180 270 -P -45 0 35 -S '512x512'
```
