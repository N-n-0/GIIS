from matplotlib import pyplot as plt
import numpy as np
from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class Shape:
    def __init__(self, points):
        self.center_point = None
        self.points = points
        self.update_center_point()

    def update_center_point(self):
        num_points = len(self.points)
        sum_x = sum(point.x for point in self.points)
        sum_y = sum(point.y for point in self.points)
        sum_z = sum(point.z for point in self.points)
        center_x = sum_x / num_points
        center_y = sum_y / num_points
        center_z = sum_z / num_points
        self.center_point = Point(center_x, center_y, center_z)

    def rotate(self, angle, axis):
        rotation_matrix = self.get_rotation_matrix(angle, axis)
        for point in self.points:
            point.x, point.y, point.z = np.dot(rotation_matrix, [point.x, point.y, point.z])
        self.update_center_point()

    def get_rotation_matrix(self, angle, axis):
        c = np.cos(angle)
        s = np.sin(angle)
        if axis == 'x':
            return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
        elif axis == 'y':
            return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
        elif axis == 'z':
            return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

    def scale(self, scale_factor):
        for point in self.points:
            point.x = (point.x - self.center_point.x) * scale_factor + self.center_point.x
            point.y = (point.y - self.center_point.y) * scale_factor + self.center_point.y
            point.z = (point.z - self.center_point.z) * scale_factor + self.center_point.z
        self.update_center_point()


