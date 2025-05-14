from Windows.MainWindow import MainWindow
import pandas as pd
if __name__ == "__main__":
    #mw = MainWindow(pd.read_excel("test.xlsx", nrows=14, skiprows=12, usecols="P:R"))
    #mw = MainWindow(pd.read_excel("test.xlsx", nrows=15, skiprows=0, usecols="A:I"))
    mw = MainWindow(pd.read_excel("test.xlsx", nrows=15, skiprows=23, usecols="X:AB"))
    #mw = MainWindow(pd.DataFrame())

    mw.show()

