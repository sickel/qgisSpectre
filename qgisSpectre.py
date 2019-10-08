# -*- coding: utf-8 -*-
"""
/***************************************************************************
 qgisSpectre
                                 A QGIS plugin
 To view spectra
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-10-07
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Morten Sickel
        email                : morten@sickel.net
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction,QGraphicsScene
# Initialize Qt resources from file resources.py
from .resources import *
from operator import add # To add spectra

from PyQt5 import QtCore,QtGui
from qgis.core import QgsProject, Qgis

# Import the code for the DockWidget
from .qgisSpectre_dockwidget import qgisSpectreDockWidget
import os.path


class qgisSpectre:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'qgisSpectre_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Spectre Viewer')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'qgisSpectre')
        self.toolbar.setObjectName(u'qgisSpectre')

        #print "** INITIALIZING qgisSpectre"

        self.pluginIsActive = False
        self.dockwidget = None


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('qgisSpectre', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToDatabaseMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/qgisSpectre/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'View Spectra'),
            callback=self.run,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING qgisSpectre"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD qgisSpectre"

        for action in self.actions:
            self.iface.removePluginDatabaseMenu(
                self.tr(u'&Spectre Viewer'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
    
    # Boilerplate so far
    #--------------------------------------------------------------------------
    
    def listfields(self):
        # When selecting a new layer. List fields for that layer
        self.dockwidget.cbItem.clear()
        layername=self.dockwidget.cbLayer.currentText()
        layers = QgsProject.instance().mapLayersByName(layername) # list of layers with any name
        layer = layers[0] # first layer .
        fields = layer.fields().names() #Get Fiels
        # TODO: Add only if array field
        self.dockwidget.cbItem.addItems(fields) #Added to the comboBox
    
    def drawspectra(self,dataset):
        # Drawing the spectra on the graphicsstage
        h=300
        self.scene.clear()
        self.scene.addRect(0,0,1200,300)
        bt=20
        n=bt
        self.scene.addLine(float(n-1),float(h-bt),float(n-1),10.0) # Y-axis
        self.scene.addLine(float(n-1),float(h-bt-1),float(len(dataset)+10),float(h-bt-1)) # X-axis
        fact=1.0
        if max(dataset) > h-bt-10:
            fact=(h-bt-10)/max(dataset)
        self.iface.messageBar().pushMessage(
                    "Info", "maxvalue {}".format(str(max(dataset))),
                    level=Qgis.Success, duration=3)
            
        for ch in dataset:
            self.scene.addLine(float(n),float(h-bt),float(n),(h-bt-fact*ch))
            if n%100==0:
                self.scene.addLine(float(n),float(h-bt),float(n),float(h-bt+5)) # Ticklines
            
            n+=1
        #DONE: Add x and y axis
        #TODO: Add scale factors to scale x axis from channel number to keV
        #TODO: Add settings to have custom unit
        #TODO: Custom scales
        #TODO: Possibly keep spectra
        #TODO: Draw spectra as line, not "line-histogram"
        #TODO: Save as file or export to clipboard
        
    def findselected(self):
        # Is being run when points have been selected
        layername=self.dockwidget.cbLayer.currentText()
        layers = QgsProject.instance().mapLayersByName(layername) # list of layers with selected name
        layer = layers[0] # first layer .
        #TODO: THis is a kludge. More layers may have same name in qgis. By doing this, it is only possible 
        #      to plot spectra from the first layer if more have the same name 
        sels=layer.selectedFeatures() # The selected features in the active (from this plugin's point of view) layer
        n=len(sels)
        if n>0:
            self.iface.messageBar().pushMessage(
                    "Success", "Selected {} points".format(str(n)),
                    level=Qgis.Success, duration=3)
            fieldname=self.dockwidget.cbItem.currentText()
            if isinstance(sels[0][fieldname],list):
                sumspectre = None
                for sel in sels:
                    spectre=sel[fieldname]
                    del spectre[-1] # To get rid of last channel i.e. cosmic from RSI-spectra
                                    # TODO: Make this customable
                    if sumspectre == None:
                        sumspectre = spectre
                    else:
                        sumspectre = list( map(add, spectre, sumspectre))
                self.drawspectra(sumspectre)
            else:
                self.iface.messageBar().pushMessage(
                    "Error", "Use an array field",
                    level=Qgis.Success, duration=3)
                
                
        
    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            #print "** STARTING qgisSpectre"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = qgisSpectreDockWidget()
            # Setting the scene to plot spectra
            self.scene=QGraphicsScene()
            self.dockwidget.graphicsView.setScene(self.scene)
            self.scene.setSceneRect(0,0,1200,300)
            # Relisting field when new layer is selected:
            self.dockwidget.cbLayer.currentIndexChanged['QString'].connect(self.listfields)
            # Replotting spectre when a new selection is made
            self.iface.mapCanvas().selectionChanged.connect(self.findselected)        
            # Listing layers
            # TODO: Only list vector layers
            # TODO: Repopulate when layers are added or removed
            layers = QgsProject.instance().layerTreeRoot().children()
            self.dockwidget.cbLayer.clear()
            self.dockwidget.cbLayer.addItems([layer.name() for layer in layers])
            self.listfields()
            
            #Boilerplate below:
            
            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.BottomDockWidgetArea, self.dockwidget)
            self.dockwidget.show()
