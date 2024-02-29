from tkinter import *
from tkinter import ttk
import time


class GraphicsEditor:
    def __init__(self, root):
        self.click_count, self.start_x, self.start_y = 0, 0, 0

        self.debug_mode = IntVar()
        self.is_drawing = True

        self.label = ttk.Label(text="Алгоритм не выбран")
        self.label.pack(anchor=SW)
        self.label.destroy()

        self.root = root
        self.root.title("Мой Графический редактор")
        self.root.geometry("900x500")
        self.root.resizable(True, True)

        self.canvas = Canvas(self.root, background="black", cursor="hand2")
        self.canvas.pack(fill="both", expand=True)

        self.root.bind("<Configure>", self.resize_canvas)

        self.methods = ["ЦДА", "Брезенхема", "Ву"]
        self.selected_method = StringVar()
        self.header = ttk.Label(text="Выберите алгоритм")
        self.header.pack(anchor=NW)
        self.clear_button = Button(self.root, text="Очистить", command=self.clear_canvas)

        for method in self.methods:
            self.method_btn = ttk.Radiobutton(text=method, value=method, variable=self.selected_method)
            self.method_btn.pack(anchor=NW)

        enabled_checkbutton = ttk.Checkbutton(text="Отладка", variable=self.debug_mode, onvalue=True, offvalue=False,
                                              command=self.draw_grid)
        enabled_checkbutton.pack(padx=6, pady=6, anchor=SE, side=RIGHT)
        self.clear_button.pack(anchor=SW, side=LEFT)

    def run(self):
        self.canvas.bind("<Button-1>", self.handle_click)

        self.root.update_idletasks()
        self.root.mainloop()

    def draw_grid(self):
        if self.debug_mode.get() == 1:
            line_color = "gray"

            for y in range(0, self.canvas.winfo_height(), 5):
                self.canvas.create_line(0, y, self.canvas.winfo_width(), y, fill=line_color)

            for x in range(0, self.canvas.winfo_width(), 5):
                self.canvas.create_line(x, 0, x, self.canvas.winfo_height(), fill=line_color)
            self.canvas.update()
        elif self.debug_mode.get() == 0:
            self.clear_canvas()

    def resize_canvas(self, event):
        self.canvas.config(width=event.width, height=event.height * 0.8)

    def clear_canvas(self):
        self.click_count, self.start_x, self.start_y = 0, 0, 0
        self.is_drawing = False
        self.canvas.delete("all")

    def change_header(self):
        self.header.config(text=f"Выбран {self.selected_method.get()}")

    def handle_click(self, event):
        self.is_drawing = True
        if self.click_count == 0:
            self.start_x = event.x
            self.start_y = event.y
            self.click_count += 1
        else:
            self.choose_line(event.x, event.y)
            self.click_count = 0

    def choose_line(self, x, y):
        if self.label.winfo_exists():
            self.label.destroy()
        if self.selected_method.get() == self.methods[0]:
            self.generate_line_dda(x, y)
        elif self.selected_method.get() == self.methods[1]:
            self.generate_line_bresenham(x, y)
        elif self.selected_method.get() == self.methods[2]:
            self.generate_line_wu(x, y)
        else:
            self.label = ttk.Label(text="Алгоритм не выбран")
            self.label.pack(anchor=SW)

    def generate_line_dda(self, x, y):
        dx = x - self.start_x
        dy = y - self.start_y
        steps = max(abs(dx), abs(dy))
        if steps != 0:
            x_increment = dx / steps
            y_increment = dy / steps
        else:
            self.start_x, self.start_y, x_increment, y_increment = 0, 0, 0, 0

        x = self.start_x
        y = self.start_y

        for _ in range(int(steps)):
            self.canvas.create_rectangle(x, y, x, y, outline='white')
            x += x_increment
            y += y_increment

            if self.debug_mode.get() == 1:
                self.canvas.update()
                time.sleep(0.1)

        self.start_x, self.start_y = 0, 0

    def generate_line_bresenham(self, x, y):
        dx = abs(x - self.start_x)
        dy = abs(y - self.start_y)
        sx = -1 if self.start_x > x else 1
        sy = -1 if self.start_y > y else 1

        if dx > dy:
            err = dx / 2
        else:
            err = -dy / 2

        while True:
            self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='white')

            if self.debug_mode.get() == 1:
                self.canvas.update()
                time.sleep(0.1)

            if self.start_x == x and self.start_y == y:
                break
            e2 = err
            if e2 > -dx:
                err -= dy
                self.start_x += sx
            if e2 < dy:
                err += dx
                self.start_y += sy

        self.start_x, self.start_y = 0, 0

    def generate_line_wu(self, x, y):
        dx = x - self.start_x
        dy = y - self.start_y

        is_steep = abs(dy) > abs(dx)
        if is_steep:
            self.start_x, self.start_y = self.start_y, self.start_x
            x, y = y, x

        if self.start_x > x:
            self.start_x, x = x, self.start_x
            self.start_y, y = y, self.start_y

        dx = x - self.start_x
        dy = y - self.start_y
        gradient = dy / dx if dx != 0 else 1.0

        xend = round(self.start_x)
        yend = self.start_y + gradient * (xend - self.start_x)
        xpxl1 = int(xend)
        ypxl1 = int(yend)

        if is_steep:
            self.canvas.create_rectangle(ypxl1, xpxl1, ypxl1 + 1, xpxl1, outline='white')
        else:
            self.canvas.create_rectangle(xpxl1, ypxl1, xpxl1, ypxl1 + 1, outline='white')

        if is_steep:
            self.canvas.create_rectangle(ypxl1, xpxl1 + 1, ypxl1 + 1, xpxl1 + 1, outline='white')
        else:
            self.canvas.create_rectangle(xpxl1 + 1, ypxl1, xpxl1 + 1, ypxl1 + 1, outline='white')

        intery = yend + gradient
        xend = round(x)

        for x in range(int(xpxl1) + 1, int(xend)):
            if is_steep:
                self.canvas.create_rectangle(int(intery), x, int(intery) + 1, x, outline='white')
                self.canvas.create_rectangle(int(intery), x + 1, int(intery) + 1, x + 1, outline='white')
            else:
                self.canvas.create_rectangle(x, int(intery), x, int(intery) + 1, outline='white')
                self.canvas.create_rectangle(x + 1, int(intery), x + 1, int(intery) + 1, outline='white')
            intery += gradient
            if self.debug_mode.get() == 1:
                self.canvas.update()
                time.sleep(0.1)

        self.start_x, self.start_y = 0, 0


if __name__ == '__main__':
    root = Tk()
    editor = GraphicsEditor(root)
    editor.run()
