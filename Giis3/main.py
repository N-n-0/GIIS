from tkinter import *
from tkinter import ttk
import math

class GraphicsEditor:
    def __init__(self, root):
        self.points = []

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

        self.methods = ["форма Эрмита", "форма Безье", "B-сплайн"]
        self.selected_method = StringVar()
        self.header = ttk.Label(text="Выберите метод")
        self.header.pack(anchor=NW)
        self.clear_button = Button(self.root, text="Очистить", command=self.clear_canvas)

        for method in self.methods:
            self.method_btn = ttk.Radiobutton(text=method, value=method, variable=self.selected_method)
            self.method_btn.pack(anchor=NW)

        self.clear_button.pack(anchor=SW, side=LEFT)
        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind('<Double-Button-3>', self.delete_point)
        self.canvas.bind("<B3-Motion>", self.drag_point)

    def run(self):
        self.root.update_idletasks()
        self.root.mainloop()

    def resize_canvas(self, event):
        self.canvas.config(width=event.width, height=event.height * 0.8)

    def clear_canvas(self):
        self.points = []
        self.canvas.delete("all")

    def change_header(self):
        self.header.config(text=f"Выбран {self.selected_method.get()}")

    def delete_point(self, event):
        self.remove_nearest_point((event.x, event.y))
        self.choose_method()

    def find_nearest_point(self, target_point):
        nearest_distance = math.inf
        nearest_index = -1

        for i, point in enumerate(self.points):
            distance = math.sqrt((point[0] - target_point[0]) ** 2 + (point[1] - target_point[1]) ** 2)
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_index = i

        return nearest_index

    def remove_nearest_point(self, target_point):
        nearest_index = self.find_nearest_point(target_point)
        if nearest_index != -1:
            del self.points[nearest_index]

    def drag_point(self, event):
        x = event.x
        y = event.y
        nearest_index = self.find_nearest_point((x, y))
        if nearest_index != -1:
            self.points[nearest_index] = (x, y)
            self.choose_method()

    def handle_click(self, event):
        x = event.x
        y = event.y
        self.points.append((x, y))
        self.choose_method()

    def choose_method(self):
        self.canvas.delete("all")

        if self.label.winfo_exists():
            self.label.destroy()
        if self.selected_method.get() == self.methods[0]:
            self.generate_hermit()
        elif self.selected_method.get() == self.methods[1]:
            self.generate_bezier()
        elif self.selected_method.get() == self.methods[2]:
            self.generate_b_splain()
        else:
            self.label = ttk.Label(text="Алгоритм не выбран")
            self.label.pack(anchor=SW)
            self.clear_canvas()

    def generate_hermit(self):
        for point in self.points:
            x, y = point
            self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill='red')

        for i in range(len(self.points) - 1):
            p0 = self.points[i]
            p1 = self.points[i + 1]
            t0 = (p1[0] - self.points[i - 1][0]) / 2 if i > 0 else 0
            t1 = (self.points[i + 2][0] - p0[0]) / 2 if i < len(self.points) - 2 else 0

            for t in range(0, 101):
                t /= 100.0
                h1 = 2 * t ** 3 - 3 * t ** 2 + 1
                h2 = -2 * t ** 3 + 3 * t ** 2
                h3 = t ** 3 - 2 * t ** 2 + t
                h4 = t ** 3 - t ** 2

                x = h1 * p0[0] + h2 * p1[0] + h3 * t0 + h4 * t1
                y = h1 * p0[1] + h2 * p1[1] + h3 * t0 + h4 * t1

                if t == 0:
                    prev_x, prev_y = x, y
                else:
                    self.canvas.create_line(prev_x, prev_y, x, y, fill='blue')
                    prev_x, prev_y = x, y


    def generate_bezier(self):
        for i, point in enumerate(self.points):
            x, y = point
            if i % 3 != 0:
                self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill='green')
            else:
                self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill='red')

        size = (len(self.points) - 1) // 3
        if len(self.points) >= 4:# and (len(self.points) - 1) % 3 == 0:
            for i in range(0, size):
                p0 = self.points[3*i]
                p1 = self.points[3*i + 1]
                p2 = self.points[3*i + 2]
                p3 = self.points[3*i + 3]

                iterations = 100  # Количество итераций дискретизации

                for j in range(iterations + 1):
                    t = j / iterations

                    x = (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t ** 2 * p2[0] + t ** 3 * \
                        p3[0]
                    y = (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t ** 2 * p2[1] + t ** 3 * \
                        p3[1]

                    if j == 0:
                        prev_x, prev_y = x, y
                    else:
                        self.canvas.create_line(prev_x, prev_y, x, y, fill='blue')
                        prev_x, prev_y = x, y

    def generate_b_splain(self):
        for point in self.points:
            x, y = point
            self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill='red')

        if len(self.points) > 3:

            for i in range(1, len(self.points)-2):
                '''if i+1 > len(self.points):
                    k = 0
                    p = 1
                elif i+2 > len(self.points):
                    k = len(self.points) - 1
                    p = 0
                else:'''
                k = i+1
                p = i+2

                a0 = (self.points[i-1][0] + 4*self.points[i][0] + self.points[k][0])/6
                a1 = (-self.points[i-1][0] + self.points[k][0])/2
                a2 = (self.points[i-1][0] - 2*self.points[i][0] + self.points[k][0])/2
                a3 = (-self.points[i-1][0] + 3*self.points[i][0] - 3*self.points[k][0] + self.points[p][0])/6
                b0 = (self.points[i-1][1] + 4 * self.points[i][1] + self.points[k][1]) / 6
                b1 = (-self.points[i-1][1] + self.points[k][1]) / 2
                b2 = (self.points[i-1][1] - 2 * self.points[i][1] + self.points[k][1]) / 2
                b3 = (-self.points[i-1][1] + 3 * self.points[i][1] - 3 * self.points[k][1] + self.points[p][1]) / 6

                for t in range(0, 101):
                    t /= 100.0

                    x = ((a3*t + a2)*t +a1)*t +a0
                    y = ((b3*t + b2)*t +b1)*t +b0

                    if t == 0:
                        prev_x, prev_y = x, y
                    else:
                        self.canvas.create_line(prev_x, prev_y, x, y, fill='blue')
                        prev_x, prev_y = x, y

if __name__ == '__main__':
    root = Tk()
    editor = GraphicsEditor(root)
    editor.run()
