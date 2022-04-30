from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import *
import scrap as sp
from multiprocessing import Pool
import tqdm
from multiprocessing import cpu_count
import csv
from tkinter.filedialog import asksaveasfile
from os import system, name
from time import sleep

def scrape(link):
    data = sp.Scrap(link, "video")
    data = data.run_video_scrapper()
    return data


class GUI:
    # Backend For Requests
    def scrapePool(self):
        self.links = list(set(self.links))
        with Pool(processes=cpu_count()) as pool, tqdm.tqdm(
                total=len(self.links)) as pbar:  # create Pool of processes (only 2 in this example) and tqdm Progress bar
            self.list = []  # into this list I will store the urls returned from parse() function
            for data in pool.imap_unordered(scrape,
                                            self.links):  # send urls from all_urls list to parse() function (it will be done concurently in process pool). The results returned will be unordered (returned when they are available, without waiting for other processes)
                if data != "":
                    self.list.append(data)  # update all_data list
                    pbar.update()


    # Backend For Channel Videos`
    def channel_scrape(self, link):
        data = sp.Scrap(link)
        return data.get_chanel_videos()

    # Create Label
    def main_label(self):
        label = Label(self.gui, text="Enter Link Please", font=("Arial", 20))
        label.pack()

    def radio(self):
        self.type = StringVar(None, "video")
        radiobutton_1 = Radiobutton(self.gui, text='Videos', variable=self.type, value="video")
        radiobutton_1.pack()
        radiobutton_2 = Radiobutton(self.gui, text='Channels', variable=self.type, value="channel")
        radiobutton_2.pack()

    # Create Input & Button
    def input(self):
        style = Style()
        style.configure('W.TButton', font=
        ('calibri', 10, 'bold', 'underline'),
                        foreground='red')
        self.yt_link = ScrolledText(self.gui, height=15)
        self.yt_link.pack()
        self.save_btn = Button(self.gui, text='Generate CSV', style = 'W.TButton', command=self.save)
        self.save_btn.pack(pady=10)

    def run(self):
        self.gui.mainloop()

    def save(self):
        self.saveText = self.yt_link.get('1.0', END)  # Get all text in widget.
        self.radioType = self.type.get()
        self.yt_link.configure(state=DISABLED)
        self.save_btn.configure(state=DISABLED)
        if self.type.get() == "video":
            self.links = self.saveText.split("\n")
            self.links = [i for i in self.links if i]
            self.scrapePool()
            self.csv_export()
            self.finish_process()
        else:
            self.links = self.saveText.split("\n")
            self.links = self.links[0]
            self.links = self.channel_scrape(self.links)
            self.scrapePool()
            self.csv_export()
            self.finish_process()
        print("DONE! Clearing screen in 3 Seconds!")
        sleep(3)
        _ = system('cls')

    def csv_export(self):
        data = [("csv file(*.csv)", "*.csv")]
        try:
            file = asksaveasfile(filetypes=data, defaultextension=data)

            keys = self.list[0].keys()

            with open(file.name, 'w', newline='', encoding="utf-8") as csvfile:
                dict_writer = csv.DictWriter(csvfile, keys)
                dict_writer.writeheader()
                dict_writer.writerows(self.list)
        except:
            pass


    def finish_process(self):
        self.yt_link.configure(state=NORMAL)
        self.save_btn.configure(state=NORMAL)
        self.yt_link.delete("1.0", END)
        self.list = []
        self.links = []


    def __init__(self):
        self.gui = Tk()
        self.gui.title("Youtube Scrapper")
        self.gui.geometry("800x400")
        self.main_label()
        self.radio()
        self.input()
