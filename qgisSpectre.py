# -*- coding: utf-8 -*-
from os import sys
sys.path.append("/usr/lib/python3/dist-packages/")
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
import qgis.PyQt.QtCore
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction,QGraphicsScene,QApplication,QGraphicsView,QCheckBox
# Initialize Qt resources from file resources.py
from .resources import *
from operator import add # To add spectra

from PyQt5 import QtCore,QtGui
from qgis.core import QgsProject, Qgis, QgsMapLayerType, QgsMapLayer,QgsMapLayerProxyModel,QgsFieldProxyModel

# Import the code for the DockWidget
from .qgisSpectre_dockwidget import qgisSpectreDockWidget
import os.path
import math 

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
        self.toolbar = self.iface.addToolBar(u'qgisSpectre')
        self.toolbar.setObjectName(u'qgisSpectre')


        self.view = MouseReadGraphicsView(self.iface)
        #print "** INITIALIZING qgisSpectre"

        self.pluginIsActive = False
        

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
        self.dlg=qgisSpectreDockWidget(self.iface.mainWindow())
        self.view.setParent(self.dlg) 
        self.dlg.hlMain.addWidget(self.view)
        #self.dlg.cbLayer.currentIndexChanged['QString'].connect(self.listfields)
        self.dlg.qgLayer.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.dlg.qgField.setLayer(self.dlg.qgLayer.currentLayer())
       # self.dlg.qgField.setFilters(QgsFieldProxyModel.Numeric)
        self.dlg.qgLayer.layerChanged.connect(lambda: self.dlg.qgField.setLayer(self.dlg.qgLayer.currentLayer()))    
    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING qgisSpectre"

        # disconnects
        self.dlg.closingPlugin.disconnect(self.onClosePlugin)

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
    
    
    def listfields_delete(self):
        # When selecting a new layer. List fields for that layer
        self.dlg.cbItem.clear()
        layername=self.dlg.qgLayer.currentText()
        layers = QgsProject.instance().mapLayersByName(layername) # list of layers with any name
        if len(layers)==0:
            return
        layer = layers[0] # first layer .
        fields = layer.fields().names() #Get Fiels
        # TODO: Add only if array field, but c.f the idea on using comma-separated numbers
    #    self.dlg.cbItem.addItems(fields) #Added to the comboBox
    
    def drawspectra(self):
        # Drawing the spectra on the graphicsstage
        logscale=self.dlg.cbLog.isChecked()
        if logscale:
            dataset=[]
            for n in self.view.spectreval:
                if n==0:
                    n=0.9
                dataset.append(math.log(n))
        else:
            dataset=self.view.spectreval
        self.spectre=dataset    
        #DONE: Add x and y axis
        #DONE: Add scale factors to scale x axis from channel number to keV
        #TODO: Add settings to have custom unit
        #TODO: Custom scales
        #TODO: Possibly keep spectra
        #DONE: Draw spectra as line, not "line-histogram"
        #TODO: Select different types of 
        #TODO: Save as file 
        #DONE: export to clipboard
        self.scene.h=300 # HEight of stage
        self.scene.clear()
        self.scene.crdtext=None
        self.scene.markerline=None
        self.scene.addRect(0,0,1200,300)
        self.scene.bottom=20 # Bottom clearing (for x tick marks and labels)
        self.scene.left=self.scene.bottom # Left clearing (for y tick marks and labels)
        n=self.scene.left
        bt=self.scene.bottom
        h=self.scene.h
        self.scene.addLine(float(n-1),float(h-bt),float(n-1),10.0) # Y-axis
        self.scene.addLine(float(n-1),float(h-bt-1),float(len(dataset)+10),float(h-bt-1)) # X-axis
        # Need to scale it down if the total number of counts > height of plot
        # TODO: Customizable scale
        fact=1.0
        #if max(dataset) > h-bt-10:
        fact=(h-bt-10)/max(dataset)
        prevch=0
        for ch in dataset:
            # DONE: Use another form of plot. Multiline?
       #     self.scene.addLine(float(n),float(h-bt),float(n),(h-bt-fact*ch))
       #     self.scene.addLine(float(n),float(h-(bt+4)-fact*ch),float(n),(h-bt-fact*ch))
            self.scene.addLine(float(n),float(h-bt-fact*prevch),float(n+1),(h-bt-fact*ch))
            prevch=ch
            n+=1
        tickval=self.tickinterval
        left=self.scene.left
        while tickval < self.scene.acalib*n+self.scene.bcalib:
            tickch=(tickval-self.scene.bcalib)/self.scene.acalib+left
            self.scene.addLine(float(tickch),float(h-bt),float(tickch),float(h-bt+5)) # Ticklines
            text=self.scene.addText(str(tickval))
            text.setPos(tickch+left-40, 280)
            tickval+=self.tickinterval
        text=self.scene.addText(self.unit)
        text.setPos(n+50, 280)
        
        
    def findselected(self):
        # Is being run when points have been selected
        layername=self.dlg.qgLayer.currentText()
        layers = QgsProject.instance().mapLayersByName(layername) # list of layers with selected name
        layer = layers[0] # first layer .
        #TODO: This is a kludge. More layers may have same name in qgis. By doing this, it is only possible 
        #      to plot spectra from the first layer if more have the same name 
        sels=layer.selectedFeatures() # The selected features in the active (from this plugin's point of view) layer
        n=len(sels)
        if n>0:
            self.iface.messageBar().pushMessage(
                    "Drawing", "Selected {} points".format(str(n)),
                    level=Qgis.Success, duration=3)
            fieldname=self.dlg.qgField.currentText()
            # TODO: Rewrite to make it possible to read in a spectra as a string of comma-separated numbers
            if fieldname=='' or fieldname== None:
                return # Invalid fieldname, probably not selected yet
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
                self.view.spectreval=sumspectre
                self.drawspectra()
            else:
                self.iface.messageBar().pushMessage(
                    "Error", "Use an array field",
                    level=Qgis.Success, duration=3)
                
    def spectreToClipboard(self):
        clipboard = QApplication.clipboard()
        text=",".join(str(x) for x in self.spectre)
        clipboard.setText(text)
        
    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            #print "** STARTING qgisSpectre"

            self.tickinterval=100
            # The three former to be user-settable
            self.spectre=[]
            # Setting the scene to plot spectra
            self.unit='Ch'
            self.scene=QGraphicsScene()
            self.scene.crdtext=None
            self.scene.markerline=None
            self.scene.acalib=3.038
            self.scene.bcalib=-6.365
            showch=False
            if showch:
                self.scene.acalib=1
                self.scene.bcalib=0
            self.view.setScene(self.scene)
            self.scene.setSceneRect(0,0,1200,300)
            # Relisting field when new layer is selected:
            # Replotting spectre when a new selection is made
            self.iface.mapCanvas().selectionChanged.connect(self.findselected)        
            # Listing layers
            # TODO: Only list vector layers
            # TODO: Repopulate when layers are added or removed
            #layers = QgsProject.instance().layerTreeRoot().children()
            #self.dlg.cbLayer.clear()
            #for layer in layers:
                #if layer.layer().type==QgsMapLayerType.VectorLayer:
            #       self.dlg.cbLayer.addItem(layer.name())
            #self.dlg.cbLayer.addItems([layer.name() for layer in layers])
            #self.listfields()
            self.dlg.pBCopy.clicked.connect(self.spectreToClipboard)
            #Boilerplate below:
            
            # connect to provide cleanup on closing of dockwidget
            self.dlg.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.mainWindow().addDockWidget(Qt.BottomDockWidgetArea, self.dlg)
            self.dlg.show()
            self.findselected()

class MouseReadGraphicsView(QGraphicsView):
    def __init__(self, iface):
        self.iface = iface
        QGraphicsView.__init__(self)
        
        
        
    def mousePressEvent(self, event):
        if event.button() == 1:
            coords=self.mapToScene(event.pos())    
            x = coords.x()
            if x != None:
                energy=(x-self.scene().left)*self.scene().acalib+self.scene().bcalib
                # DONE: draw a vertical line where clicked. Mark energy
                coords=str(int(energy))+" keV"
                if self.scene().crdtext!=None:
                    self.scene().removeItem(self.scene().crdtext)
                self.scene().crdtext=self.scene().addText(coords)
                self.scene().crdtext.setPos(x,10)
                if self.scene().markerline!=None:
                    self.scene().removeItem(self.scene().markerline)
                self.scene().markerline=self.scene().addLine(x,0,x,300)
