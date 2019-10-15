# qgisSpectre

This plugin allows viewing of spectra recorded with geographical information. Using the available selection possibilities in Qgis, spectra can be integrated over a time span, a geospatial selection or any other way a set of features can be selected in Qgis. The primary usage for the plugin is analysis of gamma spectra collected using mobile detectors, such as airborne, carborne or portable. 

The data source needs to be able to store specra as array. The development is presently done using postgis enabled postgresql as the data source.

To use this:

* create a postgis enabled postgresql database
* create a table in the database using schema.sql
* Set the correct connection parameters in readdata.py
* Import a csv-file exported from RSI radassist using readdata.py. It must contain the base data and the virtual detector spectra

Spectra data from other systems may also be used. Use readdata.py as a template for writing a new import function.


See also:

https://github.com/sickel/qgisstripchart

Usage:

The plugin opens as a window pane. Select the layer containing the specra, then select the column with the spectra. When one or more features in the data set is selected, the spectra integrated over those features will be shown.

Selected TODOs:

- Correct energy calibration - make it user settable
- Copy spectra to clipboard - Done, as comma separated channel values
- Save spectra to PNG
- Show more specra simultaneously
- Use a custom scale on the y-axis
- Show specra in log scale
- Only list vector layers in the layer selector
- List only relevant (i.e. array) columns in the column selector
- Allow spectra being stored as comma separated numbers (and adjust point above accordingly)
- Find out how to handle several layers with same name

