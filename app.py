import tkinter as tk

from copy import deepcopy

from time import sleep

from tkinter.simpledialog import askfloat
from tkinter.filedialog import askopenfile, asksaveasfile, askopenfiles, askdirectory

from tkinter.ttk import Separator
from PIL import Image, ImageTk
from PIL.Image import DecompressionBombError

import io
import os


CANVAS_SIZE = (600, 300)
PREVIEW_SIZE = (600, 300)

Image.MAX_IMAGE_PIXELS = None

class PanResizer(object):
    def __init__(self):
        self.initial_file_path = None
        self.initial_file = None
        self.initial_img = None
        self.logo_label = None
        self.img_preview = None
        self.initial_file_mb = None
        # self.log = []
        self.needed_mb = None
        self.icc_profile = None
        self.candidate_img = None
        # self.cand_size_mb = None
        # self.cand_percentage = None
        self.preview_canvas = None
        self.result_size = None
        self.bulk_mode = None
        self.bulk_files = None
        self.is_resize_complete = None
        # self.is_cand_save_complete = None
        self.filesize = None
        # self.can_process_next_file = None
        self.bulk_counter = None
        self.bulk_count_now = None
        self.is_next_button_pressed = False

        self.insta_start_cut_original_position_x = None


    def create_canvas(self):

        frame = tk.Frame(self.root, padx=0, pady=10, width=CANVAS_SIZE[0])

        self.canvas = tk.Canvas(frame, height=CANVAS_SIZE[0], width=CANVAS_SIZE[1])
        self.canvas.grid(column=2, row=11)

    def add_settings_button(self):

        self.settings_btn_text = tk.StringVar()
        self.settings_btn = tk.Button(self.root, textvariable=self.settings_btn_text,
                                    font="Raleway",
                                    command=lambda: SettingsWindow(self.root))
        self.settings_btn_text.set("Settings")
        self.settings_btn.grid(column=0, row=0)


    def add_logo(self):
        logo = Image.open('logo.jpg')
        logo = ImageTk.PhotoImage(logo)
        logo_label = tk.Label(self.root, image=logo, height=200, anchor='center')
        logo_label.image = logo
        logo_label.grid(column=1, row=0)


    def add_instructions(self):
        instructions = tk.Label(self.root, text="Select JPG to resize", font="Raleway")
        instructions.grid(column=0, row=1)
        instructions2 = tk.Label(self.root, text="Select several JPGs to resize", font="Raleway")
        instructions2.grid(column=0, row=3)
        instructions3 = tk.Label(self.root, text="Select folder to process all JPGs", font="Raleway")
        instructions3.grid(column=0, row=5)
        instructions4 = tk.Label(self.root, text="Select JPG for instagram cutting", font="Raleway")
        instructions4.grid(column=0, row=8)

    def add_open_button(self):

        self.browse_text = tk.StringVar()
        self.browse_btn = tk.Button(self.root, textvariable=self.browse_text,
                                    font="Raleway",
                                    command=lambda: self.open_file())
        self.browse_text.set("Browse...")
        lbl_frame = Separator(master=self.root, orient='horizontal')
        # lbl_frame.grid(column=0, row=2, sticky="we", columnspan=3, ipadx=300, pady=5)
        lbl_frame.grid(column=0, row=2, sticky="we", columnspan=3, pady=5)
        self.browse_btn.grid(column=1, row=1)

    def add_bulk_open_button(self):

        self.bulk_browse_text = tk.StringVar()
        self.bulk_browse_btn = tk.Button(self.root, textvariable=self.bulk_browse_text,
                                         font="Raleway",
                                         command=lambda: self.open_bulk_files(),
                                         anchor='center')
        self.bulk_browse_text.set("Browse several...")
        lbl_frame2 = Separator(master=self.root, orient='horizontal')
        lbl_frame2.grid(column=0, row=4, sticky="we", columnspan=3)
        self.bulk_browse_btn.grid(column=1, row=3, pady=5, sticky='n')

    def add_folder_open_button(self):
        self.fldr_browse_text = tk.StringVar()
        self.fldr_browse_btn = tk.Button(self.root, textvariable=self.fldr_browse_text,
                                         font="Raleway",
                                         command=lambda: self.open_folder(),
                                         anchor='center')
        self.fldr_browse_text.set("Select folder...")
        lbl_frame3 = Separator(master=self.root, orient='horizontal')
        lbl_frame3.grid(column=0, row=6, columnspan=3, sticky="we")
        lbl_frame4 = Separator(master=self.root, orient='horizontal')
        lbl_frame4.grid(column=0, row=7, columnspan=3, sticky="we")
        self.fldr_browse_btn.grid(column=1, row=5, pady=5, sticky='n')

    def add_insta_cutter_button(self):
        self.insta_cutter_open_btn_text = tk.StringVar()
        self.insta_cutter_open_btn = tk.Button(self.root,
                                               textvariable=self.insta_cutter_open_btn_text,
                                               font="Raleway",
                                               command=lambda: self.open_insta_cutter(),
                                               anchor='center')
        self.insta_cutter_open_btn_text.set("Browse file")
        self.insta_cutter_open_btn.grid(column=1, row=8, pady=6, sticky='n')

    def add_insta_start_cutting_button(self):
        self.insta_start_cutting_btn_text = tk.StringVar()
        self.insta_start_cutting_btn = tk.Button(self.root,
                                                 textvariable=self.insta_start_cutting_btn_text,
                                                 font="Raleway",
                                                 command=lambda: self.start_insta_cutting(),
                                                 anchor='center')
        self.insta_start_cutting_btn_text.set("Start cutting")
        # lbl_frame3 = Separator(master=self.root, orient='horizontal')
        # lbl_frame3.grid(column=0, row=6, columnspan=3, sticky="we")
        self.insta_start_cutting_btn.grid(column=2, row=8, sticky='w')


    def add_info_box(self):
        self.info_box = tk.Text(self.root, height=20, width=65, padx=20, font=("Raleway", 10))
        self.info_box.grid(columnspan=2, column=0, row=11)

    def update_info_box(self, message):
        self.info_box.insert(1.0, '\n\n%s' % message)



    def open_file(self):
        file = tk.filedialog.askopenfile(title="Choose a file",
                                         filetype=[("JPG file", "*.jpg"),
                                                   ("JPEG file", "*.jpeg")]
                                         )
        self.bulk_mode = False
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
        self.bulk_mode = True

        self.initial_file = None
        self.initial_img = None
        self.initial_file_path = None

        if files:
            print(files)
            self.bulk_files = files
            print(self.bulk_files)
            self.update_info_box('Files are opened:\n %s' % [f.name for f in self.bulk_files])
            self.bulk_counter = len(self.bulk_files)
            self.bulk_count_now = 0

            self.start()


    def open_folder(self):

        from tkinter.filedialog import Open

        folder_path = tk.filedialog.askdirectory(title="Choose folder to process all images")

        files = []
        if folder_path:

            folder_files = os.listdir(folder_path)

            for f in folder_files:
                f = io.TextIOWrapper(open((os.sep.join([folder_path, f]))))
                files.append(f)

            self.bulk_mode = True

            self.initial_file = None
            self.initial_img = None
            self.initial_file_path = None

            self.bulk_files = files
            self.bulk_count_now = 0
            self.bulk_counter = len(self.bulk_files)

            self.start()

    def open_insta_cutter(self):
        file = tk.filedialog.askopenfile(title="Choose a file",
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
                self.initial_photo_img = ImageTk.PhotoImage(self.initial_img)

                self.update_info_box(str('---' * 35) + '\n')
                if self.bulk_mode:
                    self.update_info_box("[Image %s of %s ]" % (self.bulk_count_now + 1, self.bulk_counter))
                self.update_info_box('Starting processing file:\n%s' % f.name)
                self.calculate_initial_data()
                self.make_preview()
                self.ask_new_size()
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
        self.initial_photo_img = None

        if self.initial_file:
            # try:
            self.initial_img = Image.open(self.initial_file.name)

            self.initial_photo_img = ImageTk.PhotoImage(self.initial_img)

            self.update_info_box('File opened for cutting:\n%s' % self.initial_file.name)

            self.calculate_initial_data()
            self.make_preview()

            self.calculate_insta_data()
        else:
            return

    def calculate_insta_data(self):

        if self.initial_img:
            if not self.initial_width or not self.initial_height:
                self.calculate_initial_data()

            self.insta_parts_amount = int(self.initial_width / self.initial_height)
            if self.insta_parts_amount < 3:
                self.update_info_box('The weidth of image is not lareger than 3 x heighgt.\n'
                                     'Aborting.')

                return
            else:
                self.update_info_box('The image could be cutted into %s square parts.'
                                     % self.insta_parts_amount)
                self.add_responsive_frame()

    def add_responsive_frame(self):
        # import pyautogui

        def on_move(event):
            component = event.widget
            # print(component)
            # locx, locy = component.winfo_x(), component.winfo_y()
            # w, h = self.root.winfo_width(), self.root.winfo_height()
            # mx, my = component.winfo_width(), component.winfo_height()
            # xpos = (locx + event.x) - (15)
            # ypos = (locy + event.y) - int(my / 2)
            # if xpos >= 0 and ypos >= 0 and w - abs(xpos) >= 0 and h - abs(
            #         ypos) >= 0 and xpos <= w - 5 and ypos <= h - 5:
            #     component.coords(x=xpos, y=ypos)

            # print(event.x, event.y)
            # print(rect_middle_point_x, rect_middle_point_y)

            x1, y1, x2, y2 = (round(event.x - rect_middle_point_x),
                              round(event.y - rect_middle_point_y),
                              round(event.x + rect_middle_point_x),
                              round(event.y + rect_middle_point_y))

            print('Rect coords: %s' % str(self.preview_canvas.coords(self.rect)))
            # print('CD: %s' % str(self.preview_img.size[0]))

            if x1 >= -0.0 and x2 <= self.preview_img.size[0]:

                # draw rect
                self.preview_canvas.coords(self.rect, x1, 0, x2, self.img_prevew_size[1])

                # draw central pint
                self.preview_canvas.coords(self.touch_center,
                                           event.x-5,
                                           self.img_prevew_size[1]/2 - 5,
                                           event.x+5,
                                           self.img_prevew_size[1]/2 + 5)
                print(self.preview_canvas.coords(self.rect))

                # move vert separs
                # print('Seps at move: %s' % str(self.ver_seps))
                for i in range(1, len(self.ver_seps)+1):
                    self.preview_canvas.coords(
                        self.ver_seps[i-1],
                        self.preview_canvas.coords(self.rect)[0] + (rect_cords[-1] * i),
                        self.preview_canvas.coords(self.rect)[1],
                        self.preview_canvas.coords(self.rect)[0] + (rect_cords[-1] * i),
                        self.preview_canvas.coords(self.rect)[3],
                    )

                self.get_insta_frame_position()

        if not self.initial_img or not self.insta_parts_amount:
            return
        else:
            print('Preview size: %s' % str(self.img_prevew_size))

            self.crop_factor_x = self.img_prevew_size[0] / self.initial_width
            self.crop_factor_y = self.img_prevew_size[1] / self.initial_height

            rec_x = self.img_prevew_size[1] * self.insta_parts_amount
            rec_y = self.img_prevew_size[1]
            print('Rec: ', rec_x, rec_y)
            #
            self.rect = self.preview_canvas.create_rectangle(1, 1,
                                                 rec_x, rec_y,
                                                 outline='red',
                                                 width=1)
            rect_cords = self.preview_canvas.coords(self.rect)
            print('Rect coords: %s' % rect_cords)

            rect_middle_point_x = rect_cords[2] / 2
            rect_middle_point_y = rect_cords[3] / 2

            self.touch_center = self.preview_canvas.create_oval(rect_middle_point_x-5,
                                                                rect_middle_point_y-5,
                                                                rect_middle_point_x+5,
                                                                rect_middle_point_y+5,
                                                                outline='red',
                                                                width=1)
            # create vertical lines:
            self.ver_seps = []
            for i in range(1, self.insta_parts_amount):
                print(self.insta_parts_amount, ' parts')
                print(self.preview_canvas.coords(self.rect)[2])
                print(i, self.preview_canvas.coords(self.rect)[0] + (rect_cords[-1] * i))
                self.ver_seps.append(self.preview_canvas.create_line(
                    self.preview_canvas.coords(self.rect)[0] + (rect_cords[-1] * i),
                    self.preview_canvas.coords(self.rect)[1],
                    self.preview_canvas.coords(self.rect)[0] + (rect_cords[-1] * i),
                    self.preview_canvas.coords(self.rect)[3],
                    fill='red',
                    dash=(2, 2)
                ))
                try:
                    print((self.preview_canvas.coords(self.ver_seps[i])))
                except Exception as e:
                    print(e)
            self.preview_canvas.bind('<B1-Motion>', on_move)

            self.preview_canvas.grid()

            # self.get_insta_frame_position()

    def get_insta_frame_position(self):
        if self.rect:
            self.insta_start_cut_preview_position_x = self.preview_canvas.coords(self.rect)[0]
            self.add_insta_start_cutting_button()

    def start_insta_cutting(self):
        if self.insta_start_cut_preview_position_x < 1:
            self.insta_start_cut_original_position_x = 0
        # else:
        if self.crop_factor_x:
            print(self.insta_start_cut_preview_position_x, ' insta cut position x')
            print(self.crop_factor_x, ' crop factor x')
            print(int(self.insta_start_cut_preview_position_x / self.crop_factor_x), ' original start pixel x')
            self.insta_start_cut_original_position_x = int(
                self.insta_start_cut_preview_position_x / self.crop_factor_x)
        else:
            return

        tails = []
        if self.insta_start_cut_original_position_x is not None:
            # print(self.initial_img.size)
            for i in range(0, self.insta_parts_amount):
                print('Processing tail # %d' % i)

                print('Tail %d: \nX: %s\n' % (i, self.insta_start_cut_original_position_x +
                                            i * self.initial_height))
                print('Tail %d: \nX+: %s\n\n' % (
                    i, self.insta_start_cut_original_position_x +
                    i * self.initial_height + self.initial_height))
                # print('Tail %d:\n'
                #       'X: %s\n'
                #       'Y: %s\n'
                #       'X+widht: %s\n'
                #       'Y+width: %s' % (i,
                #                    self.insta_start_cut_original_position_x * i,
                #                    0,
                #                    (self.insta_start_cut_original_position_x +
                #                     self.preview_canvas.coords(self.rect)[-1]) * i,
                #                    self.preview_canvas.coords(self.rect)[-1]
                #                    ))
                # print('Tail: ',
                #       (i* self.insta_start_cut_original_position_x,
                #        0,
                #        self.insta_start_cut_original_position_x + (
                #                i * self.initial_width / self.insta_parts_amount),
                #        self.initial_width / self.insta_parts_amount)
                #       )
                # # try:

                # tails.append(self.initial_img.crop(
                #     (i *self.insta_start_cut_original_position_x,
                #     0,
                #     self.insta_start_cut_original_position_x + (i * self.initial_width / self.insta_parts_amount),
                #     self.initial_width / self.insta_parts_amount)
                # ))

                tails.append(self.initial_img.crop(
                    (self.insta_start_cut_original_position_x + i * self.initial_height,
                     0,
                     self.insta_start_cut_original_position_x +
                     i * self.initial_height + self.initial_height,
                     self.initial_height)
                ))

                # except Exception as e:
                #     print(e)
            # print(tails)

        for i in range(len(tails)):
            tail = tails[i]
            file = asksaveasfile(
                defaultextension='*.jpg',
                filetypes=[("JPG file", "*.jpg"), ("JPEG file", "*.jpeg")],
                initialfile='%d_part_of_%s.jpg' % (i+1, str(os.path.split(self.initial_file.name)[-1])))
            if file:
                tail.save(file, quality=100, subsampling=0, icc_profile=self.icc_profile)




    def add_counter_display(self):
        if self.bulk_count_now + 1 <= self.bulk_counter:
            counter = tk.Label(self.root,
                               text="[Image %s of %s ]" % (self.bulk_count_now + 1, self.bulk_counter),
                               font=("Raleway", 9),
                               anchor='se')
            counter.grid(column=2, row=11, rowspan=2, sticky='N')


    def calculate_initial_data(self):
        print(self.initial_img)
        if self.initial_img:
            self.initial_height = self.initial_img.height
            self.initial_width = self.initial_img.width

            self.update_info_box('Initial height: %s px' % self.initial_height)
            self.update_info_box('Initial width : %s px' % self.initial_width)

            im = Image.open(self.initial_file.name)
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
            self.preview_canvas = tk.Canvas(self.root, width=600, height=300,
                                            borderwidth=0, highlightthickness=0)
            self.preview_canvas.create_image(0, 0, image=preview, anchor='nw')
            self.preview_canvas.grid(column=0, row=10, columnspan=3)


    def ask_new_size(self):

        if self.bulk_files[0] == self.initial_file:
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
            # self.log.append(e)
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
                self.candidate_img.save(file, quality=100, subsampling=0, icc_profile=self.icc_profile)
                # self.can_process_next_file = tk.IntVar()
                # self.can_process_next_file.set(1)
                self.update_info_box('File saved:\n%s\n' % file.name)
                if self.bulk_mode:
                    self.add_next_button()
            else:
                self.add_next_button()
                return

        if self.is_resize_complete:
            self.save_text = tk.StringVar()
            self.save_btn = tk.Button(self.root, textvariable=self.save_text,
                                      font="Raleway",
                                      command=lambda: save_file(self))
            self.save_text.set("Save...")
            self.save_btn.grid(column=2, row=11)



    def add_next_button(self):
        print('Add next button')
        def press_next_button(self):
            self.next_btn_pressed_var.set(1)
            self.next_btn_pressed_var.get()
            # print(self.is_next_button_pressed)
            # print(self.bulk_count_now)
            # print(self.bulk_counter)

            self.is_next_button_pressed = True
            self.bulk_count_now += 1

            self.start()


        self.next_btn_pressed_var = tk.IntVar()

        self.next_btn_text = tk.StringVar()
        self.next_btn = tk.Button(self.root, textvariable=self.next_btn_text,
                                  font="Raleway",
                                  command=lambda: press_next_button(self))
        self.next_btn_text.set("Next")
        self.next_btn.grid(column=2, row=11, sticky='N', pady=30)

        # print('aue')
        # print(self.next_btn_pressed_var.get())



        # self.next_btn.wait_variable(self.next_btn_pressed_var)





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

        # self.process()

        self.add_info_box()
        # self.calculate_initial_data()

        self.add_settings_button()

        self.root.mainloop()


class SettingsWindow(tk.Toplevel):

    def __init__(self, master=None):
        # tk.Toplevel.__init__(self, master)
        super(SettingsWindow, self).__init__(master=master)
        self.master_window = master
        self.settings_window = self
        self.settings_window.wm_title("Settings")
        self.master_window.title("AUE")
        print(dir(self.master_window))
        # print(self.master_window.root)
        # print(master.logo_label.get(self))
        # a = self.root()
        # print(self.logo_label)

        self.settings_window.wm_geometry("300x300")
        settings_frame = tk.Frame(master)

        self.settings_canvas = tk.Canvas(settings_frame, height=200, width=300)
        self.wm_geometry()
        self.settings_exit_button = tk.Button(
            self, text="Exit", highlightbackground="#56B426", command=self.destroy)
        self.settings_exit_button.grid(column=2, row=2, sticky='ne')
        # print(self.canvas.title)
        self.settings_canvas.grid(column=3, row=3)



if __name__ == "__main__":
    resizer = PanResizer()
    resizer.app()