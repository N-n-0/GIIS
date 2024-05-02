from tkinter import *
from tkinter import messagebox, ttk
from functools import partial
import math
import time
import keyboard


class PolygonEditor:
    def __init__(self, root):
        self.root = root
        self.root.geometry("900x500")
        self.root.resizable(True, True)

        self.canvas = Canvas(self.root, background="black", cursor="hand2")
        self.canvas.pack(fill="both", expand=True)

        self.root.bind("<Configure>", self.resize_canvas)

        self.points, self.lines, self.line_points = [], [], []
        self.polygon = None
        self.click_count = 0
        self.edges = []
        self.active_edges = []
        self.scanline = 0

        self.x_label = Label(self.root, text="X:")
        self.x_label.pack(anchor=NW)
        self.x_entry = Entry(self.root, width=10)
        self.x_entry.pack(anchor=NW)

        self.y_label = Label(self.root, text="Y:")
        self.y_label.pack(anchor=NW)
        self.y_entry = Entry(self.root, width=10)
        self.y_entry.pack(anchor=NW)

        self.add_button = Button(self.root, text="Проверить точку", command=self.check_point)
        self.add_button.pack(anchor=NW)

        self.convex_hull_menu = Menu(self.root, tearoff=0)

        self.poligon_menu = Menu(self.root, tearoff=0)
        self.poligon_menu.add_command(label="Метод Грэхема", command=lambda: self.compute_convex_hull("graham"))
        self.poligon_menu.add_command(label="Метод Джарвиса", command=lambda: self.compute_convex_hull("jarvis"))

        self.fill_menu = Menu(self.root, tearoff=0)
        self.fill_menu.add_command(label="Растровая развертка с упорядоченным списком ребер",
                                   command=self.fill_polygon_scanline)
        self.fill_menu.add_command(
            label="Растровая развертка с упорядоченным списком ребер, использующая список активных ребер",
            command=self.fill_polygon)
        self.fill_menu.add_command(
            label="Заполнение с затравкой",
            command=self.fill_polygon_with_seed)
        self.fill_menu.add_command(
            label="Заполнение с затравкой 1",
            command=self.fill_polygon_with_seed_line)

        self.convex_hull_menu.add_command(label="Очистить", command=self.clear_canvas)
        self.convex_hull_menu.add_command(label="Построить полигон", command=self.build_polygon)
        self.convex_hull_menu.add_command(label="Проверить выпуклость", command=self.check_convex)
        self.convex_hull_menu.add_command(label="Вычислить нормали", command=self.calculate_normals)
        self.convex_hull_menu.add_command(label="Поиск точек пересечения", command=self.find_cross_points)
        self.convex_hull_menu.add_cascade(label="Построение выпуклых оболочек", menu=self.poligon_menu)
        self.convex_hull_menu.add_cascade(label="Заливка", menu=self.fill_menu)

        self.root.config(menu=self.convex_hull_menu)

        self.canvas.bind("<Button-1>", self.add_point)
        self.canvas.bind("<Button-3>", self.handle_click)

    def handle_click(self, event):
        if self.click_count == 0:
            self.line_points.append((event.x, event.y))
            self.click_count += 1
        else:
            self.canvas.create_line(self.line_points[-1][0], self.line_points[-1][1], event.x, event.y, fill='red')
            self.line_points.append((event.x, event.y))

    def resize_canvas(self, event):
        self.canvas.config(width=event.width, height=event.height * 0.8)

    def clear_canvas(self):
        self.points, self.lines, self.line_points = [], [], []
        self.polygon = None
        self.click_count = 0
        self.canvas.delete("all")

    def add_point(self, event):
        x, y = event.x, event.y
        self.points.append((x, y))
        self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="white")

        if len(self.points) > 1:
            last_point = self.points[-2]
            self.lines.append(self.canvas.create_line(last_point[0], last_point[1], x, y, fill='white'))

    def check_point(self):
        if self.polygon is None:
            messagebox.showerror("Ошибка", "Полигон не построен.")
            return

        x = int(self.x_entry.get())
        y = int(self.y_entry.get())

        self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="white", tags="point")

        if self.check_point_in_polygon((x, y)):
            messagebox.showinfo("Результат", "Точка принадлежит полигону.")
        else:
            messagebox.showinfo("Результат", "Точка не принадлежит полигону.")

        if self.point_in_polygon((x, y)):
            messagebox.showinfo("Результат", "Точка принадлежит полигону.")
        else:
            messagebox.showinfo("Результат", "Точка не принадлежит полигону.")

        if self.check((x, y)):
            messagebox.showinfo("Результат", "Точка принадлежит полигону.")
        else:
            messagebox.showinfo("Результат", "Точка не принадлежит полигону.")

        self.x_entry.delete(0, END)
        self.y_entry.delete(0, END)

        self.canvas.delete("point")


    def check_point_in_polygon(self, point):
        if len(self.points) < 3:
            return False

        intersections = 0
        last_point = self.points[-1]

        if point in self.points:
            return True

        if point[0] >= sorted(self.points, key=lambda p: (p[0], p[1]))[0][0]:
            for i in range(len(self.points)):
                current_point = self.points[i]
                intersection = self.intersect(last_point, current_point, point, (self.canvas.winfo_width(), point[1]))
                if intersection is not None:
                    intersections += 1

                last_point = current_point

        return intersections % 2 == 1


    def intersect(self, point1, point2, point3, point4):
        x1, y1 = point1
        x2, y2 = point2
        x3, y3 = point3
        x4, y4 = point4

        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if den == 0:
            return None

        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den

        if 0 <= t <= 1 and 0 <= u <= 1:
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            return x, y

        return None

    def find_intersection(self, p1, p2, p3, p4):
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4

        a1 = y2 - y1
        b1 = x1 - x2
        c1 = x2 * y1 - x1 * y2

        a2 = y4 - y3
        b2 = x3 - x4
        c2 = x4 * y3 - x3 * y4

        denominator = a1 * b2 - a2 * b1

        if denominator == 0:
            return None

        x = (b1 * c2 - b2 * c1) / denominator
        y = (a2 * c1 - a1 * c2) / denominator

        if min(x1, x2) <= x <= max(x1, x2) and min(y1, y2) <= y <= max(y1, y2) and \
                min(x3, x4) <= x <= max(x3, x4) and min(y3, y4) <= y <= max(y3, y4):
            return int(x), int(y)
        else:
            return None

    def find_intersections(self):
        intersections = []

        n1 = len(self.points)
        n2 = len(self.line_points)

        for i in range(n1):
            p1 = self.points[i]
            p2 = self.points[(i - 1) % n1]

            for j in range(n2 - 1):
                p3 = self.line_points[j]
                p4 = self.line_points[j + 1]

                intersection = self.find_intersection(p1, p2, p3, p4)

                if intersection:
                    intersections.append(intersection)

        return intersections

    def find_cross_points(self):
        if self.polygon is None:
            messagebox.showerror("Ошибка", "Полигон не построен.")
            return

        if not self.line_points:
            messagebox.showerror("Ошибка", "Не найдено линий.")
            return

        points = self.find_intersections()

        message = 'Точки пересечения:\n'

        for point in points:
            message += f'{point}\n'

        messagebox.showinfo("Результат", message)

    def build_polygon(self):
        if len(self.points) < 3:
            messagebox.showerror("Ошибка", "Необходимо добавить как минимум 3 точки для построения полигона.")
            return

        last_point = self.points[-1]
        first_point = self.points[0]
        self.lines.append(
            self.canvas.create_line(last_point[0], last_point[1], first_point[0], first_point[1], fill='white'))
        print(self.points)
        self.polygon = self.points

    def is_convex_polygon(self):
        num_vertices = len(self.polygon)
        if num_vertices < 3:
            return False

        cross_products = []
        for i in range(num_vertices):
            curr_vertex = self.polygon[i]
            next_vertex = self.polygon[(i + 1) % num_vertices]
            prev_vertex = self.polygon[(i - 1) % num_vertices]

            cross_products.append(self.find_rotate(prev_vertex, curr_vertex, next_vertex))

        positive_cross_products = [product for product in cross_products if product > 0]
        negative_cross_products = [product for product in cross_products if product < 0]
        null_cross_products = [product for product in cross_products if product == 0]

        if len(null_cross_products) == num_vertices:
            result = 'Полигон вырождается в отрезок'
        elif len(positive_cross_products) == num_vertices or len(negative_cross_products) == num_vertices:
            result = 'Полигон выпуклый'
        else:
            result = 'Полигон вогнутый'

        return result

    def find_rotate(self, prev_vertex, curr_vertex, next_vertex):
        vector_ab = (next_vertex[0] - curr_vertex[0], next_vertex[1] - curr_vertex[1])
        vector_bc = (prev_vertex[0] - curr_vertex[0], prev_vertex[1] - curr_vertex[1])

        cross_product = vector_ab[0] * vector_bc[1] - vector_ab[1] * vector_bc[0]
        return cross_product

    def check_convex(self):
        if self.polygon is None:
            messagebox.showerror("Ошибка", "Полигон не построен.")
            return

        is_convex = self.is_convex_polygon()

        if is_convex:
            messagebox.showinfo("Результат", is_convex)

    def calculate_inner_normal(self, point_a, point_b):
        dx = point_b[0] - point_a[0]
        dy = point_b[1] - point_a[1]
        return (-dy, dx)

    def calculate_normals(self):
        if self.polygon is None:
            messagebox.showerror("Ошибка", "Полигон не построен.")
            return

        normals = []

        for i in range(len(self.polygon)):
            current_point = self.polygon[i]
            next_point = self.polygon[(i + 1) % len(self.polygon)]

            normal = self.calculate_inner_normal(current_point, next_point)
            normals.append(normal)

        message = 'Внутренние нормали:\n'
        for normal in normals:
            message += f'{normal}\n'

        messagebox.showinfo("Результат", message)

    def compute_convex_hull(self, method):
        if self.polygon is None:
            messagebox.showerror("Ошибка", "Полигон не построен.")
            return

        points = self.polygon[:]

        if self.is_convex_polygon(self.polygon) == 'Полигон вогнутый':
            if method == "graham":
                self.polygon = self.graham_scan(points)
            elif method == "jarvis":
                self.polygon = self.jarvis_march(points)
        else:
            messagebox.showerror("Ошибка", "Постройка выпуклой оболочки невозможна")
            return

        self.points = self.polygon

        self.canvas.delete("all")

        for i in range(len(self.polygon) - 1):
            current_point = self.polygon[i]
            next_point = self.polygon[(i + 1) % len(self.polygon)]

            self.lines.append(
                self.canvas.create_line(current_point[0], current_point[1], next_point[0], next_point[1], fill='white'))

        last_point = self.points[-1]
        first_point = self.points[0]
        self.lines.append(
            self.canvas.create_line(last_point[0], last_point[1], first_point[0], first_point[1], fill='white'))

    def graham_scan(self, points):
        def polar_angle(p, leftmost):
            dx = p[0] - leftmost[0]
            dy = p[1] - leftmost[1]

            angle = math.atan2(dy, dx)
            angle_degrees = math.degrees(angle)
            if angle_degrees < 0:
                angle_degrees += 360

            return angle_degrees

        n = len(points)
        if n < 3:
            return points

        leftmost = min(points, key=lambda p: (p[1], p[0]))

        sorted_points = sorted(points,
                               key=lambda p: (polar_angle(p, leftmost), -p[1], p[0]))

        sorted_points.remove(leftmost)
        convex_hull = [leftmost, sorted_points[0]]

        for i in range(1, n - 1):
            if self.find_rotate(convex_hull[-2], convex_hull[-1], sorted_points[i]) > 0:
                convex_hull.append(sorted_points[i])
            elif len(convex_hull) > 3:
                convex_hull.pop()

        return convex_hull

    def jarvis_march(self, points):
        def polar_angle(p, leftmost):
            dx = p[0] - leftmost[0]
            dy = p[1] - leftmost[1]

            angle = math.atan2(dy, dx)
            angle_degrees = math.degrees(angle)
            if angle_degrees < 0:
                angle_degrees += 360

            return angle_degrees

        n = len(points)
        if n < 3:
            return points

        leftmost = min(points, key=lambda p: (p[0], p[1]))

        convex_hull = [leftmost]
        current_point = leftmost

        while True:
            next_point = None
            for point in points:
                if point == current_point:
                    continue
                if next_point is None or polar_angle(point, current_point) < polar_angle(next_point, current_point):
                    next_point = point

            if next_point == leftmost:
                break

            convex_hull.append(next_point)
            current_point = next_point

        return convex_hull



class Edge:
    def __init__(self, y_max, x, dx, dy):
        self.y_max = y_max
        self.x = x
        self.dx = dx
        self.dy = dy
        self.next = None


root = Tk()
editor = PolygonEditor(root)
root.mainloop()