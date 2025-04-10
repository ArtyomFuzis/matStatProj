from Windows.MainWindow import MainWindow
import pandas as pd
if __name__ == "__main__":
    #mw = MainWindow(pd.read_excel("table.xlsx", nrows=10, skiprows=13, usecols="Z:AA"))
    mw = MainWindow(pd.DataFrame())
    mw.show()

