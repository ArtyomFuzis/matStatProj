from Windows.MainWindow import MainWindow
import pandas as pd

from Windows.SystemParamsShowWindow import SystemParamsShowWindow

if __name__ == "__main__":
    #mw = MainWindow(pd.read_excel("test_area.xlsx", nrows=7, skiprows=14, usecols="P:X"))
    mw = MainWindow(pd.read_excel("test2.xlsx", nrows=13, skiprows=21, usecols="K:S"))
    #mw = MainWindow(pd.DataFrame())
    mw.show()

