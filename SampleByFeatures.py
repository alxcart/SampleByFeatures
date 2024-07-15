# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SampleByFeatures
                                 A QGIS plugin
 The sampling plan by feature class (layer) calculates the sample size (n) from population size (N), inspection level (I, II or III) and acceptable quality limit (AQL). 
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-04-02
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Alex Santos
        email                : alxcart@gmail.com
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from qgis.core import *
from math import ceil
#import os.path
from osgeo import ogr
import random

from .main_sample_plan import * # functions of project
#from .constants import * # constants of project
#import sys # usar no desenvolvimento #
#sys.path.append(os.path.abspath(r"C:/Users/Admin/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/SampleByFeatures/"))
#from main_sample_plan import *

# based on the clip_multiple_layers plugin
import processing, os, subprocess, time
from qgis.utils import *
from qgis.PyQt.QtCore import *
from processing.algs.gdal.GdalUtils import GdalUtils

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .SampleByFeatures_dialog import SampleByFeaturesDialog
import os.path

class SampleByFeatures:
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
            'SampleByFeatures_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Sample by features')

        # Create the dialog (after translation) and keep reference
        self.dlg = SampleByFeaturesDialog()

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

        #Connecting the buttons and actions / Conectando os botoes e acoes
        self.dlg.lineEdit.clear()
        self.initFolder()
        self.dlg.pushButton.clicked.connect(self.select_output_file)
        # add news buttons here        


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
        return QCoreApplication.translate('SampleByFeatures', message)


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
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/SampleByFeatures/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Sample by features'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&Sample by features'),
                action)
            self.iface.removeToolBarIcon(action)

    def initFolder(self):
        path_project = QgsProject.instance().fileName()
        path_project = path_project[:path_project.rfind("/"):]
        self.folderName = path_project

        self.dlg.lineEdit.setText(self.folderName)

    def select_output_file(self):
    #Select output folder / Seleciona a pasta de saida
        folderTmp = QFileDialog.getExistingDirectory(self.dlg, "Select output folder ", self.folderName)
        if folderTmp != "":
            self.folderName = folderTmp
        self.dlg.lineEdit.setText(self.folderName)

    def isFileOpened(self, file_path):
        if os.path.exists(file_path):
            try:
                os.rename(file_path, file_path+"_")
                os.rename(file_path+"_", file_path)
                return False
            except OSError as e:
                return True

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = SampleByFeaturesDialog()
            self.dlg.pushButton.clicked.connect(self.select_output_file)

        # Preenchendo o comboBox (principal)
        self.dlg.comboBox.clear()
        #self.dlg.lineEditSize.setText(str(4.0))
        #self.dlg.comboBoxLevel.setItemText(self, 1, "II")

        #layers = list_layers()
        
        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer :
                if layer.isValid()==True and layer.__len__()>=1: # layer valido e com pelo menos 1 registro
                    self.dlg.comboBox.addItem(layer.name(), layer )

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            #pass
            try: 
                if not os.path.isdir(self.folderName):
                    raise FileNotFoundError(
                        errno.ENOENT, os.strerror(errno.ENOENT), self.folderName)
            except NameError:
                QMessageBox.critical(None, "Folder not found", "Please select folder")
                return True

            directory = self.folderName + "/sample_" + str(ATIVO) 
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            #Input data selection
            index = self.dlg.comboBox.currentIndex()
            selection = self.dlg.comboBox.itemData(index)
            checkedLayers = QgsProject.instance().layerTreeRoot().checkedLayers()
            
            # Sampling plan / Plano de amostragem
            nivel_inspecao = self.dlg.comboBoxLevel.currentIndex()
            tipo_inspecao = self.dlg.comboBoxType.currentIndex()
            lqa = self.dlg.comboBoxLQA.currentIndex()
            

            
            ###########  Sample by area ###############################   
            if ATIVO =="area": 
                isSelectedId, features, N, n, num_aceitacao, letra_codigo_i, letra_codigo_f, msg = grid_square(selection, nivel_inspecao, lqa, tipo_inspecao, size)
            
            ###########  Sample by features ###########################   

            if ATIVO == "feature":
                N, n, num_aceitacao, letra_codigo_i, letra_codigo_f, msg = sample_plan (features_selection(selection), nivel_inspecao, lqa + 4 , tipo_inspecao)
                features = selection
                isSelectedId = sample_features(N, n)          

  

            if N > n and ATIVO == 'feature':
                #codigo_arquivo, nome_arquivo, amostra_virtual = output_sample_plan(N, n, selection, directory, msg, num_aceitacao, ATIVO)
                codigo_arquivo, nome_arquivo, amostra_virtual = output_sample_plan (N, n, selection, directory, features, isSelectedId, msg, num_aceitacao, ATIVO)
                filename = nome_arquivo
                ly_virtual = amostra_virtual
                size = selection.__len__()

                sumario, texto_resultado = msg_sample_plan( N, n, num_aceitacao, letra_codigo_i, letra_codigo_f, msg, lqa, nivel_inspecao)
                texto_metadado = metadado(sumario, texto_resultado, size, selection.name(), nome_arquivo)
                save_gpkg(ly_virtual, filename, codigo_arquivo)  

                layer = QgsVectorLayer(nome_arquivo, "sample_" + str(ATIVO) + "_" + str(codigo_arquivo) ,"ogr")
                if layer.isValid() == True:
                    f = open (directory + "/sample_" + str(ATIVO) + "_" + codigo_arquivo + ".qmd", "w+")
                    f.write(texto_metadado)
                    f.close()
                    # criar função define_style
                    dir_style = os.path.dirname(__file__) # 'C:\\Users/Admin/AppData/Roaming/QGIS/QGIS3\\profiles\\default/python/plugins\\SampleByArea'
                    style = (dir_style + '/inspecao_a.qml')
                    style_inspecao_p = (dir_style + '/inspecao_p.qml')
                    layer_sample = iface.addVectorLayer(nome_arquivo, "" ,"ogr")
                    # Definir o caminho para o arquivo Geopackage
                    #geopackage_path = filename

                    # Definir o nome da camada e o nome do estilo
                    layer_name = "sample_" + str(ATIVO) + codigo_arquivo
                    layer_inspecao = "inspecao_p"
                    #style sample area
                    project = QgsProject.instance()
                    #layer = project.mapLayersByName(layer_name)[0]
                    layer.loadNamedStyle(style)
                    layer.saveNamedStyle(directory + "/sample_" + str(ATIVO) + "_" + codigo_arquivo + ".qml") 
                    #success = layer.saveStyleToDatabase(style, "sample", QgsStyle.UseLayerName)
                    #style inspecao pontual
                    #inspecao_p_style = project.mapLayersByName(layer_inspecao)#[0]
                    #inspecao_p_style.loadNamedStyle(style_inspecao_p)
                    #inspecao_p_style.saveNamedStyle(directory + "/inspecao_p.qml")
                    #style_manager = QgsMapLayerStyleManager(str(qml_path+ "/sample_area_" + codigo_arquivo + ".qml"))
                    #style_manager.saveStyleToDatabase(style_name, geopackage_path)
                                       
                    QMessageBox.about(None, "Sample by feature", sumario)
                if layer.isValid() == False:
                    QMessageBox.warning(None, "Sample by feature", "O arquivo " + 
                                        codigo_arquivo + " já existe na pasta.\n" +
                                        "\n   Por favor, alterar os parâmetros do plano de amostragem" +
                                        "\nou selecionar uma nova pasta.\n"
                                        )

                # carregar metadado neste momento. 
                # checar existencia do arquivo antes de escrever. Atualmente, o anterior é perdido. 
                #Carregar camada
                #QgsProject.instance().addMapLayer(ly)
                           
            if N <= n:
                msg_complete( N, n, msg)