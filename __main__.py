import scrap as sp
import GUI
from multiprocessing import freeze_support

def main():
    freeze_support()
    gui = GUI.GUI()
    gui.run()


if __name__ == "__main__":
    main()