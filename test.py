import pandas as pd

def main():
  gridframe = pd.read_csv('./Data/100m_grid/100m_grid.csv')
  muniframe = pd.read_csv('./Data/municipal_main/municipal_main.csv')
  csframe = pd.read_csv('./Data/HiDrive/cross_section/CampusFile_WM_2023.csv')
  panelframe = pd.read_csv('./Data/HiDrive/panel/CampusFile_WM_cities.csv')
  print(gridframe.describe())
  print(muniframe.describe())
  print(csframe.describe())
  print(panelframe.describe())

if __name__ == "__main__":
  main()