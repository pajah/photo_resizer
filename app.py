import tkinter as tk

from tkinter.filedialog import askopenfile
from PIL import Image, ImageTk


class PanResizer(object):
    def __init__(self):
        self.initial_file_path = None
        self.initial_file = None
        self.logo_label = None
        self.img_preview = None
        self.log = []

    def open_file(self):
        file = tk.filedialog.askopenfile(title="Open file")
        if file:
            img = Image.open(file.name)
            self.initial_file = ImageTk.PhotoImage(img)

            print(img.size)

            self.initial_height = img.height
            self.initial_width = img.width

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


        self.info_box.grid(columnspan=2, column=0, row=3)

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
        if self.initial_file:
            print(self.initial_file.width)
            self.log.append('Height: %s' % self.initial_height)
            self.log.append('Width: %s' % self.initial_width)
            self.add_info_box()


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
    # root = tk.Tk()
    # # MainApplication(root).pack(side="top", fill="both", expand=True)
    # canvas = tk.Canvas(root, width=600, height=300)
    # canvas.grid(columnspan=2)
    #
    # browse_text = tk.StringVar()
    # browse_btn = tk.Button(root, textvariable=browse_text, font="Raleway",
    #                        command=lambda: open_file())
    # browse_text.set("Browse...")
    # browse_btn.grid(column=1, row=0)
    #
    # root.mainloop()

    resizer = PanResizer()
    resizer.app()