from tkinter import *
from tkinter import ttk
import numpy as np
import time

click_count = 0
start_x, start_y = 0, 0


class GraphicsEditor:
    def __init__(self, root):
        self.click_count, self.start_x, self.start_y, self.start_x1, self.start_y1 = 0, 0, 0, 0, 0

        self.debug_mode = IntVar()
        self.is_drawing = True

        self.label = ttk.Label(text="Алгоритм не выбран")
        self.label.pack(anchor=SW)
        self.label.destroy()

        self.root = root
        self.root.title("Графический редактор")
        self.root.geometry("900x500")
        self.root.resizable(True, True)

        self.canvas = Canvas(self.root, background="black", cursor="hand2")
        self.canvas.pack(fill="both", expand=True)
        self.root.bind("<Configure>", self.resize_canvas)

        self.methods = ["Окружность", "Эллипс", "Гипербола", "Парабола"]
        self.selected_method = StringVar()
        self.header = ttk.Label(text="Выберите фигуру")
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
        self.canvas.bind("<Button-1>", self.handle_click, )

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
        self.click_count, self.start_x, self.start_y, self.start_x1, self.start_y1 = 0, 0, 0, 0, 0
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
        elif self.click_count == 1 and self.selected_method.get() != self.methods[3]:
            self.choose_line(event.x, event.y)
            self.click_count = 0
        elif self.click_count == 1 and self.selected_method.get() == self.methods[3]:
            self.start_x1 = event.x
            self.start_y1 = event.y
            self.click_count += 1
        else:
            self.choose_line(event.x, event.y)
            self.click_count = 0

    def choose_line(self, x, y):
        if self.label.winfo_exists():
            self.label.destroy()

        if self.selected_method.get() == self.methods[0]:
            self.draw_circle(self.start_x, self.start_y, x, y)
        elif self.selected_method.get() == self.methods[1]:
            self.draw_ellipse(self.start_x, self.start_y, x, y)
        elif self.selected_method.get() == self.methods[2]:
            self.draw_hyperbola(self.start_x, self.start_y, x, y)
        elif self.selected_method.get() == self.methods[3]:
            self.draw_parabola(self.start_x, self.start_y, self.start_x1, self.start_y1, x, y)
        else:
            self.label = ttk.Label(text="Фигура не выбрана")
            self.label.pack(anchor=SW)

    def draw_circle(self, x1, y1, x2, y2):
        radius = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        x = 0
        y = radius
        delta = 1 - 2 * radius

        while y >= x:
            if self.is_drawing:
                self.draw_circle_pixels(x1, y1, x, y)
            if self.debug_mode.get() == 1:
                self.canvas.update()
                time.sleep(0.1)

            error = 2 * (delta + y) - 1

            if delta < 0 and error <= 0:
                x += 1
                delta += 2 * x + 1
                continue

            error = 2 * (delta - x) - 1

            if delta > 0 and error > 0:
                y -= 1
                delta += 1 - 2 * y
                continue

            x += 1
            delta += 2 * (x - y)
            y -= 1

        self.start_x, self.start_y = 0, 0

    def draw_circle_pixels(self, x1, y1, x, y):
        self.canvas.create_rectangle(x1 + x, y1 + y,
                                     x1 + x, y1 + y, outline="white")
        self.canvas.create_rectangle(x1 - x, y1 + y,
                                     x1 - x, y1 + y, outline="white")
        self.canvas.create_rectangle(x1 + x, y1 - y,
                                     x1 + x, y1 - y, outline="white")
        self.canvas.create_rectangle(x1 - x, y1 - y,
                                     x1 - x, y1 - y, outline="white")
        self.canvas.create_rectangle(x1 + y, y1 + x,
                                     x1 + y, y1 + x, outline="white")
        self.canvas.create_rectangle(x1 - y, y1 + x,
                                     x1 - y, y1 + x, outline="white")
        self.canvas.create_rectangle(x1 + y, y1 - x,
                                     x1 + y, y1 - x, outline="white")
        self.canvas.create_rectangle(x1 - y, y1 - x,
                                     x1 - y, y1 - x, outline="white")

    def draw_ellipse(self, x1, y1, x2, y2):
        a = abs(x2 - x1) / 2
        b = abs(y2 - y1) / 2
        _x = 0
        _y = b
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        a_sqr = a * a
        b_sqr = b * b
        delta = 4 * b_sqr * ((_x + 1) * (_x + 1)) + a_sqr * (
                (2 * _y - 1) * (2 * _y - 1)) - 4 * a_sqr * b_sqr
        while a_sqr * (2 * _y) > 2 * b_sqr * _x:
            if self.is_drawing:
                self.draw_ellipse_pixels(center_x, center_y, _x, _y)
            if self.debug_mode.get() == 1:
                self.canvas.update()
                time.sleep(0.1)

            if delta < 0:
                _x += 1
                delta += 4 * b_sqr * (2 * _x + 3)
            else:
                _x += 1
                delta = delta - 8 * a_sqr * (_y - 1) + 4 * b_sqr * (2 * _x + 3)
                _y -= 1
        delta = b_sqr * ((2 * _x + 1) * (2 * _x + 1)) + 4 * a_sqr * (
                (_y + 1) * (_y + 1)) - 4 * a_sqr * b_sqr
        while _y > 0:
            if self.is_drawing:
                self.draw_ellipse_pixels(center_x, center_y, _x, _y)
            if self.debug_mode.get() == 1:
                self.canvas.update()
                time.sleep(0.1)

            if delta < 0:
                _y -= 1
                delta += 4 * a_sqr * (2 * _y + 3)
            else:
                _y -= 1
                delta = delta - 8 * b_sqr * (_x + 1) + 4 * a_sqr * (2 * _y + 3)
                _x += 1

        self.start_x, self.start_y = 0, 0

    def draw_ellipse_pixels(self, x, y, _x, _y):
        self.canvas.create_rectangle(x + _x, y + _y,
                                     x + _x, y + _y, outline="white")
        self.canvas.create_rectangle(x + _x, y - _y,
                                     x + _x, y - _y, outline="white")
        self.canvas.create_rectangle(x - _x, y - _y,
                                     x - _x, y - _y, outline="white")
        self.canvas.create_rectangle(x - _x, y + _y,
                                     x - _x, y + _y, outline="white")

    def draw_hyperbola(self, x0, y0, x1, y1):
        c = (x1 * y1 - x0 * y0) / (y0 - y1)
        k = y0 * y1 * (x1 - x0) / (y0 - y1)
        x = 0
        while x < self.canvas.winfo_width():
            x = x + 0.02
            y = k / (x + c)
            x_center = x
            y_center = y
            if self.is_drawing:
                self.canvas.create_rectangle(x_center, y_center,
                                             x_center, y_center, outline="white")
            if self.debug_mode.get() == 1:
                self.canvas.update()
                time.sleep(10 ** -100)

        self.start_x, self.start_y = 0, 0

    def draw_parabola(self, x0, y0, x1, y1, x2, y2):
        A = [[x0 ** 2, x0, 1],
             [x1 ** 2, x1, 1],
             [x2 ** 2, x2, 1]]
        Y = [y0, y1, y2]
        a, b, c = np.linalg.solve(A, Y)

        x = 0
        while x <= self.canvas.winfo_width():
            y = int(a * x ** 2 + b * x + c)
            x_center = x
            y_center = y
            if self.is_drawing:
                self.canvas.create_rectangle(x_center, y_center,
                                             x_center, y_center, outline='white')
            x += 0.1
            if self.debug_mode.get() == 1:
                self.canvas.update()
                time.sleep(0.01)

        self.start_x, self.start_y, self.start_x1, self.start_y1 = 0, 0, 0, 0


if __name__ == '__main__':
    root = Tk()
    editor = GraphicsEditor(root)
    editor.run()
