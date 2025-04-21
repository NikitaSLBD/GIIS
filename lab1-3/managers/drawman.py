import tkinter as tk
from tkinter import messagebox

from algorithms.line import LineAlgorithms
from algorithms.curve import CurveAlgorithms
from algorithms.parametric import ParametricAlgorithms

class DrawManager:
    def __init__(self, editor):
        self.editor = editor
        self.canvas = None
        self.points = []
        self.point_markers = []
        self.selected_point = None
        self.dragging = False
        
        # Инициализация алгоритмов
        self.line_algo = LineAlgorithms(self.log)
        self.curve_algo = CurveAlgorithms(self.log)
        self.parametric_algo = ParametricAlgorithms(self.log)
    
    def setup_canvas(self):
        self.canvas = tk.Canvas(self.editor.root, width=800, height=600, bg="white")
        self.canvas.grid(row=1, column=0, columnspan=6, sticky="nsew")
        
        # Привязка событий
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
    
    def on_canvas_click(self, event):
        if self.dragging:
            return
            
        # Проверка клика по существующей точке
        for i, (marker, (x, y)) in enumerate(zip(self.point_markers, self.points)):
            if abs(x - event.x) <= 5 and abs(y - event.y) <= 5:
                self.selected_point = i
                self.dragging = True
                return
        
        # Добавление новой точки
        if not self.editor.current_tool or not self.editor.current_algorithm:
            messagebox.showwarning("Предупреждение", "Сначала выберите инструмент и алгоритм")
            return
        
        self.add_point(event.x, event.y)
        self.try_draw()
    
    def on_canvas_drag(self, event):
        if self.selected_point is not None and self.dragging:
            index = self.selected_point
            old_x, old_y = self.points[index]
            dx = event.x - old_x
            dy = event.y - old_y
            
            self.canvas.move(self.point_markers[index], dx, dy)
            self.points[index] = (event.x, event.y)
            self.redraw()
    
    def on_canvas_release(self, event):
        if self.selected_point is not None:
            self.log(f"Точка {self.selected_point} перемещена в ({event.x}, {event.y})")
            self.selected_point = None
            self.dragging = False
    
    def add_point(self, x, y):
        self.points.append((x, y))
        marker = self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="gray", tags="point")
        self.point_markers.append(marker)
        self.log(f"Добавлена точка: ({x}, {y})")
    
    def try_draw(self):
        tool = self.editor.current_tool
        algo = self.editor.current_algorithm
        
        if tool == "line" and len(self.points) == 2:
            self.draw_line()
        elif tool == "curve" and len(self.points) == 2:
            self.draw_curve()
        elif tool == "parametric":
            if (algo in ["Эрмит", "Безье"] and len(self.points) == 4) or \
               (algo == "B-сплайн" and len(self.points) >= 4):
                self.draw_parametric()
    
    def draw_line(self):
        x1, y1 = self.points[0]
        x2, y2 = self.points[1]
        
        if self.editor.current_algorithm == "ЦДА":
            steps = [(x, y, 1) for x, y in self.line_algo.dda(x1, y1, x2, y2)]
        elif self.editor.current_algorithm == "Брезенхем":
            steps = [(x, y, 1) for x, y in self.line_algo.bresenham(x1, y1, x2, y2)]
        elif self.editor.current_algorithm == "Ву":
            steps = self.line_algo.wu(x1, y1, x2, y2)
        
        self.editor.debug.set_steps(steps)
    
    def draw_curve(self):
        x1, y1 = self.points[0]
        x2, y2 = self.points[1]
        
        if self.editor.current_algorithm == "Окружность":
            r = int(((x2 - x1)**2 + (y2 - y1)**2)**0.5)
            steps = [(x, y, 1) for x, y in self.curve_algo.circle(x1, y1, r)]
        elif self.editor.current_algorithm == "Эллипс":
            a = abs(x2 - x1)
            b = abs(y2 - y1)
            steps = [(x, y, 1) for x, y in self.curve_algo.ellipse(x1, y1, a, b)]
        elif self.editor.current_algorithm == "Гипербола":
            a = abs(x2 - x1)
            b = abs(y2 - y1)
            steps = [(x, y, 1) for x, y in self.curve_algo.hyperbola(x1, y1, a, b)]
        elif self.editor.current_algorithm == "Парабола":
            p = abs(x2 - x1)
            steps = [(x, y, 1) for x, y in self.curve_algo.parabola(x1, y1, p)]
        
        self.editor.debug.set_steps(steps if steps else [])
    
    def draw_parametric(self):
        if self.editor.current_algorithm == "Эрмит":
            p1, p4, r1, r4 = self.points
            steps = [(x, y, 1) for x, y in self.parametric_algo.hermite(p1, p4, (r1[0]-p1[0], r1[1]-p1[1]), (r4[0]-p4[0], r4[1]-p4[1]))]
        elif self.editor.current_algorithm == "Безье":
            steps = [(x, y, 1) for x, y in self.parametric_algo.bezier(*self.points)]
        elif self.editor.current_algorithm == "B-сплайн":
            steps = [(x, y, 1) for x, y in self.parametric_algo.bspline(self.points)]
        
        self.editor.debug.set_steps(steps)
    
    def redraw(self):
        # Сохраняем текущий режим отладки
        debug_mode = self.editor.debug.debug_mode
        current_step = self.editor.debug.step_index
        
        # Удаляем только кривые, но не точки
        self.canvas.delete("curve")
        
        # Перерисовываем кривую
        self.try_draw()
        
        # Восстанавливаем состояние отладки
        if debug_mode:
            self.editor.debug.debug_mode = True
            self.editor.debug.step_index = min(current_step, len(self.editor.debug.steps)-1)
            self.editor.debug.redraw_current()
    
    def clear_points(self):
        for marker in self.point_markers:
            self.canvas.delete(marker)
        self.points = []
        self.point_markers = []
        self.selected_point = None
    
    def clear_canvas(self):
        self.canvas.delete("all")
        self.clear_points()
    
    def log(self, message):
        self.editor.debug.log_message(message)