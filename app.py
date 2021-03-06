import tkinter as tk
from tkinter.filedialog import askopenfile, asksaveasfile, askopenfiles, askdirectory

from copy import deepcopy

from time import sleep

from tkinter.simpledialog import askfloat, askinteger

from tkinter.ttk import Separator, Combobox
from PIL import Image, ImageTk
from PIL.Image import DecompressionBombError

import io
import os


CANVAS_SIZE = (600, 300)
PREVIEW_SIZE = (600, 300)

INITIAL_FILE_SIZE_MB = 49.9

INSTA_CUT_DEFAULT_TAILS_VARIANTS = [3, 4, 5, 6, 7, 8, 9, 10]
INSTA_CUT_DEFAULT_TAILS_AMOUNT = INSTA_CUT_DEFAULT_TAILS_VARIANTS[0]
INSTA_CUT_MINIMUM_TAIL_SIZE_PX = 1080

Image.MAX_IMAGE_PIXELS = None



class PanResizer(object):
    def __init__(self):

        self.main_frame = None
        self.canvas = None
        self.settings_ver_sep = None

        self.logo_label = None
        self.info_box = None

        self.initial_file_path = None
        self.initial_file = None
        self.initial_img = None
        self.initial_file_mb = None
        self.initial_height = None
        self.initial_width = None

        self.img_preview = None

        self.needed_mb = None
        self.icc_profile = None
        self.im_info_dpi = None
        self.candidate_img = None

        self.rect = None
        self.touch_center = None
        self.move_corner = None
        self.rect_color = None

        self.preview_canvas = None
        self.result_size = None
        self.bulk_mode = None
        self.bulk_files = None

        self.butch_size_default = INITIAL_FILE_SIZE_MB
        self.insta_exact_pixels = None

        self.crop_factor_x = None
        self.crop_factor_y = None
        self.is_resize_complete = None
        self.filesize = None
        self.bulk_counter = None
        self.bulk_count_now = None
        self.is_next_button_pressed = False

        self.insta_preview_img = None
        self.insta_start_cut_preview_position_x = None
        self.insta_start_cut_original_position_x = None
        self.insta_start_cut_preview_position_y = None
        self.insta_start_cut_original_position_y = None
        self.insta_parts_amount = None
        self.insta_ver_seps = []
        self.insta_start_cutting_btn = None
        self.insta_is_start_btn_visible = None
        self.teil_heigh = None

        self.rect_cords = None
        self.rect_middle_point_x = None
        self.rect_middle_point_y = None

        self.is_settings_opened = None
        self.master_column_number = 3
        self.master_row_nubmer = 12

        self.settings_frame = None
        self.settings_def_size_lbl = None
        self.settings_butch_size_radio_var = None
        self.settings_butch_size_mode = None
        self.settings_ask_default_value_btn = None
        self.settings_ask_exact_pixels_button = None

        self.settings_insta_tails_amount = None
        self.settings_insta_tails_drop = None

    def create_canvas(self):
        self.main_frame = tk.Frame(self.root, padx=0, width=CANVAS_SIZE[0])
        self.canvas = tk.Canvas(self.main_frame, height=CANVAS_SIZE[0], width=CANVAS_SIZE[1],
                                borderwidth=0)
        self.canvas.grid(column=self.master_column_number, row=self.master_row_nubmer,
                         padx=0, pady=0)

    def add_settings_button(self):

        settings_btn_text = tk.StringVar()
        settings_btn = tk.Button(self.root, textvariable=settings_btn_text,
                                 font="Raleway",
                                 command=lambda: self.toggle_settings())
        settings_btn_text.set("Settings")
        settings_btn.grid(column=0, row=0)

    def add_logo(self):
        logo = Image.open('logo.jpg')
        logo = ImageTk.PhotoImage(logo)
        logo_label = tk.Label(self.root, image=logo, height=200, anchor='center')
        logo_label.image = logo
        logo_label.grid(column=1, row=0)

    def add_instructions(self):
        open_jpg_instr = tk.Label(self.root, text="Select JPG to resize", font="Raleway")
        open_jpg_instr.grid(column=0, row=1)
        open_jpgs_instr = tk.Label(self.root, text="Select several JPGs to resize", font="Raleway")
        open_jpgs_instr.grid(column=0, row=3)
        open_fldr_instr = tk.Label(self.root, text="Select folder to process all JPGs", font="Raleway")
        open_fldr_instr.grid(column=0, row=5)
        open_insta_cut_instr = tk.Label(self.root, text="Select JPG for instagram cutting", font="Raleway")
        open_insta_cut_instr.grid(column=0, row=8)

    def add_open_button(self):
        browse_text = tk.StringVar()
        browse_btn = tk.Button(self.root, textvariable=browse_text,
                               font="Raleway",
                               command=lambda: self.open_file())
        browse_text.set("Browse...")
        sep = Separator(master=self.root, orient='horizontal')
        sep.grid(column=0, row=2, sticky="we", columnspan=2, pady=5)
        browse_btn.grid(column=1, row=1)

    def add_bulk_open_button(self):
        bulk_browse_text = tk.StringVar()
        bulk_browse_btn = tk.Button(self.root, textvariable=bulk_browse_text,
                                    font="Raleway",
                                    command=lambda: self.open_bulk_files(),
                                    anchor='center')
        bulk_browse_text.set("Browse several...")
        sep = Separator(master=self.root, orient='horizontal')
        sep.grid(column=0, row=4, sticky="we", columnspan=2)
        bulk_browse_btn.grid(column=1, row=3, pady=5, sticky='n')
        # bulk_browse_btn.grid(column=1, row=3, sticky='n')

    def add_folder_open_button(self):
        fldr_browse_text = tk.StringVar()
        fldr_browse_btn = tk.Button(self.root, textvariable=fldr_browse_text,
                                    font="Raleway",
                                    command=lambda: self.open_folder(),
                                    anchor='center')
        fldr_browse_text.set("Select folder...")
        sep1 = Separator(master=self.root, orient='horizontal')
        sep1.grid(column=0, row=6, columnspan=2, sticky="we")
        sep2 = Separator(master=self.root, orient='horizontal')
        sep2.grid(column=0, row=7, columnspan=2, sticky="we")
        fldr_browse_btn.grid(column=1, row=5, pady=5, sticky='n')

    def add_insta_cutter_button(self):
        insta_cutter_open_btn_text = tk.StringVar()
        insta_cutter_open_btn = tk.Button(self.root,
                                          textvariable=insta_cutter_open_btn_text,
                                          font="Raleway",
                                          command=lambda: self.open_insta_cutter(),
                                          anchor='center')
        insta_cutter_open_btn_text.set("Browse file")
        insta_cutter_open_btn.grid(column=1, row=8, pady=5, sticky='n')

    def toggle_insta_start_cutting_button(self):
        if not self.insta_is_start_btn_visible:
            print(self.insta_parts_amount, 'paaaarts')
            insta_start_cutting_btn_text = tk.StringVar()
            self.insta_start_cutting_btn = tk.Button(self.root,
                                                     textvariable=insta_start_cutting_btn_text,
                                                     font="Raleway",
                                                     command=lambda: self.start_insta_cutting(),
                                                     anchor='center')
            insta_start_cutting_btn_text.set("Start cutting")
            self.insta_start_cutting_btn.grid(column=1, row=11, sticky='nw', ipady=15)
            self.insta_is_start_btn_visible = True
            # self.insta_start_cutting_btn.after(3000, self.insta_start_cutting_btn.destroy)
        else:
            if self.insta_start_cutting_btn:
                print('Knopka prisutsvuet')
                self.insta_is_start_btn_visible = True
            else:
                self.insta_is_start_btn_visible = True

    def add_info_box(self):
        self.info_box = tk.Text(self.root, height=20, width=65, padx=20, font=("Raleway", 10))
        self.info_box.grid(columnspan=2, column=0, row=12)

    def update_info_box(self, message):
        self.info_box.insert(1.0, '\n\n%s' % message)

    def open_file(self):
        file = tk.filedialog.askopenfile(title="Choose a file",
                                         filetype=[("JPG file", "*.jpg"),
                                                   ("JPEG file", "*.jpeg")]
                                         )
        self.bulk_mode = False
        self.insta_parts_amount = None
        self.toggle_insta_start_cutting_button()
        if file:
            self.bulk_files = [file]
            self.update_info_box('File "%s" is opened.' % file.name)
            self.bulk_count_now = 0
            self.start()
        else:
            return

    def open_bulk_files(self):
        files = tk.filedialog.askopenfiles(title="Choose a files",
                                           filetype=[("JPG file", "*.jpg"),
                                                     ("JPEG file", "*.jpeg")]
                                           )
        self.insta_parts_amount = None
        self.bulk_mode = True

        self.initial_file = None
        self.initial_img = None
        self.initial_file_path = None

        if files:
            self.bulk_files = files

            self.update_info_box('Files are opened:\n %s' % [f.name for f in self.bulk_files])
            self.bulk_counter = len(self.bulk_files)
            self.bulk_count_now = 0

            self.start()

    def open_folder(self):

        folder_path = tk.filedialog.askdirectory(title="Choose folder to process all images")

        files = []
        if folder_path:

            folder_files = os.listdir(folder_path)

            for f in folder_files:
                f = io.TextIOWrapper(open((os.sep.join([folder_path, f]))))
                files.append(f)

            self.insta_parts_amount = None
            self.bulk_mode = True

            self.initial_file = None
            self.initial_img = None
            self.initial_file_path = None

            self.bulk_files = files
            self.bulk_count_now = 0
            self.bulk_counter = len(self.bulk_files)

            self.start()

    def open_insta_cutter(self):
        file = askopenfile(title="Choose a file",
                           filetype=[("JPG file", "*.jpg"),
                                     ("JPEG file", "*.jpeg")]
                           )
        if file:
            self.initial_file = file
            self.update_info_box('File "%s" is opened.' % file.name)

            self.start_inst_cutter()
        else:
            return

    def start(self):
        self.initial_file = None
        self.initial_img = None
        self.initial_file_path = None

        self.is_resize_complete = None

        if self.bulk_mode:
            self.add_counter_display()

        if self.bulk_files:
            self.bulk_counter = len(self.bulk_files)
            try:
                f = self.bulk_files[self.bulk_count_now]
                self.initial_file = f
                self.initial_img = Image.open(f.name)
                # self.initial_photo_img = ImageTk.PhotoImage(self.initial_img)

                self.update_info_box(str('---' * 35) + '\n')
                if self.bulk_mode:
                    self.update_info_box("[Image %s of %s ]" % (self.bulk_count_now + 1, self.bulk_counter))
                self.update_info_box('Starting processing file:\n%s' % f.name)
                self.calculate_initial_data()
                self.make_preview()
                if not self.butch_size_default:
                    print('size default: %s' % self.butch_size_default)
                    self.ask_new_size()
                else:
                    self.needed_mb = self.butch_size_default
                self.smart_resize()
                self.save_process()
            except IndexError:
                self.update_info_box(str('---' * 35) + '\n')
                self.update_info_box('All images are processed.')
                return

            except Exception as e:
                self.update_info_box(e)

    def start_inst_cutter(self):

        self.initial_img = None

        if self.initial_file:

            self.initial_img = Image.open(self.initial_file.name)
            self.update_info_box('File opened for cutting:\n%s' % self.initial_file.name)

            self.calculate_initial_data()
            self.make_preview()

            self.calculate_insta_data()
        else:
            return

    def calculate_insta_data(self):

        if self.initial_img:
            if not self.settings_insta_tails_amount:
                self.insta_parts_amount = INSTA_CUT_DEFAULT_TAILS_VARIANTS[0]
            else:
                self.insta_parts_amount = self.settings_insta_tails_amount.get()

            if self.rect:
                self.preview_canvas.delete(self.rect)
            if self.touch_center:
                self.preview_canvas.delete(self.touch_center)
            if self.move_corner:
                self.preview_canvas.delete(self.move_corner)
            if self.insta_ver_seps:
                for sep in self.insta_ver_seps:
                    self.preview_canvas.delete(sep)

            if self.settings_ask_exact_pixels_button and self.settings_resizable_frame_button:
                if self.insta_exact_pixels:
                    try:
                        self.settings_ask_exact_pixels_button['state'] = 'disabled'
                        self.settings_resizable_frame_button['state'] = 'normal'
                    except Exception as e:
                        print('e!: %s' % e)
                else:
                    try:
                        self.settings_ask_exact_pixels_button['state'] = 'normal'
                        self.settings_resizable_frame_button['state'] = 'disabled'
                    except Exception as e:
                        print('e!: %s' % e)


            self.add_responsive_frame()



    def add_responsive_frame(self):

        def move_vert_seps():
            self.rect_cords = self.preview_canvas.coords(self.rect)
            # move vert separs
            self.teil_heigh = self.rect_cords[3] - self.rect_cords[1]
            print('UUU')
            print(len(self.insta_ver_seps))
            for s in range(1, len(self.insta_ver_seps) + 1):
                print(self.rect_cords[0] + (self.rect_cords[-1] * s))
                self.preview_canvas.coords(
                    self.insta_ver_seps[s-1],
                    self.rect_cords[0] + (self.teil_heigh * s),
                    self.rect_cords[1],
                    self.rect_cords[0] + (self.teil_heigh * s),
                    self.rect_cords[3],
                )

        def move_rect(x1, y1, x2, y2):
            # move rect
            self.preview_canvas.coords(self.rect, x1, y1, x2, y2)

        def move_central_point(event):
            # move central pint
            self.preview_canvas.coords(self.touch_center,
                                       event.x - 5,
                                       event.y - 5,
                                       event.x + 5,
                                       event.y + 5)

        def move_resize_point():
            # move resize point
            self.preview_canvas.coords(self.move_corner,
                                       self.rect_cords[2] - 3,
                                       self.rect_cords[3] - 3,
                                       self.rect_cords[2] + 3,
                                       self.rect_cords[3] + 3)

        def on_move(event):


            # self.rect_cords = self.preview_canvas.coords(self.rect)
            self.rect_cords = self.preview_canvas.coords(self.rect)

            self.teil_heigh = self.rect_cords[3] - self.rect_cords[1]
            print('teil_heigh: %s' % self.teil_heigh)

            half_rect_length = (self.rect_cords[2] - self.rect_cords[0]) / 2
            half_rect_height = (self.rect_cords[3] - self.rect_cords[1]) / 2
            # rect_middle_point_y = self.rect_cords[3] / 2

            # if not self.resized_rect_cords:
            # self.resized_rect_cords = self.preview_canvas.coords(self.rect)

            print('rect_middle_point_x: %s ' % rect_middle_point_x)


            x1, y1, x2, y2 = (event.x - half_rect_length,
                              event.y - half_rect_height,
                              event.x + half_rect_length,
                              event.y + half_rect_height)

            print('Rect coords on move: %s' % str(self.preview_canvas.coords(self.rect)))
            print('Central point on move: %s\n' % str(self.preview_canvas.coords(self.touch_center)))
            # print('rect_middle_point_x: %s' % rect_middle_point_x)

            if x1 >= -0.0 and x2 < self.preview_img.size[0]+1 and \
                y1 >= 0.0 and y2 < self.preview_img.size[1]+1:

                move_rect(x1, y1, x2, y2)
                move_central_point(event)
                move_resize_point()
                move_vert_seps()

                self.rect_cords = self.preview_canvas.coords(self.rect)
                self.get_insta_frame_position()


        def on_resize(event):

            x1, y1, x2, y2 = (self.preview_canvas.coords(self.rect)[0],
                              self.preview_canvas.coords(self.rect)[1],
                              round(event.x),
                              round(event.y))

            print('Rect coords on resize: %s' % str(self.preview_canvas.coords(self.rect)))
            print('Central point on resize: %s' % str(self.preview_canvas.coords(self.touch_center)))
            print('Corner on resize: %s' % str(self.preview_canvas.coords(self.move_corner)))
            print('min_preview_y: %s' % min_preview_y)

            self.rect_cords = self.preview_canvas.coords(self.rect)

            self.teil_heigh = self.rect_cords[3] - self.rect_cords[1]

            if x1 >= 0 and y1 >= 0 and \
                x2 > (min_preview_y * self.insta_parts_amount) and \
                    x2 < self.preview_img.size[0] and \
                        y2 >= preview_min_y_size and y2 <= self.preview_img.size[1] and \
                            self.rect_cords[2] <= self.preview_img.size[0]:


                move_rect(x1, y1, x1+self.teil_heigh*self.insta_parts_amount, y2)
                move_vert_seps()

                self.rect_cords = self.preview_canvas.coords(self.rect)
                # move touch center
                self.preview_canvas.coords(
                    self.touch_center,
                    (self.rect_cords[2] + self.rect_cords[0]) / 2 - 5,
                    (self.rect_cords[3] + self.rect_cords[1]) / 2 - 5,
                    (self.rect_cords[2] + self.rect_cords[0]) / 2 + 5,
                    (self.rect_cords[3] + self.rect_cords[1]) / 2 + 5)

                self.rect_cords = self.preview_canvas.coords(self.rect)

                # self.rect_cords
                self.get_insta_frame_position()
                move_resize_point()



        if not self.initial_img or not self.insta_parts_amount:
            return
        else:

            print('Preview size: %s' % str(self.img_prevew_size))
            print('Parts amount: %s' % str(self.insta_parts_amount))
        # #
            # self.crop_factor_x = self.img_prevew_size[0] / self.initial_width
            self.crop_factor_y = self.img_prevew_size[1] / self.initial_height
            # print(self.crop_factor_x)
            print('Crop factor: %s' % self.crop_factor_y)

            preview_min_y_size = INSTA_CUT_MINIMUM_TAIL_SIZE_PX * self.crop_factor_y
            print(preview_min_y_size)

            # minimal frame
            # min_preview_x = preview_min_y_size * self.insta_parts_amount * self.crop_factor_y
            min_preview_y = int(preview_min_y_size * self.crop_factor_y) + 1
            # print('Rec: ', rec_x, rec_y)
            # print('Rec: ', min_preview_x, min_preview_y)

            if self.insta_exact_pixels:
                print('Exact pixels: %s' % self.insta_exact_pixels)
                print('Pixels * crop: %s ' % (self.insta_exact_pixels * self.crop_factor_y))
                maximized_y = self.insta_exact_pixels * self.crop_factor_y
                maximized_x = self.insta_exact_pixels * self.insta_parts_amount * self.crop_factor_y
                if maximized_y > self.img_prevew_size[1] or maximized_x > self.img_prevew_size[0]:
                    print('Too large!')
                    return
                self.rect_color = 'yellow'
            else:
                # maximize
                max_y_amount = int(self.img_prevew_size[1] / min_preview_y)
                print('max_y_amount: %s' % max_y_amount)
                maximized_y = min_preview_y * max_y_amount
                maximized_x = maximized_y * self.insta_parts_amount
                print('maximized x _px: %s' % (maximized_x / self.crop_factor_y))
                self.rect_color = 'red'
                if maximized_x > self.img_prevew_size[0]:
                    temp_crop_f = self.img_prevew_size[0] / maximized_x
                    maximized_y = maximized_y * temp_crop_f
                    maximized_x = maximized_y * self.insta_parts_amount - (temp_crop_f * self.insta_parts_amount)

            self.rect = self.preview_canvas.create_rectangle(0, 0,
                                                             maximized_x, maximized_y,
                                                             outline=self.rect_color,
                                                             width=1)
            rect_cords = self.preview_canvas.coords(self.rect)
            print('Rect coords: %s' % rect_cords)

            rect_middle_point_x = rect_cords[2] / 2
            rect_middle_point_y = rect_cords[3] / 2

            # add move point
            self.touch_center = self.preview_canvas.create_oval(rect_middle_point_x-5,
                                                                rect_middle_point_y-5,
                                                                rect_middle_point_x+5,
                                                                rect_middle_point_y+5,
                                                                outline='magenta',
                                                                width=1)
            if not self.insta_exact_pixels:
                # add resize point
                self.move_corner = self.preview_canvas.create_oval(rect_cords[2]-3,
                                                                   rect_cords[3]-3,
                                                                   rect_cords[2]+3,
                                                                   rect_cords[3]+3,
                                                                   outline='yellow',
                                                                   width=1)
            # add separators
            self.insta_ver_seps = []
            if self.insta_parts_amount:
                for i in range(1, self.insta_parts_amount):
                    print(self.insta_parts_amount, ' parts')
                    print(self.preview_canvas.coords(self.rect)[2])
                    print(i, self.preview_canvas.coords(self.rect)[0] + (rect_cords[-1] * i),
                          self.preview_canvas.coords(self.rect)[0] + (rect_cords[-1] * i) / self.crop_factor_y)
                    self.insta_ver_seps.append(self.preview_canvas.create_line(
                        self.preview_canvas.coords(self.rect)[0] + (rect_cords[-1] * i),
                        self.preview_canvas.coords(self.rect)[1],
                        self.preview_canvas.coords(self.rect)[0] + (rect_cords[-1] * i),
                        self.preview_canvas.coords(self.rect)[3],
                        fill=self.rect_color,
                        dash=(2, 2)
                    ))
                    print(self.insta_ver_seps)
                    # try:
                    # print((self.preview_canvas.coords(self.insta_ver_seps[i])))
                    # except Exception as e:
                    #     print(e)

            def upd_infobox_with_tail_pixels_info(event):
                self.update_info_box('Current tail pixel size: %s' % str(round(
                    (self.rect_cords[3] - rect_cords[1]) / self.crop_factor_y)))


            self.preview_canvas.bind('<B3-Motion>', on_move)
            self.preview_canvas.bind('<B1-Motion>', on_resize)
            self.preview_canvas.bind('<ButtonRelease-1>', upd_infobox_with_tail_pixels_info)


            if self.insta_exact_pixels:
                self.preview_canvas.unbind('<B1-Motion>')
                # self.move_corner.destroy()

            self.preview_canvas.grid()



    def get_insta_frame_position(self):
        print('AAW')
        if self.rect:
            print('AAWццц')
            self.insta_start_cut_preview_position_x = self.preview_canvas.coords(self.rect)[0]
            self.insta_start_cut_preview_position_y = self.preview_canvas.coords(self.rect)[1]
            if self.insta_parts_amount or self.insta_exact_pixels:
                print('AAWцвввввцц')
                self.toggle_insta_start_cutting_button()



    def start_insta_cutting(self):
        print('Hello from start cutting')
        print(self.insta_start_cut_preview_position_x)
        print(self.teil_heigh)
        print(self.crop_factor_y)

        self.rect_cords = self.preview_canvas.coords(self.rect)
        self.teil_heigh = self.rect_cords[3] - self.rect_cords[1]

        tail_height_orig = self.teil_heigh / self.crop_factor_y
        print(tail_height_orig, '<--- tail pixels h')

        if not self.insta_start_cut_preview_position_x or not self.insta_start_cut_preview_position_y:
            self.update_info_box('Can not start cutting cause — lack of initial position')

        if self.insta_start_cut_preview_position_x <= 1:
            self.insta_start_cut_original_position_x = 0
        if self.insta_start_cut_preview_position_y <= 1:
            self.insta_start_cut_original_position_y = 0
        # else:
        if self.crop_factor_y:
            # print(self.insta_start_cut_preview_position_x, ' insta cut position x')
            # print(self.crop_factor_x, ' crop factor x')
            # print(int(self.insta_start_cut_preview_position_x / self.crop_factor_x), ' original start pixel x')
            self.insta_start_cut_original_position_x = self.insta_start_cut_preview_position_x / self.crop_factor_y
            self.insta_start_cut_original_position_y = self.insta_start_cut_preview_position_y / self.crop_factor_y
        else:
            return

        tails = []
        if self.insta_start_cut_original_position_x is not None:

            for i in range(0, self.insta_parts_amount):
                print('Processing tail # %d' % i)
                tail_x1 = self.insta_start_cut_original_position_x + i * tail_height_orig
                print('Tail %d: \nX: %s' % (i, tail_x1))
                tail_x2 = self.insta_start_cut_original_position_x + i * tail_height_orig + tail_height_orig
                print('Tail %d: \nX+: %s\n\n' % (
                    # i, self.insta_start_cut_original_position_x + i * tail_height_orig + self.initial_height)
                    i, tail_x2)
                      )
                print('Tail %d: \nY: %s' % (i, self.insta_start_cut_original_position_y +
                                              i * tail_height_orig))
                print('Tail %d: \nY+: %s\n\n' % (
                    i, self.insta_start_cut_original_position_y +
                    i * tail_height_orig + self.initial_height))

                print(tail_height_orig)
                tails.append(self.initial_img.crop(
                    (tail_x1,
                     self.insta_start_cut_original_position_y,
                     tail_x2,
                     self.insta_start_cut_original_position_y + tail_height_orig)
                ))

        for i in range(len(tails)):
            tail = tails[i]
            file = asksaveasfile(
                defaultextension='*.jpg',
                filetypes=[("JPG file", "*.jpg"), ("JPEG file", "*.jpeg")],
                initialfile='%d_part_of_%s.jpg' % (i+1, str(os.path.split(self.initial_file.name)[-1])))
            if file:
                tail.save(file, quality=100, subsampling=0, icc_profile=self.icc_profile)
                self.update_info_box('Tail saved as: %s \n' % file)

    def add_counter_display(self):
        if self.bulk_count_now + 1 <= self.bulk_counter:
            counter = tk.Label(self.root,
                               text="[Image %s of %s ]" % (self.bulk_count_now + 1, self.bulk_counter),
                               font=("Raleway", 9),
                               anchor='se')
            counter.grid(column=0, row=11, sticky='nw', pady=5)

    def calculate_initial_data(self):
        if self.initial_img:
            self.initial_height = self.initial_img.height
            self.initial_width = self.initial_img.width

            self.update_info_box('Initial height: %s px' % self.initial_height)
            self.update_info_box('Initial width : %s px' % self.initial_width)

            im = Image.open(self.initial_file.name)
            self.icc_profile = im.info.get('icc_profile')
            size_mb = len(im.fp.read()) / 1048576
            self.initial_file_mb = size_mb

            self.update_info_box('Initial file size: %s Mb' % str(size_mb)[:4])

    def make_preview(self):

        if self.initial_img:
            self.preview_img = deepcopy(self.initial_img)
            self.preview_img.thumbnail(PREVIEW_SIZE, Image.LANCZOS)
            self.img_prevew_size = self.preview_img.size
            self.img_preview = ImageTk.PhotoImage(self.preview_img)

            try:
                self.place_preview()
            except Exception as e:
                self.update_info_box(e)

    def place_preview(self):
        if self.img_preview:
            preview = self.img_preview
            self.preview_canvas = tk.Canvas(self.root, width=600, height=200,
                                            borderwidth=0, highlightthickness=0)
            self.preview_canvas.create_image(0, 0, image=preview, anchor='nw')
            self.preview_canvas.grid(column=0, row=10, columnspan=2)

    def ask_new_size(self):
        # if self.bulk_files[0] == self.initial_file:
        needed_size_mb = askfloat(
            "Set desirable file size in MBytes",
            "Input needed MBytes amount for file\n %s" % os.path.split(self.initial_file.name)[-1],
            parent=self.root,
            initialvalue="49.9")
        if needed_size_mb:
            self.needed_mb = needed_size_mb
            self.update_info_box('Desirable size of input file: %s Mb' % self.needed_mb)
        else:
            return
        if self.needed_mb >= self.initial_file_mb:
            self.update_info_box('Processing is not needed because the initial file larger than desirable one.')

    def smart_resize(self):
        print('Start resize: %s' % self.initial_file.name)
        if self.initial_img and self.needed_mb:
            self.is_resize_complete = False
            print('Starting process')

            if self.needed_mb > self.initial_file_mb:
                self.update_info_box('Cant enlarge from %s Mb to %s Mb' % (str(self.initial_file_mb)[:4], self.needed_mb))
                return self.add_next_button()

            img = img_orig = Image.open(self.initial_file.name)

            aspect = img.size[0] / img.size[1]
            tolerance = 0
            target_size = self.needed_mb * 1024 * 1024

            att_counter = 0
            while not self.is_resize_complete:
                att_counter += 1
                with io.BytesIO() as buffer:
                    img.save(buffer, format="JPEG", quality=100, subsampling=0, icc_profile=self.icc_profile)
                    data = buffer.getvalue()

                self.filesize = len(data)
                print('Fs at resize: %s' % self.filesize)
                size_deviation = self.filesize / target_size

                self.update_info_box('Attempt # %s\nSize: %s Mbytes, it is x %s of needed size.' %
                                     (att_counter, str(self.filesize/1048576)[:4], str(size_deviation)[:7]))

                if size_deviation <= (100 + tolerance) / 100:
                    # # filesize fits
                    self.candidate_img = img
                    self.result_size = self.candidate_img.size
                    self.add_example_frame()
                    self.update_info_box(
                        'Image processed successfully! \n\n'
                        'You may see proportional '
                        'size of new image marked by red frame. \nClick "Save..." now.\n\n'
                        'New height: %s px \n'
                        'New wight : %s px' % (self.candidate_img.size[0], self.candidate_img.size[1]))
                    self.is_resize_complete = True
                else:
                    # filesize not good enough => adapt width and height
                    # use sqrt of deviation since applied both in width and height
                    new_width = img.size[0] / size_deviation ** 0.5
                    new_height = new_width / aspect
                    # resize from img_orig to not lose quality
                    print('New width: %s' % new_width)
                    print('New height: %s' % new_height)
                    img = img_orig.resize((int(new_width), int(new_height)))

    def add_example_frame(self):
        try:
            print('Result size: ', self.result_size)
            self.crop_factor_x = self.result_size[0] / self.initial_width
            self.crop_factor_y = self.result_size[1] / self.initial_height

            # print(crop_factor_x)
            rec_x, rec_y = self.img_prevew_size[0] * self.crop_factor_x, \
                           self.img_prevew_size[1] * self.crop_factor_y
            print('Rec: ', rec_x, rec_y)

            self.preview_canvas.create_rectangle(1, 1,
                                                 rec_x, rec_y,
                                                 outline='red',
                                                 width=2)
            self.preview_canvas.grid()
        except Exception as e:
            self.update_info_box(e)

    def save_process(self):

        def save_file(self):
            print('Fs: %s' % self.filesize)
            print('name at save: %s ' % self.initial_file.name)
            file = asksaveasfile(
                defaultextension='*.jpg',
                filetypes=[("JPG file", "*.jpg"), ("JPEG file", "*.jpeg")],
                initialfile=self.initial_file.name.replace(
                    '.jpg', '_resized_to_%s_Mb.jpg' % str(self.filesize/1048576).replace('.', ',')[:4]))
            if file:
                self.candidate_img.save(file, quality=100, subsampling=0, icc_profile=self.icc_profile,
                                        )
                self.update_info_box('File saved:\n%s\n' % file.name)
                if self.bulk_mode:
                    self.add_next_button()
            else:
                self.add_next_button()
                return

        if self.is_resize_complete:
            save_text = tk.StringVar()
            save_btn = tk.Button(self.root, textvariable=save_text,
                                 font="Raleway",
                                 command=lambda: save_file(self))
            save_text.set("Save...")
            save_btn.grid(column=2, row=10, sticky='sw')

    def add_next_button(self):

        def press_next_button(self):
            self.is_next_button_pressed = True
            print(self.is_next_button_pressed)
            if self.bulk_count_now < self.bulk_counter:
                self.bulk_count_now += 1
                self.start()

        next_btn_text = tk.StringVar()
        next_btn = tk.Button(self.root, textvariable=next_btn_text,
                             font="Raleway",
                             command=lambda: press_next_button(self))
        next_btn_text.set("Next")
        next_btn.grid(column=2, row=10, sticky='N', pady=30)

    def toggle_settings(self):
        if self.is_settings_opened:
            # self.settings_ver_sep.destroy()
            self.settings_frame.destroy()
            self.master_column_number -= 3
            self.is_settings_opened = False
        else:
            self.master_column_number += 3
            self.is_settings_opened = True

            self.create_settings()

    def create_settings(self):

        self.settings_frame = tk.LabelFrame(self.root,
                                            width=250, height=CANVAS_SIZE[0],
                                            borderwidth=2)
        self.settings_frame.grid(column=self.master_column_number - 2,
                                 row=2,
                                 rowspan=11,
                                 sticky='snw',
                                 pady=5)

        bulk_separ = Separator(master=self.settings_frame, orient='horizontal')
        bulk_separ.grid(column=self.master_column_number - 2, row=7, sticky="we",
                        columnspan=3)

        bulk_separ2 = Separator(master=self.settings_frame, orient='horizontal')
        bulk_separ2.grid(column=self.master_column_number - 2, row=8, sticky="we",
                        columnspan=3)


        # for row in range(self.master_row_nubmer):
        #     self.settings_frame.rowconfigure(row, minsize=13)
        self.add_setting_set_resizable_frame()
        self.add_setting_set_exact_pixels_size()
        self.add_setting_butch_keep_size_radio()
        self.add_setting_insta_cut_tails_amount()

    def add_setting_set_exact_pixels_size(self):

        def ask_exact_pixels_size():
            needed_pixels_amount = askinteger(
                "Set desirable squerq size in pixels",
                "Input: ",
                parent=self.settings_frame,
                initialvalue="1080")
            if not needed_pixels_amount:
                return
            else:
                self.insta_exact_pixels = needed_pixels_amount
                self.calculate_insta_data()
                self.toggle_insta_start_cutting_button()

        self.settings_ask_exact_pixels_button = tk.Button(self.settings_frame,
                                                          text='Set pixels',
                                                          command=lambda: ask_exact_pixels_size(),
                                                          font=("Raleway", 10),
                                                          height=1
                                                          )
        if self.insta_exact_pixels:
            try:
                self.settings_ask_exact_pixels_button['state'] = 'disabled'
            except Exception as e:
                print('e!: %s' % e)

        if self.initial_img and self.insta_parts_amount:
            self.settings_ask_exact_pixels_button.grid(column=self.master_column_number-1,
                                                       row=9,
                                                       sticky='s',
                                                       pady=5
                                                       )

    def add_setting_set_resizable_frame(self):

        def set_resizable_frame():
            self.insta_exact_pixels = None
            self.calculate_insta_data()
            self.toggle_insta_start_cutting_button()


        self.settings_resizable_frame_button = tk.Button(self.settings_frame,
                                                          text='Resize',
                                                          command=lambda: set_resizable_frame(),
                                                          font=("Raleway", 10),
                                                          height=1
                                                          )

        if not self.insta_exact_pixels:
            try:
                self.settings_resizable_frame_button['state'] = 'disabled'
            except Exception as e:
                print('e!: %s' % e)

        if self.initial_img and self.insta_parts_amount:
            self.settings_resizable_frame_button.grid(column=self.master_column_number-2,
                                                      row=9,
                                                      sticky='s',
                                                      pady=5,
                                                      padx=5
                                                      )




    def add_setting_butch_keep_size_radio(self):

        def ask_default_size():
            needed_size_mb = askfloat(
                "Set desirable file size in MBytes",
                "Input for all files in bulk",
                parent=self.settings_frame,
                initialvalue="49.9")
            if not needed_size_mb:
                return
            else:
                self.butch_size_default = needed_size_mb
                add_default_size_mb_lable()

        self.settings_butch_size_radio_var = tk.IntVar()
        self.settings_butch_size_radio_var.set(1)  # set default as default

        self.settings_butch_size_mode = tk.StringVar(None, 'default')

        self.settings_ask_default_value_btn = tk.Button(self.settings_frame,
                                                        text='Set size',
                                                        command=lambda: ask_default_size(),
                                                        font=("Raleway", 10),
                                                        height=1
                                                        )

        def set_butch_size_ask_each_time():
            self.settings_butch_size_mode.set('each_time')
            butch_size_radio_ask_each.setvar('value', 1)
            butch_size_radio_set_def.setvar('value', 0)
            print(self.settings_butch_size_mode.get())
            if self.settings_ask_default_value_btn:
                self.settings_ask_default_value_btn.destroy()
            if self.settings_def_size_lbl:
                self.settings_def_size_lbl.destroy()

        def set_butch_size_set_default():
            self.settings_butch_size_mode.set('default')
            butch_size_radio_set_def.setvar('value', 1)
            butch_size_radio_ask_each.setvar('value', 0)
            add_ask_size_button()
            add_default_size_mb_lable()

        def add_default_size_mb_lable():
            # print('def lable')
            # print(self.butch_size_default)
            if self.butch_size_default and self.settings_butch_size_mode.get() == 'default':
                self.settings_def_size_lbl = tk.Label(self.settings_frame,
                                        text='Now: %s' % self.butch_size_default,
                                        font=("Raleway", 9, 'bold'),
                                        bg='brown')
                self.settings_def_size_lbl.grid(column=self.master_column_number, row=4, sticky="ns",
                                  pady=0)

        def add_ask_size_button():
            self.settings_ask_default_value_btn = tk.Button(self.settings_frame,
                                                            text='Set size',
                                                            command=lambda: ask_default_size(),
                                                            font=("Raleway", 10),
                                                            height=1
                                                            )
            self.settings_ask_default_value_btn.grid(column=self.master_column_number,
                                                     row=6,
                                                     sticky='s',
                                                     pady=5
                                                     )

        add_default_size_mb_lable()
        add_ask_size_button()

        butch_size_radio_ask_each = tk.Radiobutton(self.settings_frame,
                                                   text='Ask each photo',
                                                   variable=self.settings_butch_size_radio_var,
                                                   command=set_butch_size_ask_each_time,
                                                   value=0,
                                                   # tristatevalue="each_time",
                                                   # height=1
                                                   )
        butch_size_radio_set_def = tk.Radiobutton(self.settings_frame,
                                                  text='Set default',
                                                  variable=self.settings_butch_size_radio_var,
                                                  command=set_butch_size_set_default,
                                                  value=1,
                                                  # tristatevalue="",
                                                  # height=1,
                                                  bg='yellow')
        butch_size_radio_ask_each.grid(column=self.master_column_number-1,
                                       row=3, sticky='nw', pady=5)
        butch_size_radio_set_def.grid(column=self.master_column_number,
                                      # row=3, sticky='nw', pady=20)
                                      row=3, sticky='nw', pady=5)

    def add_setting_insta_cut_tails_amount(self):

        if self.initial_img:
            self.settings_insta_tails_amount = tk.IntVar()
            self.settings_insta_tails_amount.set(INSTA_CUT_DEFAULT_TAILS_AMOUNT)

            max_tails_amount_x = int(self.initial_width / INSTA_CUT_MINIMUM_TAIL_SIZE_PX)
            print('Max tails amount in row: %s' % max_tails_amount_x)

            tails_list = [x for x in range(3, max_tails_amount_x+1)]


            # tails_list = INSTA_CUT_DEFAULT_TAILS_VARIANTS[:max_tails_amount_x]

            self.settings_insta_tails_drop = Combobox(self.settings_frame,
                                                      values=tails_list,
                                                      width=3,
                                                      # postcommand=lambda: print(self.settings_insta_tails_amount.set(
                                                      #     self.settings_insta_tails_drop.get()))
                                                      # postcommand=self.calculate_insta_data,
                                                      )
            self.settings_insta_tails_drop.grid(column=self.master_column_number,
                                                row=9, sticky='nw', pady=5)
            # if self.settings_insta_tails_drop.get():
            self.settings_insta_tails_drop.current(0)
            print(self.settings_insta_tails_amount.get())
            print(self.initial_width)

            def set_dropbox_amount(event):
                self.settings_insta_tails_amount.set(self.settings_insta_tails_drop.get())
                self.calculate_insta_data()
                print(self.settings_insta_tails_drop.get())

            self.settings_insta_tails_drop.bind(
                "<<ComboboxSelected>>", set_dropbox_amount)
            # print(self.settings_insta_tails_drop.current(), self.settings_insta_tails_drop.get())
        else:
            return


    def show_startup(self):
        text = 'Hi!\n' \
               'Default size for output files is %s Mb now.\n' \
               'You could change it in settings.\n' % self.butch_size_default
        self.update_info_box(text)



    def app(self):
        self.root = tk.Tk()
        self.root.title('PanResizer by @world_of_distortion')

        self.create_canvas()
        self.add_instructions()
        self.add_logo()
        self.add_open_button()
        self.add_bulk_open_button()
        self.add_folder_open_button()

        self.add_insta_cutter_button()
        # self.add_insta_start_cutting_button()
        # self.toggle_insta_start_cutting_button()


        self.add_info_box()
        # self.calculate_initial_data()

        self.add_settings_button()

        self.show_startup()

        self.root.mainloop()




# class SettingsWindow(tk.Toplevel):
#
#     def __init__(self, master=None):
#         # tk.Toplevel.__init__(self, master)
#         super(SettingsWindow, self).__init__(master=master)
#         self.master_window = master
#         self.settings_window = self
#         self.settings_window.wm_title("Settings")
#         self.master_window.title("AUE")
#         print(dir(self.master_window))
#         # print(self.master_window.root)
#         # print(master.logo_label.get(self))
#         # a = self.root()
#         # print(self.logo_label)
#
#         self.settings_window.wm_geometry("300x300")
#         settings_frame = tk.Frame(master)
#
#         self.settings_canvas = tk.Canvas(settings_frame, height=200, width=300)
#         self.wm_geometry()
#         self.settings_exit_button = tk.Button(
#             self, text="Exit", highlightbackground="#56B426", command=self.destroy)
#         self.settings_exit_button.grid(column=2, row=2, sticky='ne')
#         # print(self.canvas.title)
#         self.settings_canvas.grid(column=3, row=3)



if __name__ == "__main__":
    resizer = PanResizer()
    resizer.app()