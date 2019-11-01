# qgisSpectre

This plugin allows viewing of spectra recorded with geographical information. Using the available selection possibilities in Qgis, spectra can be integrated over a time span, a geospatial selection or any other way a set of features can be selected in Qgis. The primary usage for the plugin is analysis of gamma spectra collected using mobile detectors, such as airborne, carborne or portable. 

The data source needs to be able to store specra as array. The development is presently done using postgis enabled postgresql as the data source.

To use this:

* create a postgis enabled postgresql database
* create a table in the database using schema.sql
* Set the correct connection parameters in readdata.py
* Import a csv-file exported from RSI radassist using readdata.py. It must contain the base data and the virtual detector spectra

Spectra data from other systems may also be used. Use readdata.py or readspe.py as a template for writing a new import function. As both these are storing data using the postgresql array field type, it will not work in any other data base systems I know of. To store it in other systems, store the spectre as a comma separated string.

See also:

https://github.com/sickel/qgisstripchart


Usage:

The plugin opens as a window pane. Select the layer containing the specra, then select the column with the spectra. When one or more features in the data set is selected, the spectra integrated over those features will be shown.

Demo data:

Two demodataset are included in demodata. Both are created from https://github.com/juhele/opengeodata/tree/master/Airborne_gammaspectrometry_demo_data Please note, the data is from a real flight data set, but it has been moved to another location, see the above mentioned link for more information.

One set is a gpkg file that can be used directly in QGIS, the other is a databasedump that can be imported into a postgis database as the table ulurutest. 

Load the data into QGIS and select the field specstring or spectre (The latter only exists in the postgis version) in the spectre viewer and select some points from the dataset to see the spectre.


Selected TODOs:

- Correct energy calibration - make it user settable - In work. Will release as 1.0 non-experimental when this is finished
- Copy spectra to clipboard - Done, as comma separated channel values
- Save spectra to PNG - Done
- Show more specra simultaneously - May look into this after v 1.0. 
- Use a custom scale on the y-axis - May look into this after v 1.0.
- List only relevant (i.e. array and strings) columns in the column selector
- Allow spectra being stored as comma separated numbers (and adjust point above accordingly) - DONE

