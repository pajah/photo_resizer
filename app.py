import tkinter as tk

from tkinter.simpledialog import askfloat
from tkinter.filedialog import askopenfile, asksaveasfile

from tkinter.ttk import Separator
from PIL import Image, ImageTk

import io

class PanResizer(object):
    def __init__(self):
        self.initial_file_path = None
        self.initial_file = None
        self.initial_img = None
        self.logo_label = None
        self.img_preview = None
        self.initial_file_mb = None
        self.log = []
        self.needed_mb = None
        self.icc_profile = None
        self.candidate_img = None
        self.cand_size_mb = None
        self.cand_percentage = None
        self.preview_canvas = None


    def open_file(self):
        file = tk.filedialog.askopenfile(title="Open file")
        if file:
            img = Image.open(file.name)
            self.initial_file = file
            self.initial_img = ImageTk.PhotoImage(img)
            self.icc_profile = img.info.get('icc_profile')

            # with open(file.name, 'r') as f:
            #     im = Image.open(f)
            # print(im)
            #     # im = Image.open(readed)
            #     print(readed)

            print('Open file size: ', img.size)

            self.initial_height = img.height
            self.initial_width = img.width
            # self.initial_file_mb = len(img.fp.read()) / 1048576

            img.thumbnail((600, 300), Image.LANCZOS)
            self.img_prevew_size = img.size
            self.img_preview = ImageTk.PhotoImage(img)

            self.log.append('File opened')


        self.add_info_box()
        # self.open_image()
        self.open_image2()
        self.calculate_initial_data()

    def create_canvas(self):
        self.canvas = tk.Canvas(self.root, height=600, width=300)
        self.canvas.grid(column=2, row=4)


    def add_logo(self):
        logo = Image.open('logo.jpg')
        logo = ImageTk.PhotoImage(logo)
        logo_label = tk.Label(self.root, image=logo, height=300)
        logo_label.image = logo
        # print(logo_label)
        logo_label.grid(column=1, row=0)


    # @staticmethod
    def add_instructions(self):
        instructions = tk.Label(self.root, text="Select JPG to resize", font="Raleway")
        instructions.grid(column=0, row=1)

    def add_open_button(self):

        self.browse_text = tk.StringVar()
        self.browse_btn = tk.Button(self.root, textvariable=self.browse_text,
                                    font="Raleway",
                                    command=lambda: self.open_file())
        self.browse_text.set("Browse...")
        lbl_frame = Separator(master=self.root, orient='horizontal')
        lbl_frame.grid(column=0, row=2, sticky="we", columnspan=3, ipadx=300, pady=15)
        self.browse_btn.grid(column=1, row=1)


    def add_info_box(self):
        self.info_box = tk.Text(self.root, height=20, width=50)
        for _ in self.log:
            self.info_box.insert(1.0, _)
            self.info_box.insert(1.0, '\n')
            self.info_box.insert(1.0, '\n')

        self.info_box.grid(columnspan=2, column=0, row=4)

    def open_image(self):
        if self.img_preview:
            print('!')
            preview = self.img_preview
            self.preview_label = tk.Label(self.root, image=preview)
            self.preview_label.image = preview
            # self.preview_label
            # print(logo_label)
            self.preview_label.grid(column=0, row=2, columnspan=3)

    def open_image2(self):
        if self.img_preview:
            print('!')
            preview = self.img_preview
            # self.preview_canvas = tk.Canvas(self.root, width=600, height=300)
            self.preview_canvas = tk.Canvas(self.root, width=600, height=200,
                                            borderwidth=0, highlightthickness=0)
            self.preview_canvas.create_image(0, 0, image=preview, anchor='nw')
            # self.preview_label = tk.Label(self.root, image=preview)
            # self.preview_label.image = preview
            # self.preview_label
            # print(logo_label)
            self.preview_canvas.grid(column=0, row=3, columnspan=3)



    def calculate_initial_data(self):
        # pass
        if self.initial_img:
            self.log.append('Height: %s px' % self.initial_height)
            self.log.append('Width : %s px' % self.initial_width)
            self.add_info_box()

            self.create_candidate()


    def create_candidate(self):
        if self.initial_file:
            im = Image.open(self.initial_file.name)
            size_mb = len(im.fp.read()) / 1048576
            # print(size_mb)
            self.initial_file_mb = size_mb
            self.log.append('Initial file size: %s Mb' % str(size_mb)[:4])
            self.add_info_box()

            self.ask_new_size()

    def ask_new_size(self):
        needed_size_mb = askfloat("Set desirable file size in MBytes",
                                  "Input needed MBytes amount: \n",
                                  parent=self.root,
                                  initialvalue="49.9")
        self.needed_mb = needed_size_mb
        self.log.append('Desirable size of input file: %s' % self.needed_mb)
        if self.needed_mb >= self.initial_file_mb:
            self.log.append('Processing is not needed because the initial file larger than desirable one.')
        self.add_info_box()
        self.process()

    def process(self):
        if self.initial_img and self.needed_mb:
            print('Starting process')

            if self.needed_mb > self.initial_file_mb:
                self.log.append('Cant enlarge')
                self.add_info_box()
                return

            # value = int(self.needed_mb)
            #
            # rng = range(10, 100)
            # low = rng[0]
            # high = rng[-1]
            # mid = len(rng) // 2
            #
            # img = Image.open(self.initial_file.name)
            #
            # i = 0
            # while low < high:
            #     i += 1
            #     img = Image.open(self.initial_file.name)
            #     new_im = img.resize((int(img.width * mid * 0.01), int(img.height * mid * 0.01)), Image.ANTIALIAS)
            #     new_im.save("cand.jpg", format='JPEG', quality=100, subsampling=0, icc_profile=self.icc_profile)
            #     img.close()
            #
            #     cand_size_mb = 0
            #     cand = Image.open("cand.jpg")
            #     print(cand.format)
            #     cand_size_mb = len(cand.fp.read()) / 1048576
            #     cand.close()
            #
            #     if cand_size_mb < value:
            #         low = mid + 1
            #     else:
            #         high = mid - 1
            #
            #     mid = (low + high) // 2
            #
            #     self.log.append('Attempt %s\n'
            #                     'Trying %s percent of initial file:\n'
            #                     'MB file result: %s\n' % (str(i), str(mid), str(cand_size_mb)[:4]))
            #     self.log.append('---' * 20)
            #
            #     self.cand_percentage = mid
            #     self.cand_size_mb = cand_size_mb
            #
            #     self.candidate_img = cand
            #     self.add_info_box()
            #
            #     if self.cand_percentage and self.cand_size_mb and self.candidate_img:
            #         self.save_process()
            # print('Last mid: %s' % mid)
            # print('Last size: %s' % str(cand_size_mb))

            img = img_orig = Image.open(self.initial_file.name)

            aspect = img.size[0] / img.size[1]
            tolerance = 0
            target_size = self.needed_mb * 1024 * 1024

            att_counter = 0
            while True:

                att_counter += 1
                with io.BytesIO() as buffer:
                    img.save(buffer, format="JPEG", quality=100, subsampling=0, icc_profile=self.icc_profile)
                    data = buffer.getvalue()

                filesize = len(data)
                size_deviation = filesize / target_size

                self.log.append('Attempt # %s\nSize: %s Mbytes, now file is x %s larger than needed' %
                                (att_counter, str(filesize/1048576)[:4], str(size_deviation)[:5]))
                self.add_info_box()
                # print("size: {}; factor: {:.3f}".format(filesize, size_deviation))

                if size_deviation <= (100 + tolerance) / 100:
                    # # filesize fits
                    # with open(img_target_filename, "wb") as f:
                    #     f.write(data)

                    self.candidate_img = img
                    self.save_io()
                    self.add_example_frame(size_deviation)
                    break
                else:
                    # filesize not good enough => adapt width and height
                    # use sqrt of deviation since applied both in width and height
                    new_width = img.size[0] / size_deviation ** 0.5
                    new_height = new_width / aspect
                    # resize from img_orig to not lose quality
                    print('New width: %s' % new_width)
                    print('New height: %s' % new_height)
                    img = img_orig.resize((int(new_width), int(new_height)))


    def add_example_frame(self, size_deviation):

        # bbox = self.canvas.bbox("")
        # self.
        try:
            # print(size_deviation)
            # prevew_x = self.preview_canvas.winfo_rootx()
            # print(self.initial_width)
            # prevew_y = self.preview_canvas.winfo_rooty()
            # print(self.initial_width)
            # # canvas_y = self.canvas.canvasy()
            #
            # x_factor = self.initial_width / 600
            # y_factor = self.initial_height / 200
            #

            # print(x_factor, y_factor)

            # rec_x = self.initial_width / x_factor * size_deviation
            # rec_y = self.initial_height / x_factor            # rec_y = (200 / y_factor)
            #
            # print(rec_x, rec_y)

            print('Result size: ', self.result_size)
            # print('Preview img size: ', self.img_preview.size())

            crop_factor_x = self.result_size[0] / self.initial_width
            crop_factor_y = self.result_size[1] / self.initial_height

            print(crop_factor_x)

            rec_x, rec_y = self.img_prevew_size[0] * crop_factor_x, self.img_prevew_size[1] * crop_factor_y
            print('Rec: ', rec_x, rec_y)

            self.preview_canvas.create_rectangle(0, 0,
                                                 rec_x, rec_y,
                                                 outline='red',
                                                 width=2)
            self.preview_canvas.grid()
        except Exception as e:
            print(e)
        # self.canvas.grid()

    def save_process(self):

        def save_file(file):
            file = asksaveasfile(defaultextension='.jpg')
            if file:
                self.candidate_img.save(file, quality=100, subsampling=0, icc_profile=self.icc_profile)
                file.close()

        self.save_text = tk.StringVar()
        self.save_btn = tk.Button(self.root, textvariable=self.save_text,
                                  font="Raleway",
                                  command=lambda: save_file(self.candidate_img))
        self.save_text.set("Save...")
        self.save_btn.grid(column=2, row=4)

    def save_io(self):
        file = asksaveasfile()
        if file:
            self.candidate_img.save(file, quality=100, subsampling=0, icc_profile=self.icc_profile)
            self.result_size = self.candidate_img.size
            # contents = output.getvalue()

    def app(self):
        self.root = tk.Tk()
        self.root.title('PanResizer')

        self.create_canvas()
        self.add_instructions()
        self.add_logo()
        self.add_open_button()

        # self.open_image()
        self.add_info_box()

        self.calculate_initial_data()

        self.root.mainloop()

if __name__ == "__main__":
    resizer = PanResizer()
    resizer.app()