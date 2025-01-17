
Convert the «csv_plotter.ui» file to (python) .py file using pyuic5:

## Step 1 - Using Anaconda or WinPython CMD prompt                        
Pyuic5 is often in «base» environment, so switch to base env.: conda activate base 
Navigate to project folder D:\Python_Prosjekt\211_CSVplotter_v3\ and run following:

pyuic5 csv_plotter.ui -o csv_plotter_ui.py 
Usage: Pyuic5 myInputFile.ui -o myOutputFile.py
(alternative make it possible to run standalone: pyuic5 -x input.ui -o output.py)

## Step 2 - Using Anaconda or WinPython CMD prompt                                    
Navigate to a folder where you have access rights, i.e. "C:\temp" and run following:
pyinstaller.exe --onefile --noconfirm --icon= D:\Python_Prosjekt\211_CSVplotter_v3\wave_graph.ico D:\Python_Prosjekt\211_CSVplotter_v3\main.py
D:\Python_Prosjekt\211_CSVplotter_v3\drag_drop.py



## INFO                                                              
Note that a virtual environment is used containing Python installation with ONLY the packages required (= smaller .exe file)
Example:
 
Følgende er hele forskjellen mellom lasting av en ui fil med loadUi vs. konvertere med pyuic5 til en .py fil og laste
 
 

