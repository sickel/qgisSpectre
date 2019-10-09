# qgisSpectre

This plugin allows viewing of spectra recorded with geographical information. Using the available selection possibilities in Qgis, spectra can be integrated over a time span, a geospatial selection or any other way a set of features can be selected in Qgis. The primary usage for the plugin is analysis of gamma spectra collected using mobile detectors, such as airborne, carborne or portable. 

The data source needs to be able to store specra as array. The development is presently done using postgis enabled postgresql as the data source.

Usage:
The plugin opens as a window pane. Select the layer containing the specra, then select the column with the spectra. When one or more features in the data set is selected, the spectra integrated over those features will be shown.

Selected TODOs:

- Use energy calibration to convert channel# to energy
- Copy spectra to clipboard
- Save spectra to PNG
- Show more specra simultaneously
- Use a custom scale on the y-axis
- Show specra in log scale
- Only list vector layers in the layer selector
- List only relevant (i.e. array) columns in the column selector
- Allow spectra being stored as comma separated numbers (and adjust point above accordingly)
- Find out how to handle several layers with same name

(known) bugs:
- When doing other selection than simple "draw" selections (rectangle or polygon, I have not tested circle) i.e. invert selection or selection on the feature table, the selection some times needs to be redone to get the specra drawn. 
