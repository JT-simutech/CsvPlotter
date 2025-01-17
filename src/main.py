'''
v1  2022-07-02 - Created based on Pyshine project for csv plot single file
v2  2022-07-04 - Added possibility to read .txt files from SIMIT in addition to csv
v3 draft  2022-07-05 - Modified text and data file input reading, added fixed second y-scale
v3 final 2022-07-05 - Added scale factor. Updated plot and tested with two csv + a text file 
v4 final 2022-07-12 - Combined file open filter to both text and csv.
v5 final 2022-07-12 - Updated GUI and x-axis offset. Added Refresh buttons for dataset 1 and 2.

@Author: John Tore Andreassen
'''

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as Navi
from matplotlib.figure import Figure
import seaborn as sns
import pandas as pd
import numpy as np
import sip # can be installed : pip install sip
from datetime import datetime
import os #To handle file dialogue

# GUI add-on methods
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtGui import QDoubleValidator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as Navi

# Build .exe with using the pyuic generated csv_plotter.py
from csv_plotter_ui import Ui_MainWindow # Added to build from pyuic5 py file

# We require a canvas class (called from Update)
class MatplotlibCanvas(FigureCanvasQTAgg):
    def __init__(self,parent=None, dpi = 90):
        
        #Note: only reason to set "self" in self.fig is to be able to use legend
        self.fig = Figure(dpi = dpi)
        
        self.axes = self.fig.add_subplot(111)
        super(MatplotlibCanvas,self).__init__(self.fig)
        self.fig.tight_layout()
        
        
