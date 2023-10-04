# qgisSpectre

This plugin allows viewing of spectra recorded with geographical information. Using the available selection possibilities in QGIS, spectra can be integrated over a time span, a geospatial selection or any other way a set of features can be selected in QGIS. The primary usage for the plugin is analysis of gamma spectra collected using mobile detectors, such as airborne, carborne or portable. 


To use this:

Store spectra for each location either as an array (eg in postGIS) or as a comma separated integer set


See also:

https://github.com/sickel/qgisstripchart


Usage:

The plugin opens as a window pane. Select the layer containing the specra, then select the column with the spectra. When one or more features in the data set is selected, the spectra integrated over those features will be shown. 

To set energy calibration, type in a and b values and the unit. Press Save to save for the active layer and field, check Set defaults before pressing save to also store new default values. Press "Use defaults" to fetch the default values for the active layer and field.

The last development version of the plugin is available as qgisSpectre.zip in this repository. It may be used, but the preferred way of installation is through QGIS' plugin manager

Demo data:

Two demodataset are included in demodata. Both are created from https://github.com/juhele/opengeodata/tree/master/Airborne_gammaspectrometry_demo_data Please note, the data is from a real flight data set, but it has been moved to another location, see the above mentioned link for more information.

One set is a gpkg file that can be used directly in QGIS, the other is a databasedump that can be imported into a postgis database as the table ulurutest. 

Load the data into QGIS and select the field specstring or spectre (The latter only exists in the postgis version) in the spectre viewer and select some points from the dataset to see the spectre.



