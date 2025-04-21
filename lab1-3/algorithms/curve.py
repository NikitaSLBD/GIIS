import math

class CurveAlgorithms:
    def __init__(self, logger):
        self.log = logger
    
    def circle(self, xc, yc, r):
        """Алгоритм Брезенхема для окружности"""
        def plot_circle_points(x, y):
            points = [
                (xc + x, yc + y), (xc - x, yc + y),
                (xc + x, yc - y), (xc - x, yc - y),
                (xc + y, yc + x), (xc - y, yc + x),
                (xc + y, yc - x), (xc - y, yc - x)
            ]
            for i, p in enumerate(points):
                self.log(f"Окружность: точка {i + 1} {p}")
            return points
        
        x = 0
        y = r
        d = 3 - 2 * r
        
        all_points = []
        all_points.extend(plot_circle_points(x, y))
        
        while y >= x:
            x += 1
            if d > 0:
                y -= 1
                d = d + 4 * (x - y) + 10
            else:
                d = d + 4 * x + 6
            all_points.extend(plot_circle_points(x, y))
        
        return all_points
    
    def ellipse(self, xc, yc, a, b):
        """Алгоритм для эллипса"""
        points = []
        for angle in range(0, 720, 1):
            rad = math.radians(angle)
            x = xc + a * math.cos(rad)
            y = yc + b * math.sin(rad)
            points.append((round(x), round(y)))
            self.log(f"Эллипс: точка {angle + 1} ({round(x)}, {round(y)})")
        
        return points
    
    def hyperbola(self, xc, yc, a, b, steps=500):
        """Алгоритм построения гиперболы x²/a² - y²/b² = 1"""
        points = []
        
        # Правая ветвь
        x_start = a
        x_end = xc + 5 * a  # Ограничиваем для визуализации
        
        for i in range(steps + 1):
            x = x_start + (x_end - x_start) * i / steps
            y = b * math.sqrt((x/a)**2 - 1)
            points.append((round(x + xc), round(y + yc)))
            points.append((round(x + xc), round(-y + yc)))
            self.log(f"Гипербола: точка {i + 1} ({round(x + xc)}, {round(y + yc)})")
        
        # Левая ветвь (зеркальное отражение)
        for i in range(steps + 1):
            x = -x_start - (x_end - x_start) * i / steps
            y = b * math.sqrt((x/a)**2 - 1)
            points.append((round(x + xc), round(y + yc)))
            points.append((round(x + xc), round(-y + yc)))
            self.log(f"Гипербола: точка {i + 1} ({round(x + xc)}, {round(y + yc)})")
        
        return points
    
    def parabola(self, xc, yc, p, steps=500):
        """Алгоритм построения параболы y² = 2px"""
        points = []
        
        # Верхняя и нижняя ветви
        x_start = 0
        x_end = xc + 5 * p  # Ограничиваем для визуализации
        
        for i in range(steps + 1):
            x = x_start + (x_end - x_start) * i / steps
            y = math.sqrt(2 * p * x)
            points.append((round(x + xc), round(y + yc)))
            points.append((round(x + xc), round(-y + yc)))
            self.log(f"Парабола: точка {i + 1} ({round(x + xc)}, {round(y + yc)})")
        
        return points