class GraphicsEditor3D:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg='white')
        self.root.title("3D")

        self.fig = plt.figure(figsize=(5, 5))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.axis('on')

        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)
        self.ax.set_zlim(0, 10)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(anchor=NW)

        self.points = []
        self.shapes = []

        self.selected_shape = None

        self.x_label = Label(self.root, text="X:")
        self.x_label.pack(anchor=NW)
        self.x_entry = Entry(self.root, width=10)
        self.x_entry.pack(anchor=NW)

        self.y_label = Label(self.root, text="Y:")
        self.y_label.pack(anchor=NW)
        self.y_entry = Entry(self.root, width=10)
        self.y_entry.pack(anchor=NW)

        self.z_label = Label(self.root, text="Z:")
        self.z_label.pack(anchor=NW)
        self.z_entry = Entry(self.root, width=10)
        self.z_entry.pack(anchor=NW)

        self.add_button = Button(self.root, text="Добавить точку", command=self.add_point)
        self.add_button.pack(anchor=NW)

        self.create_shape_button = Button(self.root, text="Создать фигуру", command=self.create_shape)
        self.create_shape_button.pack(anchor=NW)

        self.clear_button = Button(self.root, text="Очистить", command=self.clear_all)
        self.clear_button.pack(anchor=NW)

        self.shapes_listbox = Listbox(self.root, selectmode=SINGLE)
        self.shapes_listbox.pack(anchor=NW)
        self.shapes_listbox.bind("<<ListboxSelect>>", self.select_shape)

        self.root.bind("<KeyPress-d>", self.move_shape_x_plus)
        self.root.bind("<KeyPress-a>", self.move_shape_x_minus)
        self.root.bind("<KeyPress-w>", self.move_shape_y_plus)
        self.root.bind("<KeyPress-s>", self.move_shape_y_minus)
        self.root.bind("<KeyPress-q>", self.move_shape_z_plus)
        self.root.bind("<KeyPress-e>", self.move_shape_z_minus)

        self.root.bind("<KeyPress-z>", self.rotate_selected_shape_x)
        self.root.bind("<KeyPress-x>", self.rotate_selected_shape_y)
        self.root.bind("<KeyPress-c>", self.rotate_selected_shape_z)

        self.root.bind("<KeyPress-f>", self.scale_selected_shape_plus_ten_percent)
        self.root.bind("<KeyPress-g>", self.scale_selected_shape_minus_ten_percent)

    def scale_selected_shape_plus_ten_percent(self, *args):
        if self.selected_shape:
            self.selected_shape.scale(1.1)
            self.update_shape()

    def scale_selected_shape_minus_ten_percent(self, *args):
        if self.selected_shape:
            self.selected_shape.scale(0.9)
            self.update_shape()

    def rotate_selected_shape_x(self, *args):
        if self.selected_shape:
            self.selected_shape.rotate(np.pi / 4, 'x')  # Rotate by 45 degrees around the X-axis
            self.update_shape()

    def rotate_selected_shape_y(self, *args):
        if self.selected_shape:
            self.selected_shape.rotate(np.pi / 4, 'y')  # Rotate by 45 degrees around the Y-axis
            self.update_shape()

    def rotate_selected_shape_z(self, *args):
        if self.selected_shape:
            self.selected_shape.rotate(np.pi / 4, 'z')  # Rotate by 45 degrees around the Z-axis
            self.update_shape()

    def move_shape_x_plus(self, *args):
        if self.selected_shape:
            for point in self.selected_shape.points:
                point.x += 1
            self.update_shape()

    def move_shape_x_minus(self, *args):
        if self.selected_shape:
            for point in self.selected_shape.points:
                point.x -= 1
            self.update_shape()

    def move_shape_y_plus(self, *args):
        if self.selected_shape:
            for point in self.selected_shape.points:
                point.y += 1
            self.update_shape()

    def move_shape_y_minus(self, *args):
        if self.selected_shape:
            for point in self.selected_shape.points:
                point.y -= 1
            self.update_shape()

    def move_shape_z_plus(self, *args):
        if self.selected_shape:
            for point in self.selected_shape.points:
                point.z += 1
            self.update_shape()

    def move_shape_z_minus(self, *args):
        if self.selected_shape:
            for point in self.selected_shape.points:
                point.z -= 1
            self.update_shape()

    def select_shape(self, event):
        selected_index = self.shapes_listbox.curselection()
        if selected_index:
            self.selected_shape = self.shapes[selected_index[0]]
        self.update_shapes_listbox()
        self.update_shape()

    def update_shape(self):
        self.ax.clear()

        if self.selected_shape:
            points = self.selected_shape.points
            x_values = [point.x for point in points]
            y_values = [point.y for point in points]
            z_values = [point.z for point in points]
            self.draw_shape(x_values, y_values, z_values)

        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)
        self.ax.set_zlim(0, 10)
        self.canvas.draw()

    def clear_all(self):
        self.points = []
        self.selected_shape = None
        self.shapes = []
        self.update_plot()
        self.update_shape()
        self.update_shapes_listbox()

    def add_point(self):
        x = float(self.x_entry.get())
        y = float(self.y_entry.get())
        z = float(self.z_entry.get())

        self.x_entry.delete(0, END)
        self.y_entry.delete(0, END)
        self.z_entry.delete(0, END)
        self.selected_shape = None

        point = Point(x, y, z)
        self.points.append(point)
        self.update_plot()

    def draw_shape(self, x_values, y_values, z_values):
        num_steps = 20
        if len(x_values) >= 3:
            lines = []
            for i in range(len(x_values)):
                for j in range(i + 1, len(x_values)):
                    lines.append([i, j])

            interpolated_lines = []
            for line in lines:
                x_interp = np.linspace(x_values[line[0]], x_values[line[1]], num_steps)
                y_interp = np.linspace(y_values[line[0]], y_values[line[1]], num_steps)
                z_interp = np.linspace(z_values[line[0]], z_values[line[1]], num_steps)
                interpolated_lines.append(list(zip(x_interp, y_interp, z_interp)))

            for line in interpolated_lines:
                x, y, z = zip(*line)
                self.ax.plot(x, y, z, color='black', linewidth=1)
        else:
            self.ax.plot(x_values, y_values, z_values, color='black', linewidth=1)

    def create_shape(self):
        shape = Shape(self.points)
        self.shapes.append(shape)
        self.points = []
        self.update_plot()
        self.update_shapes_listbox()

    def update_plot(self):
        self.ax.clear()

        if self.points:
            marked_x = [point.x for point in self.points]
            marked_y = [point.y for point in self.points]
            marked_z = [point.z for point in self.points]
            self.ax.scatter(marked_x, marked_y, marked_z, color='red')

        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)
        self.ax.set_zlim(0, 10)
        self.canvas.draw()

    def update_shapes_listbox(self):
        self.shapes_listbox.delete(0, END)
        for shape in self.shapes:
            self.shapes_listbox.insert(END, f"Shape {self.shapes.index(shape) + 1}")


if __name__ == "__main__":
    root = Tk()
    editor = GraphicsEditor3D(root)
    root.mainloop()
