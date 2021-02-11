import tkinter as tk

from tkinter.simpledialog import askfloat
from tkinter.filedialog import askopenfile, asksaveasfile
from PIL import Image, ImageTk


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

            print(img.size)

            self.initial_height = img.height
            self.initial_width = img.width
            # self.initial_file_mb = len(img.fp.read()) / 1048576

            img.thumbnail((600, 600), Image.LANCZOS)
            self.img_preview = ImageTk.PhotoImage(img)


            self.log.append('File opened')



        self.add_info_box()
        self.open_image()
        self.calculate_initial_data()

    def create_canvas(self):
        self.canvas = tk.Canvas(self.root, height=600, width=300)
        self.canvas.grid(column=3, row=4)


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
            preview_label = tk.Label(self.root, image=preview)
            preview_label.image = preview
            # print(logo_label)
            preview_label.grid(column=0, row=2, columnspan=4)


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

            value = int(self.needed_mb)

            rng = range(10, 100)
            low = rng[0]
            high = rng[-1]
            mid = len(rng) // 2

            img = Image.open(self.initial_file.name)

            i = 0
            while low < high:
                i += 1
                new_im = img.resize((int(img.width * mid * 0.01), int(img.height * mid * 0.01)), Image.ANTIALIAS)
                new_im.save("cand.jpg", quality=100, subsampling=0, icc_profile=self.icc_profile)

                cand_size_mb = 0
                cand = Image.open("cand.jpg")
                cand_size_mb = len(cand.fp.read()) / 1048576

                if cand_size_mb < value:
                    low = mid + 1
                else:
                    high = mid - 1

                mid = (low + high) // 2

                self.log.append('Attempt %s\n'
                                'Trying %s percent of initial file:\n'
                                'MB file result: %s\n' % (str(i), str(mid), str(cand_size_mb)[:4]))
                self.log.append('---' * 20)

                self.cand_percentage = mid
                self.cand_size_mb = cand_size_mb

                self.candidate_img = cand
                self.add_info_box()

                if self.cand_percentage and self.cand_size_mb and self.candidate_img:
                    self.save_process()


            print('Last mid: %s' % mid)
            print('Last size: %s' % str(cand_size_mb))

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