import tkinter as tk
from tkinter import ttk

class DebugManager:
    def __init__(self, editor):
        self.editor = editor
        self.debug_mode = False
        self.animation_speed = 0
        self.animation_id = None
        self.steps = []
        self.step_index = 0
        
        # Элементы интерфейса
        self.debug_btn = None
        self.speed_entry = None
        self.console = None
    
    def setup_controls(self):
        # Кнопка отладки
        self.debug_btn = ttk.Button(self.editor.root, text="Режим отладки", command=self.toggle_debug)
        self.debug_btn.grid(row=3, column=1, sticky="ew")
        
        # Кнопки управления
        ttk.Button(self.editor.root, text="Шаг вперед", command=self.step_forward).grid(row=3, column=2, sticky="ew")
        ttk.Button(self.editor.root, text="Шаг назад", command=self.step_backward).grid(row=3, column=3, sticky="ew")
        
        # Поле скорости
        self.speed_entry = ttk.Entry(self.editor.root, width=5)
        self.speed_entry.insert(0, "0")
        ttk.Label(self.editor.root, text="Скорость (пкс/с):").grid(row=3, column=4, sticky='e')
        self.speed_entry.grid(row=3, column=5, sticky="w", padx=5)
        
        
        # Консоль
        self.console = tk.Text(self.editor.root, height=10, state='disabled')
        self.console.grid(row=2, column=0, columnspan=6, sticky="ew")
    
    def set_steps(self, steps):
        self.steps = steps
        self.step_index = 0
        self.update_display()
    
    def toggle_debug(self):
        self.debug_mode = not self.debug_mode
        status = "включен" if self.debug_mode else "выключен"
        self.debug_btn.config(text=f"Режим отладки ({status})")
        self.log_message(f"Режим отладки {status}")
        
        if self.debug_mode:
            self.start_animation()
        else:
            self.stop_animation()
            self.draw_all_steps()
    
    def start_animation(self):
        self.stop_animation()
        self.animation_speed = self.get_speed()
        
        if self.animation_speed > 0 and self.step_index < len(self.steps) - 1:
            delay = int(1000 / self.animation_speed)
            self.animation_id = self.editor.root.after(delay, self.animation_step)
    
    def animation_step(self):
        if self.step_index < len(self.steps) - 1:
            self.step_forward()
            if self.step_index < len(self.steps) - 1:
                delay = int(1000 / self.animation_speed)
                self.animation_id = self.editor.root.after(delay, self.animation_step)
    
    def stop_animation(self):
        if self.animation_id:
            self.editor.root.after_cancel(self.animation_id)
            self.animation_id = None
    
    def step_forward(self):
        if not self.debug_mode or not self.steps:
            return
        
        if self.step_index < len(self.steps) - 1:
            self.step_index += 1
            self.redraw_current()
        else:
            self.log_message("Достигнут конец построения")
            self.stop_animation()
    
    def step_backward(self):
        if not self.debug_mode or not self.steps:
            return
        
        if self.step_index > 0:
            self.step_index -= 1
            self.redraw_current()
        else:
            self.log_message("Достигнуто начало построения")
    
    def redraw_current(self):
        self.editor.draw.canvas.delete("curve")
        for i in range(self.step_index + 1):
            x, y, intensity = self.steps[i]
            gray = int(255 * (1 - intensity))
            color = f"#{gray:02x}{gray:02x}{gray:02x}"
            self.editor.draw.canvas.create_rectangle(x, y, x+1, y+1, fill=color, outline="", tags="curve")
        
        if self.step_index < len(self.steps):
            current = self.steps[self.step_index]
            self.log_message(f"Шаг {self.step_index}: точка {current[:2]}, интенсивность {current[2]:.2f}")
    
    def draw_all_steps(self):
        self.editor.draw.canvas.delete("curve")
        for x, y, intensity in self.steps:
            gray = int(255 * (1 - intensity))
            color = f"#{gray:02x}{gray:02x}{gray:02x}"
            self.editor.draw.canvas.create_rectangle(x, y, x+1, y+1, fill=color, outline="", tags="curve")
        self.log_message(f"Построено {len(self.steps)} точек")
    
    def update_display(self):
        if self.debug_mode:
            self.redraw_current()
            self.start_animation()
        else:
            self.draw_all_steps()
    
    def get_speed(self):
        try:
            speed = int(self.speed_entry.get())
            return max(0, min(speed, 100))
        except ValueError:
            return 0
    
    def log_message(self, message):
        self.console.config(state='normal')
        self.console.insert('end', message + '\n')
        self.console.config(state='disabled')
        self.console.see('end')
    
    def reset(self):
        self.stop_animation()
        self.steps = []
        self.step_index = 0