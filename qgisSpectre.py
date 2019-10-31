# -*- coding: utf-8 -*-
from os import sys
sys.path.append("/usr/lib/python3/dist-packages/")
"""
/***************************************************************************
 qgisSpectre
                                 A QGIS plugin


iew spectra stored in a geodataset. The spectral data must be stored in an array, e.g. as an postgres array datafield. When features in the dataset are selected, the integrated spectra over these features will be displayed. 

The energycalibration is presently hardcoded, look for the values acalib and bcalib. (Energy=acalib*channel + bcalib)

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
from qgis.PyQt.QtGui import QIcon, QImage, QPainter
from qgis.PyQt.QtWidgets import QAction,QGraphicsScene,QApplication,QGraphicsView,QCheckBox, QFileDialog
from PyQt5.QtGui import QIcon
# Initialize Qt resources from file resources.py
from .resources import *
from operator import add # To add spectra

from PyQt5 import QtCore,QtGui
from qgis.core import QgsProject, Qgis, QgsMapLayerType, QgsMapLayer,QgsMapLayerProxyModel,QgsFieldProxyModel
from qgis.PyQt.QtGui import QPen, QBrush
# Import the code for the DockWidget
from .qgisSpectre_dockwidget import qgisSpectreDockWidget
import os.path
import math 
import json

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
        self.toolbar = self.iface.addToolBar(u'Spectre viewer')
        self.toolbar.setObjectName(u'Spectre viewer')


        self.view = MouseReadGraphicsView(self.iface)
        #print "** INITIALIZING qgisSpectre"
        # Initialize calibration information
        self.calibfilename='calibrations.json'
        """ TODO: Read in calibrations from calibration.json in the plugin directory
            if the file does not exist, initialize the calibration hash with default values
            When the values are changed, store the values under the layer and field in the 
            calib dir and write it back to the file"""
        jsonfile=self.plugin_dir+"/"+self.calibfilename
        #self.iface.messageBar().pushMessage(
        #       "Storing", self.plugin_dir+"+>"+jsonfile,
        #        level=Qgis.Success, duration=3)
        self.defaultname='_Z_Z_Z_default' 
        try:
            with open(jsonfile) as readfile:
                self.calibration=json.load(readfile)
            self.iface.messageBar().pushMessage(
               "reading", self.plugin_dir+"+>"+jsonfile,
                level=Qgis.Success, duration=3)
            # Reads in stored calibrations
        except:
            self.calibration=dict()
            self.calibration[self.defaultname]=dict()
            self.calibration[self.defaultname][self.defaultname]={"acalib":3.024,"bcalib":-4.365}
            with open(jsonfile,'w') as writefile:
                json.dump(self.calibration,writefile)
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
    
    def drawspectra(self):
        """ Drawing the spectra on the graphicsstage """
        logscale=self.dlg.cbLog.isChecked()
        if logscale:
            dataset=[]
            for n in self.view.spectreval:
                if n==0:
                    n=0.9
                dataset.append(math.log(n)-math.log(0.9))
        else:
            dataset=self.view.spectreval
        #DONE: Add x and y axis
        #DONE: Add scale factors to scale x axis from channel number to keV
        #TODO: Add settings to have custom unit
        #TODO: Custom scales
        #TODO: Keep spectra to compare
        #DONE: Draw spectra as line, not "line-histogram"
        #TODO: Select different types of 
        #DONE: Save as file 
        #DONE: export data to clipboard
        #TODO: export image to clipboard
        #TODO: Peak detection
        self.scene.h=300 # Height of stage
        self.scene.clear()
        self.scene.crdtext=None
        self.scene.markerline=None
        backgroundbrush=QBrush(Qt.white)
        outlinepen=QPen(Qt.white)
        self.scene.addRect(0,0,1200,300,outlinepen,backgroundbrush)
        self.scene.bottom=20 # Bottom clearing (for x tick marks and labels)
        self.scene.left=self.scene.bottom # Left clearing (for y tick marks and labels)
        n=self.scene.left
        bt=self.scene.bottom
        h=self.scene.h
        self.scene.addLine(float(n-1),float(h-bt),float(n-1),10.0) # Y-axis
        self.scene.addLine(float(n-1),float(h-bt-1),float(len(dataset)+10),float(h-bt-1)) # X-axis
        # Scales the spectra to fit with the size of the graphicsview
        fact=1.0
        fact=(h-bt-10)/max(dataset)
        prevch=0
        for ch in dataset:
            # TODO: User selectable type of plot
       #     self.scene.addLine(float(n),float(h-bt),float(n),(h-bt-fact*ch))
       #     self.scene.addLine(float(n),float(h-(bt+4)-fact*ch),float(n),(h-bt-fact*ch))
            self.scene.addLine(float(n),float(h-bt-fact*prevch),float(n+1),(h-bt-fact*ch))
            prevch=ch
            n+=1
        self.scene.end=n-1
        tickval=self.tickinterval
        acalib=self.calibration[self.defaultname][self.defaultname]["acalib"]
        bcalib=self.calibration[self.defaultname][self.defaultname]["bcalib"]
        
        maxval=acalib*n+bcalib
        tickdist=tickval
        #if maxval/n > 5:             # Avoids to tight numbering. 
        #    tickdist*=2 # Needs some better vay of doing this - 
        left=self.scene.left
        while tickval < maxval:
            tickch=(tickval-bcalib)/acalib+left
            self.scene.addLine(float(tickch),float(h-bt),float(tickch),float(h-bt+5)) # Ticklines
            text=self.scene.addText(str(tickval))
            text.setPos(tickch+left-40, 280)
            tickval+=tickdist
        text=self.scene.addText(self.unit)
        text.setPos(self.scene.end+15,280)
        ntext=self.scene.addText("n = {}".format(str(self.view.n)))
        ntext.setPos(self.scene.end+50,1)
        
    def updatecalib(self):
        # Store values per layer and field
        layername=self.dlg.qgLayer.currentText()
        fieldname=self.dlg.qgField.currentText()
        self.scene.acalib=float(self.dlg.leA.text())
        self.scene.bcalib=float(self.dlg.leB.text())
        if not (layername in self.calibration):
            self.calibration[layername]=dict()
        self.calibration[layername][fieldname]={"acalib":self.scene.acalib,"bcalib":self.scene.bcalib}
        # The following lines to be removed when laib per layer is handled correctly        
    
    def setdefault(self):
        # TODO: COnnect to default checkbos
        self.calibration[self.defaultname][self.defaultname]["acalib"]=self.scene.acalib
        self.calibration[self.defaultname][self.defaultname]["bcalib"]=self.scene.bcalib
        # TODO: Set acalib and bcalib to default values when button is pressed
        
    def findselected(self):
        """ Is being run when points have been selected. Makes a sum spectra from selected points"""
        layername=self.dlg.qgLayer.currentText()
        fieldname=self.dlg.qgField.currentText()
        layer=self.dlg.qgLayer.currentLayer()
        if layer==None:
            return # Happens some times, just as well to return
        if layername in self.calibration:
            if fieldname in self.calibration[layername]:
                self.scene.acalib=self.calibration[layername][fieldname]["acalib"]
                self.scene.bcalib=self.calibration[layername][fieldname]["bcalib"]
        else:
            self.scene.acalib=self.calibration[self.defaultname][self.defaultname]["acalib"]
            self.scene.bcalib=self.calibration[self.defaultname][self.defaultname]["bcalib"]
        self.dlg.leA.setText(str(self.scene.acalib))
        self.dlg.leB.setText(str(self.scene.bcalib))
        sels=layer.selectedFeatures() # The selected features in the active (from this plugin's point of view) layer
        n=len(sels)
        if n>0:
            #self.iface.messageBar().pushMessage(
            #        "Drawing spectra", "Integrated over {} measurements".format(str(n)),
            #        level=Qgis.Success, duration=3)
            fieldname=self.dlg.qgField.currentText()
            # TODO: Rewrite to make it possible to read in a spectra as a string of comma-separated numbers
            if fieldname=='' or fieldname== None:
                return # Invalid fieldname, probably not selected yet
            stringspec = isinstance(sels[0][fieldname],str)
            stringspec = stringspec and (sels[0][fieldname].find(',') != -1)
            if isinstance(sels[0][fieldname],list) or stringspec:
                # Only draw if a list field is selected
                sumspectre = None
                for sel in sels:
                    spectre=sel[fieldname]
                    if stringspec:
                        vals=spectre.split(',')
                        spectre = list(map(int, vals))
                    del spectre[-1] # To get rid of last channel i.e. cosmic from RSI-spectra
                                    # TODO: customable removal of channels at top and/or bottom
                    if sumspectre == None:
                        sumspectre = spectre
                    else:
                        sumspectre = list( map(add, spectre, sumspectre))
                self.view.spectreval=sumspectre
                self.view.n=n
                self.drawspectra()
            else:
                self.iface.messageBar().pushMessage(
                    "Error", "Use an array field or a comma separated string",
                    level=Qgis.Warning, duration=3)
                    
    def spectreToClipboard(self):
        """ Copies the channel values to the clipboard as a comma separated string"""
        clipboard = QApplication.clipboard()
        text=",".join(str(x) for x in self.view.spectreval)
        clipboard.setText(text)
        
        # TODO: Make a graphical copy
    def saveCalibration(self):
        """ Saves the calibration data """
        jsonfile=self.plugin_dir+"/"+self.calibfilename
        with open(jsonfile,'w') as writefile:
            json.dump(self.calibration,writefile)
        
        
        
    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True
            self.scene=QGraphicsScene()
            # Storing the spectra to be able to read out values later on
            # Setting the values storing line and text shown when the mouse button is clicked
            self.scene.crdtext=None
            self.scene.markerline=None
            self.scene.left=None
            # TODO: The four next settings to be user-settable
            self.tickinterval=100
            #self.scene.acalib=3.038
            #self.scene.bcalib=-6.365
            self.scene.acalib=self.calibration[self.defaultname][self.defaultname]["acalib"]
            self.scene.bcalib=self.calibration[self.defaultname][self.defaultname]["bcalib"]
            self.dlg.leA.setText(str(self.scene.acalib))
            self.dlg.leB.setText(str(self.scene.bcalib))
            self.unit='keV'
            showch=False # Set to True to show channel values
            if showch:
                self.unit='Ch'
                self.scene.acalib=1
                self.scene.bcalib=0
            self.view.setScene(self.scene)
            self.scene.setSceneRect(0,0,1200,300)
            # Replotting spectre when a new selection is made
            self.iface.mapCanvas().selectionChanged.connect(self.findselected)        
            # Listing layers
            # DONE: Only list vector layers
            # DONE: Repopulate when layers are added or removed
            # DONE both by using qgisWidget
            self.dlg.pBCopy.clicked.connect(self.spectreToClipboard)
            self.dlg.pBSaveCalib.clicked.connect(self.saveCalibration)
            self.dlg.pBSave.clicked.connect(self.view.saveImage)
            
            # connect to provide cleanup on closing of dockwidget
            self.dlg.closingPlugin.connect(self.onClosePlugin)
            # show the dockwidget
            self.iface.mainWindow().addDockWidget(Qt.BottomDockWidgetArea, self.dlg)
            self.dlg.show()
            self.dlg.cbLog.stateChanged.connect(self.findselected)
            self.dlg.qgField.currentIndexChanged['QString'].connect(self.findselected)
            self.dlg.qgLayer.currentIndexChanged['QString'].connect(self.findselected)
            self.dlg.leA.textChanged['QString'].connect(self.updatecalib)
            self.dlg.leB.textChanged['QString'].connect(self.updatecalib)
            self.findselected()
            
                
class MouseReadGraphicsView(QGraphicsView):
    """ A class based on QGraphicsView to enable capture of mouse events"""
    
    def __init__(self, iface):
        self.iface = iface
        QGraphicsView.__init__(self)
        self.linex=0
    #TODO: Use arrowkeys to move marker up and down in spectra
        
    
    def drawline(self):
        """ Prints a marker line and reads out energy and number of counts"""
        #TODO: Show list of nuclides with peak at actual energy
        #      Maybe as a further extention as this is radionuclide specific.
        scene=self.scene()
        x=self.linex
        ch=x-scene.left
        
        energy=ch*scene.acalib+scene.bcalib
        # DONE: draw a vertical line where clicked. Mark energy
        message="{} keV (n={})".format(int(energy),self.spectreval[int(ch)])
        if self.scene().crdtext!=None:
            self.scene().removeItem(self.scene().crdtext)
        if self.scene().markerline!=None:
            self.scene().removeItem(self.scene().markerline)
        self.scene().crdtext=self.scene().addText(message)
        self.scene().crdtext.setPos(x,20)
        self.scene().markerline=self.scene().addLine(x,0,x,300-(scene.bottom+5))
    
    def keyPressEvent(self,event):
        ### Reads key presses to move marker line """
        #TODO: Use proper key constants
        if event.key()==Qt.Key_Space:
            self.saveImage()
            return
        if event.key()==Qt.Key_Right: #16777236: #right arrowkey
            self.linex+=1
        if event.key()==Qt.Key_Left: #16777234: # left arrowkey
            self.linex-=1
        if event.key()==Qt.Key_Up: #16777235: # up arrow
            self.linex+=10
        if event.key()==Qt.Key_Down: #16777237: # down arrow
            self.linex-=10
        self.linex=max(self.scene().left,self.linex)
        self.linex=min(self.scene().end,self.linex)
        self.drawline()
        if event.key()==Qt.Key_Escape: # To  be set to Esc 
            if self.scene().crdtext!=None:
                self.scene().removeItem(self.scene().crdtext)
            if self.scene().markerline!=None:
                self.scene().removeItem(self.scene().markerline)
        
    def saveImage(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","Image files (*.png);;All Files (*)", options=options)
        if not fileName:
            return
        # Get region of scene to capture from somewhere.
        area = self.scene().sceneRect()
        # Create a QImage to render to and fix up a QPainter for it.
        image = QImage(area.width(),area.height(), QImage.Format_ARGB32_Premultiplied)
        painter = QPainter(image)
        # Render the region of interest to the QImage.
        self.scene().render(painter)
        painter.end()
        # Save the image to a file.
        image.save(fileName)
        
    def mousePressEvent(self, event):
        """ Press the left mouse button to draw a line and print the energy at the point"""
        
        #DONE: Show n at line
        if event.button() == 1:
            if self.scene().left == None: # Not yet initialized
                return
            coords=self.mapToScene(event.pos())    
            x = coords.x()
            self.linex=x
            # Make sure the data not is read out when being outside the spectra
            if x != None and x > self.scene().left and x < self.scene().end:
                self.drawline()
