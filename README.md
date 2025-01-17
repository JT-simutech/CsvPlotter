
Convert the «csv_plotter.ui» file to (python) .py file using pyuic5:

## Step 1 - Update Python file from UI file using Anaconda/miniconda or WinPython CMD prompt                        
Pyuic5 is often in «base» environment, so switch to base env.: conda activate base 
Navigate to project folder C:\GitHub\CsvPlotter\ and run following:

'''
pyuic5 csv_plotter.ui -o csv_plotter_ui.py
'''

Usage: 
''' Pyuic5 myInputFile.ui -o myOutputFile.py '''

Alternative make it possible to run standalone: 
''' pyuic5 -x input.ui -o output.py '''

## Step 2 - Using Anaconda or WinPython CMD prompt                                    
Navigate to a folder where you have access rights, i.e. "C:\GitHub" and run following:
''' pyinstaller.exe --onefile --noconfirm --icon= C:\GitHub\CsvPlotter\wave_graph.ico C:\GitHub\CsvPlotter\main.py
C:\GitHub\CsvPlotter\drag_drop.py '''

## INFO                                                              
Note that a virtual environment is used containing Python installation with ONLY the packages required (= smaller .exe file)

 
 