class data(QtWidgets.QMainWindow, Ui_MainWindow): # Add Ui_MainWindow as arg to build from pyuic5 py file
    def __init__(self):
        super(data, self).__init__() # Call the inherited classes __init__ method
        #uic.loadUi('csv_plotter.ui', self)     # Remove to build from ui directly
        self.ui = Ui_MainWindow()               # Added to build from pyuic5 py file
        self.setupUi(self)                      # Added to build from pyuic5 py file
        self.GUI_version = 'v6Alpha'
        self.setWindowTitle('Plot comparison tool for csv/txt datasets - JT. Andreassen - build '+ self.GUI_version)
        self.show()
        self.connectSignalsSlots()

        self.filename1 = ''
        self.filename2 = ''
        self.Title1 = ''
        self.Title2 = ''
        self.plot_title = 'File 1 vs. File 2'
        self.canv = MatplotlibCanvas(self)
        
        # Dataset 1 and 2
        self.dataset1={}
        self.dataset2={}
        
        self.txt_file_separator = '\t'
        self.txt_file_header_row = 0
        
        # List for populating the comboboxes (same for x/y boxes) 
        self.list_of_columns_dataset1 = []
        self.list_of_columns_dataset2 = []
        
        self.data1_x_axis_slt=None
        self.data1_y_axis_slt=None
        
        self.data2_x_axis_slt=None
        self.data2_y_axis_slt=None
        
        self.data1_x_axis_multiplier = 1
        self.data2_x_axis_multiplier = 1
        
        # Initial x-axis offset scaling
        self.offset_data1_x_axis = 0
        self.offset_data2_x_axis = 0
        
        # Control the input values for x-axis multipliers
        self.lineEdit_data1_x_multiplier.setValidator(QDoubleValidator())
        self.lineEdit_data2_x_multiplier.setValidator(QDoubleValidator())
        
        # Option to use separate y-scale for dataset 2
        self.enable_second_yscale = False
        
        # Add a list of themes, but for now only select in code
        self.themes = ['bmh', 'classic', 'dark_background', 'fast', 
        'fivethirtyeight', 'ggplot', 'grayscale', 'seaborn-bright',
         'seaborn-colorblind', 'seaborn-dark-palette', 'seaborn-dark', 
         'seaborn-darkgrid', 'seaborn-deep', 'seaborn-muted', 'seaborn-notebook',
         'seaborn-paper', 'seaborn-pastel', 'seaborn-poster', 'seaborn-talk',
         'seaborn-ticks', 'seaborn-white', 'seaborn-whitegrid', 'seaborn',
         'Solarize_Light2', 'tableau-colorblind10']

        # Make a theme selection based on list above(static for now)
        self.current_theme = self.themes[4]
        
        # The plot toolbar can be embedded but is not
        # part of the design in the .ui file
        self.toolbar = Navi(self.canv,self.centralwidget)
        self.horizontalLayout_top_common.addWidget(self.toolbar)
    
    # Initializing, called from Update() method
    def refresh_canvas(self):
        try:
            self.horizontalLayout_top_common.removeWidget(self.toolbar)
            self.verticalLayout.removeWidget(self.canv)    
            sip.delete(self.toolbar)
            sip.delete(self.canv)
            self.toolbar = None
            self.canv = None
        except Exception as e:
            print(e)
            pass
        self.canv = MatplotlibCanvas(self)
        self.toolbar = Navi(self.canv,self.centralwidget)
        
        # Add the plot toolbar onto the layout
        self.horizontalLayout_top_common.addWidget(self.toolbar)
        
        # Add the plot canvas to the central/bottom layout
        self.verticalLayout.addWidget(self.canv)
        self.canv.axes.cla()
                

    def select_data1_Xaxis(self,value):
        print('data 1 x-axis',value)
        self.data1_x_axis_slt=value
        self.Update(self.current_theme)
        
    def select_data1_Yaxis(self,value):
        print('data 1 y-axis',value)
        self.data1_y_axis_slt=value
        self.Update(self.current_theme)

    def select_data2_Xaxis(self,value):
        print('data 2 x-axis',value)
        self.data2_x_axis_slt=value
        self.Update(self.current_theme)
        
    def select_data2_Yaxis(self,value):
        print('data 2 y-axis',value)
        self.data2_y_axis_slt=value
        self.Update(self.current_theme)

  
    # Updates the plot, uses a string value in to select plot style
    def Update(self,value):
        print("Updating plot..")
        plt.style.use(value)
        
        # Reduce scope for the Update method, do some delete/refresh..
        self.refresh_canvas()
        
        # Initial axis /base axis
        ax = self.canv.axes
        
        try:     
            # Compare y1 in datasets 1 and 2
            # Numpy array is the datatype. Add/subtract offset constant to all elements
            xdata1 = self.dataset1[self.data1_x_axis_slt]+ self.offset_data1_x_axis
            
            # Scale the xdata (i.e. millisec to sec --> use 0.001 as multiplier)
            xdata1 = np.multiply(xdata1, self.data1_x_axis_multiplier)
            
            # If there is no second data yet, we need to know so we can skip errors
            dataset2_has_data = len(self.dataset2) > 0
            
            ax.plot( xdata1, self.dataset1[self.data1_y_axis_slt],
                    label=(self.Title1 + '\n' + self.data1_y_axis_slt))
            
            self.plot_title = self.Title1
            
            #TODO Y-scale tick marks
            
            # Adjust plot with the dataset 2 info
            if dataset2_has_data:
                xdata2 = self.dataset2[self.data2_x_axis_slt]+ self.offset_data2_x_axis
                xdata2 = np.multiply(xdata2, self.data2_x_axis_multiplier)
                self.plot_title = self.Title1 + " vs. " + self.Title2
                
                if self.enable_second_yscale:
                    ax2 = ax.twinx()
                    
                    ax2.plot( xdata2, self.dataset2[self.data2_y_axis_slt], '-r',   
                             label=self.Title2 + '\n' + self.data2_y_axis_slt)
                    ax2.set_ylabel(self.data2_y_axis_slt)
                    
                if not self.enable_second_yscale:
                    ax.plot( xdata2, self.dataset2[self.data2_y_axis_slt],
                            label=self.Title2 + '\n' + self.data2_y_axis_slt)
            
            # The fig legend is better than the ax legends (Matplotlib >2.1)
            # bbox to anch/transform is to get location within axes again
            self.canv.fig.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax.transAxes)
            
            ax.set_xlabel(self.data1_x_axis_slt)
            ax.set_ylabel(self.data1_y_axis_slt)
            ax.set_title(self.plot_title)
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=25)  # uncomment if you want the x-axis to tilt 25 degree
            
        except Exception as e:
            print('Error from update ==>',e)
            pass
        
        self.canv.draw()
    
    def getFile1(self):
        """ This function will get the address of the csv file location
            also calls a readData function 
        """
        self.filename1 = QFileDialog.getOpenFileName(filter = "Data file(*.csv *.txt)")[0]
        print("File :", self.filename1)
        self.readDatafile1()
    
    def getFile2(self): 
        self.filename2 = QFileDialog.getOpenFileName(filter = "Data file(*.csv *.txt)")[0]
        print("File :", self.filename2)
        self.readDatafile2()
    
    # .csv file reader
    def getDataset_csv(self,csvfilename):
        df = pd.read_csv(csvfilename,encoding='utf-8').fillna(0)
        LIST_OF_COLUMNS = df.columns.tolist()
        dataset={}
        
        # TIME FORMAT handling (optional / will skip if not formatted ok)
        #time_format = '%Y-%m-%d %H:%M:%S.%f' # Please use this format for time_series-data_2.csv kind of time stamp
        time_format = '%d/%m/%Y %H:%M%f'     # Please use this format for time_series-data_1.csv kind of time stamp
        
        for col in LIST_OF_COLUMNS:
            dataset[col]  =  df[col].iloc[0:].values
            try:
                dataset[col] = [datetime.strptime(i, time_format) for i in df[col].iloc[0:].values]
            except Exception as e:
                pass
                print(e)
        return dataset,LIST_OF_COLUMNS
    
    # .txt file reader
    def getDataset_txt(self, txt_filename):
        df = pd.read_csv(txt_filename, 
                               sep = self.txt_file_separator,
                               header=self.txt_file_header_row, 
                               encoding='utf-8', 
                               engine='python')
        LIST_OF_COLUMNS = df.columns.tolist()
        dataset={}
        
        for col in LIST_OF_COLUMNS:
            dataset[col]  =  df[col].iloc[0:].values
        return dataset,LIST_OF_COLUMNS
  
    
    def readDatafile1(self):
        self.data1_x_axis_slt=None
        self.data1_y_axis_slt=None
        self.dataset1={}

        base_name = os.path.basename(self.filename1)
        self.Title1 = os.path.splitext(base_name)[0]
        print('FILE 1', self.Title1)
        
        if 'txt' in base_name:
            self.dataset1, self.list_of_columns_dataset1 = self.getDataset_txt(self.filename1)
        if 'csv' in base_name:
            self.dataset1, self.list_of_columns_dataset1 = self.getDataset_csv(self.filename1)
           
        #self.df1 = pd.read_csv(self.filename1,encoding = 'utf-8').fillna(0)
        self.Update(self.current_theme) # lets 0th theme be the default : bmh
        self.reset_comboBoxes_data1()
        
    def readDatafile2(self):
        self.data2_x_axis_slt=None
        self.data2_y_axis_slt=None
        self.dataset2={}
        
        base_name = os.path.basename(self.filename2)
        self.Title2 = os.path.splitext(base_name)[0]
        print('FILE 2',self.Title2 )
        
        if 'txt' in base_name:
            self.dataset2, self.list_of_columns_dataset2 = self.getDataset_txt(self.filename2)
        if 'csv' in base_name:
            self.dataset2, self.list_of_columns_dataset2 = self.getDataset_csv(self.filename2)
  
        #self.df2 = pd.read_csv(self.filename2,encoding = 'utf-8').fillna(0)    
        self.Update(self.current_theme) # lets 0th theme be the default : bmh
        self.reset_comboBoxes_data2()
        
    
    def set_data1_x_offset(self, value):
        if value == 0:
            return
        self.lineEdit_data1_x_axis_offset.setText(str(value)) #Update indication
        value = float(value)
        self.offset_data1_x_axis = value
        print('Adjusted data 1 x-offset to: ', value)
        self.Update(self.current_theme)
    
    def set_data2_x_offset(self, value):
        if value == 0:
            return
        self.lineEdit_data2_x_axis_offset.setText(str(value)) #Update indication
        value = float(value)
        self.offset_data2_x_axis = value
        print('Adjusted data 2 x-offset to: ', value)
        self.Update(self.current_theme)
        
    
    # LineEdit for dataset 1, x axis multiplier
    def set_data1_x_multiplier(self, text):
        try:
             self.data1_x_axis_multiplier = float(text)
             self.Update(self.current_theme)
             print("Updated data 1 x-axis multiplier")
        except Exception as e:
            print('Dataset 1 x-multiplier input is wrong, use float i.e. 2.0 :', e)
    
     # LineEdit for dataset 2, x axis multiplier
    def set_data2_x_multiplier(self, text):
        try:
             self.data2_x_axis_multiplier = float(text)
             self.Update(self.current_theme)
             print("Updated data 2 x-axis multiplier")
        except Exception as e:
            print('Dataset 2 x-multiplier input is wrong: use float i.e. 2.0', e)

    def toggle_second_yaxis(self, b):
        if not b.isChecked():
            print('Disabled 2nd y-axis')
            self.enable_second_yscale = False
            self.Update(self.current_theme)
            return
        print('Enabled 2nd y-axis')
        self.enable_second_yscale = True
        self.Update(self.current_theme)
    
    def reset_comboBoxes_data1(self):
        self.comboBox_data1_x_axis.clear()
        self.comboBox_data1_y_axis.clear()
        self.comboBox_data1_x_axis.addItems(['Select horizontal axis here'])
        self.comboBox_data1_y_axis.addItems(['Select vertical axis here'])
        self.comboBox_data1_x_axis.addItems(self.list_of_columns_dataset1)
        self.comboBox_data1_y_axis.addItems(self.list_of_columns_dataset1)
    
    def reset_comboBoxes_data2(self):
        self.comboBox_data2_x_axis.clear()
        self.comboBox_data2_y_axis.clear()
        self.comboBox_data2_x_axis.addItems(['Select horizontal axis here'])
        self.comboBox_data2_y_axis.addItems(['Select vertical axis here'])
        self.comboBox_data2_x_axis.addItems(self.list_of_columns_dataset2)
        self.comboBox_data2_y_axis.addItems(self.list_of_columns_dataset2)
        
        
    def show_about_popup(self):
        msg = QMessageBox()
        msg.setWindowTitle("About the csv plot tool..")
        msg.setText("Compare data from two datasets with tab formatted txt\n or a comma separated file.\n\n\n Created by John Tore Andreassen - Siemens-Energy")
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
        
        
    # Connect action buttons to application actions
    def connectSignalsSlots(self): 
        self.comboBox_data1_x_axis.currentIndexChanged['QString'].connect(self.select_data1_Xaxis)
        self.comboBox_data1_y_axis.currentIndexChanged['QString'].connect(self.select_data1_Yaxis)

        self.comboBox_data2_x_axis.currentIndexChanged['QString'].connect(self.select_data2_Xaxis)
        self.comboBox_data2_y_axis.currentIndexChanged['QString'].connect(self.select_data2_Yaxis)
        
        self.actionOpen_csv_file_1.triggered.connect(self.getFile1)
        self.actionOpen_csv_file_2.triggered.connect(self.getFile2)
        self.actionExit.triggered.connect(self.close)
        self.actionAbout.triggered.connect(self.show_about_popup)
        
        # Connect action for the X-axis offset sliders
        self.slider_data1_x_axis_offset.valueChanged[int].connect(self.set_data1_x_offset)
        self.slider_data2_x_axis_offset.valueChanged[int].connect(self.set_data2_x_offset)
        
        # Connect same action for when the input is written in lineedit box instead of slider
        self.lineEdit_data1_x_axis_offset.textChanged.connect(self.set_data1_x_offset)
        self.lineEdit_data2_x_axis_offset.textChanged.connect(self.set_data2_x_offset)
        
        self.lineEdit_data1_x_multiplier.textChanged.connect(self.set_data1_x_multiplier)
        self.lineEdit_data2_x_multiplier.textChanged.connect(self.set_data2_x_multiplier)
        
        self.checkBox_enable_second_yscale.stateChanged.connect(lambda:self.toggle_second_yaxis(self.checkBox_enable_second_yscale))
        
        # Refresh-buttons
        self.pushButton_refresh_data1.clicked.connect(self.readDatafile1)
        self.pushButton_refresh_data2.clicked.connect(self.readDatafile2)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = data()  
    sys.exit(app.exec_())

