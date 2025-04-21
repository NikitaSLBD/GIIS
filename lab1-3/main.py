import tkinter as tk

from tkinter import ttk
from managers.drawman import DrawManager
from managers.debugger import DebugManager

class GraphicsEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Графический редактор")
        
        # Менеджеры компонентов
        self.draw = DrawManager(self)
        self.debug = DebugManager(self)
        
        # Переменные состояния
        self.current_tool = None
        self.current_algorithm = None
        
        # Настройка интерфейса
        self.setup_ui()
        
        # Инициализация компонентов
        self.draw.setup_canvas()
        self.debug.setup_controls()
    
    def setup_ui(self):
        # Панель инструментов
        ttk.Label(self.root, text="Инструменты:").grid(row=0, column=0, sticky="w")
        ttk.Button(self.root, text="Отрезок", command=lambda: self.set_tool("line")).grid(row=0, column=1, sticky="ew")
        ttk.Button(self.root, text="Кривые", command=lambda: self.set_tool("curve")).grid(row=0, column=2, sticky="ew")
        ttk.Button(self.root, text="Параметрические кривые", command=lambda: self.set_tool("parametric")).grid(row=0, column=3, sticky="ew")
        
        # Основные кнопки
        ttk.Button(self.root, text="Очистить", command=self.clear_all).grid(row=3, column=0, sticky="ew")
    
    def set_tool(self, tool):
        self.current_tool = tool
        self.draw.clear_points()
        self.log(f"Выбран инструмент: {tool}")
        
        if tool == "line":
            self.show_algorithm_menu(["ЦДА", "Брезенхем", "Ву"])
        elif tool == "curve":
            self.show_algorithm_menu(["Окружность", "Эллипс", "Гипербола", "Парабола"])
        elif tool == "parametric":
            self.show_algorithm_menu(["Эрмит", "Безье", "B-сплайн"])
    
    def show_algorithm_menu(self, algorithms):
        menu = tk.Menu(self.root, tearoff=0)
        for algo in algorithms:
            menu.add_command(label=algo, command=lambda a=algo: self.set_algorithm(a))
        
        try:
            menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
        finally:
            menu.grab_release()
    
    def set_algorithm(self, algorithm):
        self.current_algorithm = algorithm
        self.log(f"Выбран алгоритм: {algorithm}")
        self.draw.clear_points()
    
    def clear_all(self):
        self.draw.clear_canvas()
        self.debug.reset()
        self.log("Холст и состояние очищены")
    
    def log(self, message):
        self.debug.log_message(message)

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphicsEditor(root)
    root.mainloop()