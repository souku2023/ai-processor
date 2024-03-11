import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.font import Font
import os
from concurrent.futures import ThreadPoolExecutor
# from core.app_logger import AppLogger
import sys
sys.path.append(os.getcwd())

from core.stitching import Stitching
from core.app_logger import AppLogger

class GUI(tk.Tk):
    """
    """

    def __init__(self, *args, **kwargs):
        """
        """

        super().__init__(*args, **kwargs)

        font = Font(size=20)

        day_frame = tk.Frame(self)
        day_frame.grid(row=0, column=0, sticky='nsew')
        day_label = tk.Label(day_frame, text="Day: ", font=font)
        day_label.grid(row=0, column=0)
        self.day_entry = tk.Entry(day_frame, font=font)
        self.day_entry.grid(row=0, column=1)

        date_frame = tk.Frame(self)
        date_frame.grid(row=1, column=0, sticky='nsew')
        date_label = tk.Label(date_frame, text="Date: ", font=font)
        date_label.grid(row=0, column=0)
        self.date_entry = tk.Entry(date_frame, font=font)
        self.date_entry.grid(row=0, column=1)

        session_frame = tk.Frame(self)
        session_frame.grid(row=2, column=0, sticky='nsew')
        session_label = tk.Label(session_frame, text="Session: ", font=font)
        session_label.grid(row=0, column=0, sticky='nsw')
        session_options = (
            'Morning',
            'Afternoon',
            'Evening'
        )
        self.session_option = tk.StringVar()
        session_option_menu = tk.OptionMenu(session_frame,
                                            self.session_option,
                                            session_options[0],
                                            *session_options[1:],
                                            command=self.get_session_option,
                                            )
        session_option_menu.config(font=font)
        session_option_menu.grid(row=0, column=1, sticky='nsew')

        image_type_frame = tk.Frame(self)
        image_type_frame.grid(row=3, column=0, sticky='nsw')
        image_type_label = tk.Label(image_type_frame, text="Image Type: ", font=font)
        image_type_label.grid(row=0, column=0, sticky='nsw')
        rgb_option = (
            'RGB',
            'MS'
        )
        self.image_type_option = tk.StringVar()
        image_type_option_menu = tk.OptionMenu(
            image_type_frame,
            self.image_type_option,
            rgb_option[0],
            *rgb_option[1:],
            command=self.get_image_type_option,
        )
        image_type_option_menu.config(font=font)
        image_type_option_menu.grid(row=0, column=1, sticky='nsew')

        alt_frame = tk.Frame(self)
        alt_frame.grid(row=4, column=0, sticky='nsew')
        alt_label = tk.Label(alt_frame, text="Altitude: ", font=font)
        alt_label.grid(row=0, column=0, sticky='nsw')
        alt_options = (
            '60',
            '80',
            '120'
        )
        self.alt_option = tk.StringVar()
        alt_option_menu = tk.OptionMenu(
            alt_frame,
            self.alt_option,
            alt_options[0],
            *alt_options[1:],
            command=self.get_alt_option,
        )
        alt_option_menu.config(font=font)
        alt_option_menu.grid(row=0, column=1, sticky='nsew')

        self.input_image_path = tk.StringVar()
        # self.input_image_path.set(os.getcwd())
        input_image_path_frame = tk.Frame(self)
        input_image_path_frame.grid(row=5, column=0, sticky='nsew')
        input_image_path_label = tk.Label(input_image_path_frame, text="Images Path: ", font=font)
        input_image_path_label.grid(row=0, column=0)
        input_image_path_entry = tk.Entry(input_image_path_frame, textvariable=self.input_image_path, font=font, width=60)
        input_image_path_entry.grid(row=0, column=1, sticky='nsew')
        input_image_path_browse_button = tk.Button(input_image_path_frame, text="Browse...", command=self.get_image_input_path, font=font)
        input_image_path_browse_button.grid(row=0, column=2, sticky='nsew')

        self.output_path = tk.StringVar()
        # self.output_path.set(os.getcwd())
        output_path_frame = tk.Frame(self)
        output_path_frame.grid(row=6, column=0, sticky='nsew')
        output_path_label = tk.Label(output_path_frame, text="Output Path: ", font=font)
        output_path_label.grid(row=0, column=0)
        output_path_entry = tk.Entry(output_path_frame, textvariable=self.output_path, font=font, width=60)
        output_path_entry.grid(row=0, column=1, sticky='nsew')
        output_path_browse_button = tk.Button(output_path_frame, text="Browse...", command=self.get_output_path, font=font)
        output_path_browse_button.grid(row=0, column=2, sticky='nsew')
        
        submit_button = tk.Button(self, text="Submit", font=font, command=self.submit)
        submit_button.grid(row=7, column=0, sticky='nsew')
        
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.tasks = list()
        
    def get_session_option(self, opt):
        self.session_option.set(opt)

    def get_image_type_option(self,opt):
        print(opt)
        self.image_type_option.set(opt)

    def get_alt_option(self,opt):
        self.alt_option.set(opt)

    def get_image_input_path(self):
        file = filedialog.askdirectory(initialdir=os.getcwd())
        self.input_image_path.set(file)

    def get_output_path(self):
        file = filedialog.askdirectory(initialdir=os.getcwd())
        self.output_path.set(file)
        
    def submit(self):
        self.name = f"DAY{self.date_entry.get()}_{self.date_entry.get()}_{self.alt_option.get()}m_{self.session_option.get()}_{self.image_type_option.get()}"
        project_name, output_dir, input_dir = a.get_dets()
        AppLogger.info(f"Added new project: {self.name}")
        self.tasks.append(
            self.executor.submit(Stitching.stitch_images_by_kml, 
                                 input_dir, 
                                 output_dir, 
                                 project_name))
        
        
    def get_dets(self):
        return [self.name, self.output_path.get(), self.input_image_path.get()]
    

if __name__ == '__main__':
    a = GUI()
    a.mainloop()
    print()
    a.executor.shutdown()