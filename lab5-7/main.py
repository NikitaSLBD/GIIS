import tkinter as tk
from tkinter import messagebox, simpledialog
import math

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __repr__(self):
        return f"({self.x}, {self.y})"

class Edge:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
    
    def __eq__(self, other):
        return (self.p1 == other.p1 and self.p2 == other.p2) or (self.p1 == other.p2 and self.p2 == other.p1)
    
    def __hash__(self):
        return hash((self.p1, self.p2)) + hash((self.p2, self.p1))
    
    def __repr__(self):
        return f"[{self.p1} - {self.p2}]"

class PolygonEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Графический редактор полигонов")
        
        # Основные переменные
        self.points = []
        self.polygon = []
        self.current_polygon = []
        self.convex_hull = []
        self.triangles = []
        self.debug_text = ""
        self.line_points = []  # Точки линии для проверки пересечения
        
        # Создание интерфейса
        self.create_widgets()
        
        # Настройка обработчиков событий
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        
        # Переменные для рисования
        self.temp_line = None
        self.temp_point = None
        self.drawing_polygon = False
        self.drawing_intersection_line = False
        self.line_start = None
        
        # Цвета
        self.point_color = "red"
        self.polygon_color = "blue"
        self.line_color = "green"
        self.convex_hull_color = "purple"
        self.triangle_color = "orange"
        self.voronoi_color = "brown"
        self.fill_color = "cyan"
        
    def create_widgets(self):
        # Основной фрейм
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Холст для рисования
        self.canvas = tk.Canvas(main_frame, bg="white", width=800, height=600)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Панель управления
        control_frame = tk.Frame(main_frame, width=200, padx=5, pady=5)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления
        tk.Button(control_frame, text="Начать полигон", command=self.start_polygon).pack(fill=tk.X, pady=2)
        tk.Button(control_frame, text="Закончить полигон", command=self.finish_polygon).pack(fill=tk.X, pady=2)
        tk.Button(control_frame, text="Проверить пересечение линии", command=self.start_intersection_line).pack(fill=tk.X, pady=2)
        tk.Button(control_frame, text="Проверить выпуклость", command=self.check_convexity).pack(fill=tk.X, pady=2)
        tk.Button(control_frame, text="Найти нормали", command=self.find_normals).pack(fill=tk.X, pady=2)
        tk.Button(control_frame, text="Выпуклая оболочка (Грэхем)", command=self.graham_scan).pack(fill=tk.X, pady=2)
        tk.Button(control_frame, text="Выпуклая оболочка (Джарвис)", command=self.jarvis_march).pack(fill=tk.X, pady=2)
        tk.Button(control_frame, text="Проверить точку в полигоне", command=self.check_point_in_polygon).pack(fill=tk.X, pady=2)
        
        # Алгоритмы заполнения
        fill_frame = tk.LabelFrame(control_frame, text="Заполнение", padx=5, pady=5)
        fill_frame.pack(fill=tk.X, pady=5)
        tk.Button(fill_frame, text="Растр (упорядоченный список)", command=lambda: self.fill_polygon("ordered")).pack(fill=tk.X, pady=2)
        tk.Button(fill_frame, text="Растр (активные ребра)", command=lambda: self.fill_polygon("active")).pack(fill=tk.X, pady=2)
        tk.Button(fill_frame, text="Затравка (простой)", command=lambda: self.fill_polygon("simple")).pack(fill=tk.X, pady=2)
        tk.Button(fill_frame, text="Затравка (построчный)", command=lambda: self.fill_polygon("scanline")).pack(fill=tk.X, pady=2)
        
        # Триангуляция и диаграмма Вороного
        tk.Button(control_frame, text="Триангуляция Делоне", command=self.delaunay_triangulation).pack(fill=tk.X, pady=2)
        tk.Button(control_frame, text="Диаграмма Вороного", command=self.voronoi_diagram).pack(fill=tk.X, pady=2)
        
        # Очистка
        tk.Button(control_frame, text="Очистить все", command=self.clear_all).pack(fill=tk.X, pady=2)
        tk.Button(control_frame, text="Очистить все кроме полигона", command=self.clear_all_except_polygon).pack(fill=tk.X, pady=2)
        
        # Отладочное поле
        debug_frame = tk.LabelFrame(control_frame, text="Отладка", padx=5, pady=5)
        debug_frame.pack(fill=tk.X, pady=5)
        self.debug_textbox = tk.Text(debug_frame, height=10, width=30)
        self.debug_textbox.pack(fill=tk.BOTH, expand=True)
        tk.Button(debug_frame, text="Очистить отладку", command=self.clear_debug).pack(fill=tk.X, pady=2)
    
    def add_debug_text(self, text):
        self.debug_text += text + "\n"
        self.debug_textbox.delete(1.0, tk.END)
        self.debug_textbox.insert(tk.END, self.debug_text)
    
    def clear_debug(self):
        self.debug_text = ""
        self.debug_textbox.delete(1.0, tk.END)
    
    def on_canvas_click(self, event):
        x, y = event.x, event.y
        point = Point(x, y)
        
        if self.drawing_polygon:
            self.current_polygon.append(point)
            self.draw_point(x, y)
            
            if len(self.current_polygon) > 1:
                last_point = self.current_polygon[-2]
                self.canvas.create_line(last_point.x, last_point.y, x, y, fill=self.polygon_color)
        
        elif self.drawing_intersection_line:
            self.line_points.append(point)
            self.draw_point(x, y, color="green")
            
            if len(self.line_points) == 2:
                # Рисуем линию
                p1, p2 = self.line_points
                self.canvas.create_line(p1.x, p1.y, p2.x, p2.y, fill=self.line_color)
                
                # Проверяем пересечение с полигоном
                self.check_line_intersection()
                
                # Сбрасываем состояние
                self.line_points = []
                self.drawing_intersection_line = False
                self.canvas.delete(self.temp_line)
                self.temp_line = None
        else:
            self.points.append(point)
            self.draw_point(x, y)
    
    def on_canvas_motion(self, event):
        if self.drawing_polygon and len(self.current_polygon) > 0 and self.temp_line:
            x, y = event.x, event.y
            last_point = self.current_polygon[-1]
            self.canvas.delete(self.temp_line)
            self.temp_line = self.canvas.create_line(last_point.x, last_point.y, x, y, fill=self.polygon_color, dash=(2, 2))
        
        if self.drawing_intersection_line and len(self.line_points) == 1 and self.temp_line:
            x, y = event.x, event.y
            self.canvas.delete(self.temp_line)
            p1 = self.line_points[0]
            self.temp_line = self.canvas.create_line(p1.x, p1.y, x, y, fill=self.line_color, dash=(2, 2))
    
    def draw_point(self, x, y, color=None):
        color = color or self.point_color
        r = 3
        self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline=color)
    
    def start_polygon(self):
        self.drawing_polygon = True
        self.current_polygon = []
        self.add_debug_text("Начато рисование полигона. Кликайте по холсту для добавления вершин.")
    
    def finish_polygon(self):
        if len(self.current_polygon) < 3:
            messagebox.showerror("Ошибка", "Полигон должен иметь хотя бы 3 вершины")
            return
        
        self.drawing_polygon = False
        self.polygon = self.current_polygon.copy()
        
        # Замыкаем полигон
        first_point = self.current_polygon[0]
        last_point = self.current_polygon[-1]
        self.canvas.create_line(last_point.x, last_point.y, first_point.x, first_point.y, fill=self.polygon_color)
        
        self.add_debug_text(f"Полигон завершен. Вершины: {self.polygon}")
        self.canvas.delete(self.temp_line)
        self.temp_line = None
    
    def start_intersection_line(self):
        if len(self.polygon) < 3:
            messagebox.showerror("Ошибка", "Сначала создайте полигон")
            return
        
        self.drawing_intersection_line = True
        self.line_points = []
        self.add_debug_text("Рисуйте линию для проверки пересечения с полигоном. Кликните две точки.")
    
    def check_line_intersection(self):
        if len(self.line_points) != 2 or len(self.polygon) < 3:
            return
        
        line_p1, line_p2 = self.line_points
        intersections = []
        n = len(self.polygon)
        
        for i in range(n):
            poly_p1 = self.polygon[i]
            poly_p2 = self.polygon[(i+1)%n]
            
            # Проверяем пересечение отрезков
            intersect = self.segments_intersect(line_p1, line_p2, poly_p1, poly_p2)
            if intersect:
                # Находим точку пересечения
                x, y = self.find_intersection_point(line_p1, line_p2, poly_p1, poly_p2)
                intersections.append(Point(x, y))
                self.draw_point(x, y, color="magenta")
                self.canvas.create_oval(x-5, y-5, x+5, y+5, outline="magenta", width=2)
        
        if intersections:
            self.add_debug_text(f"Линия пересекает полигон в {len(intersections)} точках: {intersections}")
            messagebox.showinfo("Результат", f"Линия пересекает полигон в {len(intersections)} точках")
        else:
            self.add_debug_text("Линия не пересекает полигон")
            messagebox.showinfo("Результат", "Линия не пересекает полигон")
    
    def segments_intersect(self, p1, p2, p3, p4):
        def ccw(a, b, c):
            return (c.y - a.y) * (b.x - a.x) > (b.y - a.y) * (c.x - a.x)
        
        return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)
    
    def find_intersection_point(self, p1, p2, p3, p4):
        # Линия 1: p1 to p2, Линия 2: p3 to p4
        # Уравнения прямых: A1x + B1y = C1 и A2x + B2y = C2
        A1 = p2.y - p1.y
        B1 = p1.x - p2.x
        C1 = A1 * p1.x + B1 * p1.y
        
        A2 = p4.y - p3.y
        B2 = p3.x - p4.x
        C2 = A2 * p3.x + B2 * p3.y
        
        # Определитель
        det = A1 * B2 - A2 * B1
        
        if det == 0:
            # Линии параллельны
            return None
        else:
            x = (B2 * C1 - B1 * C2) / det
            y = (A1 * C2 - A2 * C1) / det
            return x, y
    
    def check_convexity(self):
        if len(self.polygon) < 3:
            messagebox.showerror("Ошибка", "Сначала создайте полигон")
            return
        
        convex, direction = self.is_convex(self.polygon)
        if convex:
            self.add_debug_text("Полигон выпуклый. Нормали направлены " + ("влево" if direction > 0 else "вправо"))
            messagebox.showinfo("Результат", "Полигон выпуклый")
        else:
            self.add_debug_text("Полигон вогнутый")
            messagebox.showinfo("Результат", "Полигон вогнутый")
    
    def is_convex(self, polygon):
        if len(polygon) < 3:
            return False, 0
        
        sign = 0
        n = len(polygon)
        
        for i in range(n):
            p1 = polygon[i]
            p2 = polygon[(i+1)%n]
            p3 = polygon[(i+2)%n]
            
            # Векторное произведение
            cross = (p2.x - p1.x)*(p3.y - p2.y) - (p2.y - p1.y)*(p3.x - p2.x)
            
            if cross == 0:
                continue  # коллинеарные точки
            
            if sign == 0:
                sign = cross
            elif cross * sign < 0:
                return False, 0  # вогнутый
        
        return True, sign
    
    def find_normals(self):
        if len(self.polygon) < 3:
            messagebox.showerror("Ошибка", "Сначала создайте полигон")
            return
        
        convex, _ = self.is_convex(self.polygon)
        if not convex:
            messagebox.showerror("Ошибка", "Нормали можно найти только для выпуклых полигонов")
            return
        
        normals = []
        n = len(self.polygon)
        
        for i in range(n):
            p1 = self.polygon[i]
            p2 = self.polygon[(i+1)%n]
            
            # Вектор ребра
            edge = Point(p2.x - p1.x, p2.y - p1.y)
            
            # Нормаль (перпендикулярный вектор)
            normal = Point(-edge.y, edge.x)
            
            # Проверяем направление нормали
            p3 = self.polygon[(i+2)%n]
            chord = Point(p3.x - p1.x, p3.y - p1.y)
            
            dot = normal.x * chord.x + normal.y * chord.y
            if dot < 0:
                normal.x *= -1
                normal.y *= -1
            
            normals.append(normal)
            
            # Рисуем нормаль (из середины ребра)
            mid_x = (p1.x + p2.x) / 2
            mid_y = (p1.y + p2.y) / 2
            end_x = mid_x + normal.x * 0.2
            end_y = mid_y + normal.y * 0.2
            
            self.canvas.create_line(mid_x, mid_y, end_x, end_y, fill="red", arrow=tk.LAST)
            
            self.add_debug_text(f"Нормаль к ребру {p1}-{p2}: ({normal.x}, {normal.y})")
        
        messagebox.showinfo("Результат", f"Найдено {len(normals)} нормалей")
    
    def graham_scan(self):
        if len(self.points) < 3:
            messagebox.showerror("Ошибка", "Нужно хотя бы 3 точки")
            return
        
        # Находим точку с минимальной y-координатой (и минимальной x, если есть совпадения)
        start_point = min(self.points, key=lambda p: (p.y, p.x))
        
        # Сортируем точки по полярному углу относительно start_point
        sorted_points = sorted(self.points, key=lambda p: (math.atan2(p.y - start_point.y, p.x - start_point.x), 
                                                          (p.x - start_point.x)**2 + (p.y - start_point.y)**2))
        
        # Удаляем дубликаты
        unique_points = []
        for p in sorted_points:
            if not unique_points or not (p.x == unique_points[-1].x and p.y == unique_points[-1].y):
                unique_points.append(p)
        
        # Если все точки коллинеарны
        if len(unique_points) < 3:
            self.convex_hull = unique_points
            self.draw_convex_hull()
            return
        
        # Инициализация стека
        stack = [unique_points[0], unique_points[1], unique_points[2]]
        
        # Алгоритм Грэхема
        for i in range(3, len(unique_points)):
            while len(stack) > 1 and self.orientation(stack[-2], stack[-1], unique_points[i]) <= 0:
                stack.pop()
            stack.append(unique_points[i])
        
        self.convex_hull = stack
        self.draw_convex_hull()
        self.add_debug_text(f"Выпуклая оболочка (Грэхем): {self.convex_hull}")
    
    def jarvis_march(self):
        if len(self.points) < 3:
            messagebox.showerror("Ошибка", "Нужно хотя бы 3 точки")
            return
        
        # Находим точку с минимальной y-координатой (и минимальной x, если есть совпадения)
        start_point = min(self.points, key=lambda p: (p.y, p.x))
        
        hull = [start_point]
        current_point = start_point
        
        while True:
            next_point = self.points[0]
            if next_point == current_point:
                next_point = self.points[1]
            
            for point in self.points:
                if point == current_point:
                    continue
                
                cross = self.cross_product(current_point, next_point, point)
                if cross > 0 or (cross == 0 and self.distance(current_point, point) > self.distance(current_point, next_point)):
                    next_point = point
            
            if next_point == start_point:
                break
            
            hull.append(next_point)
            current_point = next_point
        
        self.convex_hull = hull
        self.draw_convex_hull()
        self.add_debug_text(f"Выпуклая оболочка (Джарвис): {self.convex_hull}")
    
    def draw_convex_hull(self):
        # Очищаем предыдущую оболочку
        self.canvas.delete("convex_hull")
        
        if len(self.convex_hull) < 2:
            return
        
        # Рисуем точки оболочки
        for point in self.convex_hull:
            self.draw_point(point.x, point.y, color=self.convex_hull_color)
        
        # Рисуем ребра оболочки
        for i in range(len(self.convex_hull)):
            p1 = self.convex_hull[i]
            p2 = self.convex_hull[(i+1)%len(self.convex_hull)]
            self.canvas.create_line(p1.x, p1.y, p2.x, p2.y, fill=self.convex_hull_color, tags="convex_hull", width=2)
    
    def orientation(self, p, q, r):
        val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
        if val == 0:
            return 0  # коллинеарны
        return 1 if val > 0 else 2  # по или против часовой стрелки
    
    def cross_product(self, a, b, c):
        return (b.x - a.x)*(c.y - a.y) - (b.y - a.y)*(c.x - a.x)
    
    def distance(self, a, b):
        return math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2)
    
    def check_point_in_polygon(self):
        if len(self.polygon) < 3:
            messagebox.showerror("Ошибка", "Сначала создайте полигон")
            return
        
        # Запрашиваем координаты точки
        x = simpledialog.askinteger("X координата", "Введите X координату точки:")
        if x is None:
            return
        
        y = simpledialog.askinteger("Y координата", "Введите Y координату точки:")
        if y is None:
            return
        
        point = Point(x, y)
        self.draw_point(x, y, color="magenta")
        
        # Проверяем принадлежность точки полигону
        inside = self.point_in_polygon(point, self.polygon)
        
        if inside:
            self.add_debug_text(f"Точка ({x}, {y}) находится внутри полигона")
            messagebox.showinfo("Результат", "Точка внутри полигона")
        else:
            self.add_debug_text(f"Точка ({x}, {y}) находится вне полигона")
            messagebox.showinfo("Результат", "Точка вне полигона")
    
    def point_in_polygon(self, point, polygon):
        n = len(polygon)
        inside = False
        
        p1 = polygon[0]
        for i in range(1, n + 1):
            p2 = polygon[i % n]
            
            if point.y > min(p1.y, p2.y):
                if point.y <= max(p1.y, p2.y):
                    if point.x <= max(p1.x, p2.x):
                        if p1.y != p2.y:
                            xinters = (point.y - p1.y) * (p2.x - p1.x) / (p2.y - p1.y) + p1.x
                        
                        if p1.x == p2.x or point.x <= xinters:
                            inside = not inside
            p1 = p2
        
        return inside
    
    def fill_polygon(self, method):
        if len(self.polygon) < 3:
            messagebox.showerror("Ошибка", "Сначала создайте полигон")
            return
        
        self.canvas.delete("fill")
        
        if method == "ordered":
            self.fill_ordered_edge_list()
        elif method == "active":
            self.fill_active_edge_list()
        elif method == "simple":
            self.fill_simple_seed()
        elif method == "scanline":
            self.fill_scanline_seed()
    
    def fill_ordered_edge_list(self):
        self.add_debug_text("Заполнение: алгоритм растровой развертки с упорядоченным списком ребер")
        
        # Находим минимальную и максимальную y-координаты
        min_y = min(p.y for p in self.polygon)
        max_y = max(p.y for p in self.polygon)
        
        # Создаем список ребер
        edges = []
        n = len(self.polygon)
        
        for i in range(n):
            p1 = self.polygon[i]
            p2 = self.polygon[(i+1)%n]
            
            if p1.y != p2.y:  # Игнорируем горизонтальные ребра
                edge = Edge(p1, p2)
                edges.append(edge)
        
        # Для каждой сканирующей строки находим точки пересечения
        intersections = []
        
        for y in range(min_y, max_y + 1):
            scanline_intersections = []
            
            for edge in edges:
                p1, p2 = edge.p1, edge.p2
                
                # Проверяем, пересекает ли ребро сканирующую строку
                if (p1.y <= y < p2.y) or (p2.y <= y < p1.y):
                    if p1.y == p2.y:
                        continue  # горизонтальное ребро
                    
                    # Вычисляем x координату пересечения
                    if p1.y == p2.y:
                        x = p1.x
                    else:
                        x = p1.x + (y - p1.y) * (p2.x - p1.x) / (p2.y - p1.y)
                    
                    scanline_intersections.append(x)
            
            # Сортируем точки пересечения
            scanline_intersections.sort()
            
            # Заполняем промежутки между точками пересечения
            for i in range(0, len(scanline_intersections), 2):
                if i+1 >= len(scanline_intersections):
                    break
                
                x1 = int(scanline_intersections[i])
                x2 = int(scanline_intersections[i+1])
                
                self.canvas.create_line(x1, y, x2, y, fill=self.fill_color, tags="fill")
        
        self.add_debug_text("Заполнение завершено")
    
    def fill_active_edge_list(self):
        self.add_debug_text("Заполнение: алгоритм растровой развертки с активными ребрами")
        
        # Находим минимальную и максимальную y-координаты
        min_y = min(p.y for p in self.polygon)
        max_y = max(p.y for p in self.polygon)
        
        # Создаем список ребер
        edges = []
        n = len(self.polygon)
        
        for i in range(n):
            p1 = self.polygon[i]
            p2 = self.polygon[(i+1)%n]
            
            if p1.y != p2.y:  # Игнорируем горизонтальные ребра
                if p1.y < p2.y:
                    edge = Edge(p1, p2)
                else:
                    edge = Edge(p2, p1)
                edges.append(edge)
        
        # Сортируем ребра по минимальной y-координате
        edges.sort(key=lambda e: e.p1.y)
        
        # Инициализация списка активных ребер (AET)
        aet = []
        current_y = min_y
        edge_index = 0
        
        while current_y <= max_y:
            # Добавляем ребра, которые начинаются на текущей строке
            while edge_index < len(edges) and edges[edge_index].p1.y == current_y:
                edge = edges[edge_index]
                aet.append({
                    'x': edge.p1.x,
                    'dx': (edge.p2.x - edge.p1.x) / (edge.p2.y - edge.p1.y),
                    'ymax': edge.p2.y
                })
                edge_index += 1
            
            # Удаляем ребра, которые заканчиваются на текущей строке
            aet = [edge for edge in aet if edge['ymax'] > current_y]
            
            # Сортируем активные ребра по x
            aet.sort(key=lambda edge: edge['x'])
            
            # Заполняем промежутки между ребрами
            for i in range(0, len(aet), 2):
                if i+1 >= len(aet):
                    break
                
                x1 = int(aet[i]['x'])
                x2 = int(aet[i+1]['x'])
                
                self.canvas.create_line(x1, current_y, x2, current_y, fill=self.fill_color, tags="fill")
            
            # Обновляем x координаты для следующей строки
            for edge in aet:
                edge['x'] += edge['dx']
            
            current_y += 1
        
        self.add_debug_text("Заполнение завершено")
    
    def fill_simple_seed(self):
        self.add_debug_text("Заполнение: простой алгоритм заполнения с затравкой")
        
        # Находим точку внутри полигона (центр масс)
        if not self.polygon:
            return
        
        cx = sum(p.x for p in self.polygon) / len(self.polygon)
        cy = sum(p.y for p in self.polygon) / len(self.polygon)
        
        seed = Point(int(cx), int(cy))
        self.draw_point(seed.x, seed.y, color="magenta")
        
        # Проверяем, что затравка внутри полигона
        if not self.point_in_polygon(seed, self.polygon):
            messagebox.showerror("Ошибка", "Не удалось найти точку внутри полигона")
            return
        
        # Создаем стек и добавляем затравку
        stack = [seed]
        filled = set()
        
        while stack:
            point = stack.pop()
            x, y = point.x, point.y
            
            # Пропускаем уже заполненные точки и точки вне холста
            if (x, y) in filled or x < 0 or x >= 800 or y < 0 or y >= 600:
                continue
            
            # Проверяем, что точка внутри полигона
            if not self.point_in_polygon(point, self.polygon):
                continue
            
            # Заполняем точку
            self.canvas.create_rectangle(x, y, x+1, y+1, fill=self.fill_color, outline=self.fill_color, tags="fill")
            filled.add((x, y))
            
            # Добавляем соседние точки в стек
            stack.append(Point(x+1, y))
            stack.append(Point(x-1, y))
            stack.append(Point(x, y+1))
            stack.append(Point(x, y-1))
        
        self.add_debug_text(f"Заполнено {len(filled)} пикселей")
    
    def fill_scanline_seed(self):
        self.add_debug_text("Заполнение: построчный алгоритм заполнения с затравкой")
        
        # Находим точку внутри полигона (центр масс)
        if not self.polygon:
            return
        
        cx = sum(p.x for p in self.polygon) / len(self.polygon)
        cy = sum(p.y for p in self.polygon) / len(self.polygon)
        
        seed = Point(int(cx), int(cy))
        self.draw_point(seed.x, seed.y, color="magenta")
        
        # Проверяем, что затравка внутри полигона
        if not self.point_in_polygon(seed, self.polygon):
            messagebox.showerror("Ошибка", "Не удалось найти точку внутри полигона")
            return
        
        # Создаем стек и добавляем затравку
        stack = [seed]
        filled = set()
        
        while stack:
            point = stack.pop()
            x, y = point.x, point.y
            
            # Пропускаем уже заполненные точки и точки вне холста
            if (x, y) in filled or x < 0 or x >= 800 or y < 0 or y >= 600:
                continue
            
            # Находим крайний левый пиксел в строке
            left = x
            while left >= 0 and self.point_in_polygon(Point(left, y), self.polygon):
                left -= 1
            left += 1
            
            # Находим крайний правый пиксел в строке
            right = x
            while right < 800 and self.point_in_polygon(Point(right, y), self.polygon):
                right += 1
            right -= 1
            
            # Заполняем строку
            self.canvas.create_line(left, y, right, y, fill=self.fill_color, tags="fill")
            
            # Добавляем в заполненные
            for px in range(left, right+1):
                filled.add((px, y))
            
            # Проверяем строку выше
            self.check_scanline_seed_row(left, right, y-1, stack, filled)
            
            # Проверяем строку ниже
            self.check_scanline_seed_row(left, right, y+1, stack, filled)
        
        self.add_debug_text(f"Заполнено {len(filled)} пикселей")
    
    def check_scanline_seed_row(self, left, right, y, stack, filled):
        if y < 0 or y >= 600:
            return
        
        in_segment = False
        for x in range(left, right+1):
            if (x, y) in filled:
                in_segment = False
                continue
            
            if self.point_in_polygon(Point(x, y), self.polygon):
                if not in_segment:
                    stack.append(Point(x, y))
                    in_segment = True
            else:
                in_segment = False
    
    def delaunay_triangulation(self):
        if len(self.points) < 3:
            messagebox.showerror("Ошибка", "Нужно хотя бы 3 точки")
            return
        
        # Удаляем дубликаты
        unique_points = list(set(self.points))
        
        # Если все точки коллинеарны
        if self.are_points_collinear(unique_points):
            messagebox.showerror("Ошибка", "Точки коллинеарны, триангуляция невозможна")
            return
        
        # Создаем супертреугольник, который содержит все точки
        min_x = min(p.x for p in unique_points)
        max_x = max(p.x for p in unique_points)
        min_y = min(p.y for p in unique_points)
        max_y = max(p.y for p in unique_points)
        
        dx = max_x - min_x
        dy = max_y - min_y
        delta = max(dx, dy) * 2
        
        p1 = Point(min_x - delta, min_y - delta)
        p2 = Point(max_x + delta, min_y - delta)
        p3 = Point(min_x + dx/2, max_y + delta)
        
        triangles = [(p1, p2, p3)]
        
        # Добавляем точки по одной
        for point in unique_points:
            bad_triangles = []
            
            # Находим все треугольники, чья описанная окружность содержит текущую точку
            for triangle in triangles:
                a, b, c = triangle
                if self.in_circumcircle(point, a, b, c):
                    bad_triangles.append(triangle)
            
            polygon = []
            
            # Находим границу многоугольника
            for triangle in bad_triangles:
                for edge in [(triangle[0], triangle[1]), 
                            (triangle[1], triangle[2]), 
                            (triangle[2], triangle[0])]:
                    shared = False
                    for other in bad_triangles:
                        if triangle == other:
                            continue
                        
                        if (edge[0] in other and edge[1] in other):
                            shared = True
                            break
                    
                    if not shared:
                        polygon.append(edge)
            
            # Удаляем плохие треугольники
            for triangle in bad_triangles:
                if triangle in triangles:
                    triangles.remove(triangle)
            
            # Создаем новые треугольники из текущей точки и каждого ребра многоугольника
            for edge in polygon:
                triangles.append((edge[0], edge[1], point))
        
        # Удаляем треугольники, содержащие вершины супертреугольника
        final_triangles = []
        for triangle in triangles:
            if p1 not in triangle and p2 not in triangle and p3 not in triangle:
                final_triangles.append(triangle)
        
        self.triangles = final_triangles
        self.draw_triangles()
        self.add_debug_text(f"Триангуляция Делоне: {len(self.triangles)} треугольников")
    
    def are_points_collinear(self, points):
        if len(points) < 3:
            return True
        
        p1, p2 = points[0], points[1]
        for p3 in points[2:]:
            if self.cross_product(p1, p2, p3) != 0:
                return False
        return True
    
    def in_circumcircle(self, p, a, b, c):
        # Проверяем, находится ли точка p внутри описанной окружности треугольника abc
        ax = a.x - p.x
        ay = a.y - p.y
        bx = b.x - p.x
        by = b.y - p.y
        cx = c.x - p.x
        cy = c.y - p.y
        
        det = (ax*ax + ay*ay) * (bx*cy - by*cx) - \
              (bx*bx + by*by) * (ax*cy - ay*cx) + \
              (cx*cx + cy*cy) * (ax*by - ay*bx)
        
        return det > 0
    
    def draw_triangles(self):
        self.canvas.delete("triangles")
        
        for triangle in self.triangles:
            p1, p2, p3 = triangle
            self.canvas.create_line(p1.x, p1.y, p2.x, p2.y, fill=self.triangle_color, tags="triangles")
            self.canvas.create_line(p2.x, p2.y, p3.x, p3.y, fill=self.triangle_color, tags="triangles")
            self.canvas.create_line(p3.x, p3.y, p1.x, p1.y, fill=self.triangle_color, tags="triangles")
    
    def voronoi_diagram(self):
        if not self.triangles and len(self.points) >= 3:
            self.delaunay_triangulation()
        
        if not self.triangles:
            messagebox.showerror("Ошибка", "Сначала выполните триангуляцию Делоне")
            return
        
        self.canvas.delete("voronoi")
        
        # Словарь для хранения центров окружностей по треугольникам
        centers = {}
        
        # Находим центры описанных окружностей для каждого треугольника
        for triangle in self.triangles:
            a, b, c = triangle
            center = self.circumcenter(a, b, c)
            centers[triangle] = center
        
        # Строим ребра диаграммы Вороного между центрами соседних треугольников
        for i in range(len(self.triangles)):
            for j in range(i+1, len(self.triangles)):
                tri1 = self.triangles[i]
                tri2 = self.triangles[j]
                
                # Проверяем, имеют ли треугольники общее ребро
                common_points = set(tri1) & set(tri2)
                if len(common_points) >= 2:
                    # Рисуем линию между центрами
                    center1 = centers[tri1]
                    center2 = centers[tri2]
                    
                    if center1 and center2:
                        self.canvas.create_line(center1.x, center1.y, 
                                              center2.x, center2.y, 
                                              fill=self.voronoi_color, tags="voronoi")
        
        # Рисуем центры окружностей
        for center in centers.values():
            if center:
                self.draw_point(center.x, center.y, color="black")
        
        self.add_debug_text("Диаграмма Вороного построена")
    
    def circumcenter(self, a, b, c):
        # Находим центр описанной окружности для треугольника abc
        d = 2 * (a.x*(b.y - c.y) + b.x*(c.y - a.y) + c.x*(a.y - b.y))
        
        if d == 0:
            return None  # коллинеарные точки
        
        ux = ((a.x*a.x + a.y*a.y)*(b.y - c.y) + (b.x*b.x + b.y*b.y)*(c.y - a.y) + (c.x*c.x + c.y*c.y)*(a.y - b.y)) / d
        uy = ((a.x*a.x + a.y*a.y)*(c.x - b.x) + (b.x*b.x + b.y*b.y)*(a.x - c.x) + (c.x*c.x + c.y*c.y)*(b.x - a.x)) / d
        
        return Point(ux, uy)
    
    def clear_all(self):
        self.canvas.delete("all")
        self.points = []
        self.polygon = []
        self.current_polygon = []
        self.convex_hull = []
        self.triangles = []
        self.line_points = []
        self.debug_text = ""
        self.debug_textbox.delete(1.0, tk.END)
        self.drawing_polygon = False
        self.drawing_intersection_line = False
        self.line_start = None
        self.temp_line = None
        self.temp_point = None
    
    def clear_all_except_polygon(self):
        # Сохраняем текущий полигон
        saved_polygon = self.polygon.copy()
        saved_current_polygon = self.current_polygon.copy()
        
        # Очищаем все
        self.canvas.delete("all")
        self.points = []
        self.convex_hull = []
        self.triangles = []
        self.line_points = []
        self.debug_text = ""
        self.debug_textbox.delete(1.0, tk.END)
        self.drawing_polygon = False
        self.drawing_intersection_line = False
        self.line_start = None
        self.temp_line = None
        self.temp_point = None
        
        # Восстанавливаем полигон
        self.polygon = saved_polygon
        self.current_polygon = saved_current_polygon
        
        # Перерисовываем полигон
        if len(self.polygon) >= 3:
            # Рисуем точки
            for point in self.polygon:
                self.draw_point(point.x, point.y)
            
            # Рисуем линии
            for i in range(len(self.polygon)):
                p1 = self.polygon[i]
                p2 = self.polygon[(i+1)%len(self.polygon)]
                self.canvas.create_line(p1.x, p1.y, p2.x, p2.y, fill=self.polygon_color)
        
        self.add_debug_text("Очищено все, кроме полигона")

if __name__ == "__main__":
    root = tk.Tk()
    app = PolygonEditor(root)
    root.mainloop()