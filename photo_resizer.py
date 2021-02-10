import tkinter as tk

from PIL import Image, ImageTk

print('test')

root = tk.Tk()

canvas = tk.Canvas(root, width=600, height=300)
canvas.grid(columnspan=2)

# instructions
instructions = tk.Label(root, text="Select JPG to resize", font="Raleway")
instructions.grid(columnspan=1, column=0, row=0)

# input browse button
browse_text = tk.StringVar()
browse_btn = tk.Button(root, textvariable=browse_text, font="Raleway")
browse_text.set("Browse...")
browse_btn.grid(column=1, row=0)

root.mainloop()