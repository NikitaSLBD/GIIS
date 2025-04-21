class LineAlgorithms:
    def __init__(self, logger):
        self.log = logger
    
    def dda(self, x1, y1, x2, y2):
        """Цифровой дифференциальный анализатор"""
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))
        
        x_inc = dx / steps
        y_inc = dy / steps
        
        x = x1
        y = y1
        
        points = []
        for i in range(steps + 1):
            points.append((round(x), round(y)))
            self.log(f"ЦДА шаг {i}: ({round(x)}, {round(y)})")
            x += x_inc
            y += y_inc
        
        return points
    
    def bresenham(self, x1, y1, x2, y2):
        """Алгоритм Брезенхема для отрезков"""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        steep = dy > dx
        
        if steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
            dx, dy = dy, dx
        
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        
        dx = x2 - x1
        dy = abs(y2 - y1)
        error = dx // 2
        ystep = 1 if y1 < y2 else -1
        y = y1
        
        points = []
        for x in range(x1, x2 + 1):
            coord = (y, x) if steep else (x, y)
            points.append(coord)
            self.log(f"Брезенхем шаг {x-x1}: {coord}")
            error -= dy
            if error < 0:
                y += ystep
                error += dx
        
        return points
    
    def wu(self, x1, y1, x2, y2):
        """Алгоритм Ву для сглаживания линий (полная версия)"""
        points = []
        
        def plot(x, y, intensity):
            """Добавляет точку с учетом интенсивности"""
            points.append((round(x), round(y), intensity))
            self.log(f"Ву: пиксель ({round(x)}, {round(y)}), интенсивность {intensity:.2f}")
            return (round(x), round(y))
        
        # Определяем steep (наклон больше 45 градусов)
        steep = abs(y2 - y1) > abs(x2 - x1)
        
        # Если steep=True, меняем местами x и y
        if steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
        
        # Гарантируем, что линия рисуется слева направо
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        
        dx = x2 - x1
        dy = y2 - y1
        gradient = dy / dx if dx != 0 else 1
        
        # Первая точка
        xend = round(x1)
        yend = y1 + gradient * (xend - x1)
        xgap = 1 - (x1 + 0.5) % 1
        xpxl1 = xend
        ypxl1 = int(yend)
        
        if steep:
            plot(ypxl1, xpxl1, (1 - (yend % 1)) * xgap)
            plot(ypxl1 + 1, xpxl1, (yend % 1) * xgap)
        else:
            plot(xpxl1, ypxl1, (1 - (yend % 1)) * xgap)
            plot(xpxl1, ypxl1 + 1, (yend % 1) * xgap)
        
        intery = yend + gradient
        
        # Вторая точка
        xend = round(x2)
        yend = y2 + gradient * (xend - x2)
        xgap = (x2 + 0.5) % 1
        xpxl2 = xend
        ypxl2 = int(yend)
        
        if steep:
            plot(ypxl2, xpxl2, (1 - (yend % 1)) * xgap)
            plot(ypxl2 + 1, xpxl2, (yend % 1) * xgap)
        else:
            plot(xpxl2, ypxl2, (1 - (yend % 1)) * xgap)
            plot(xpxl2, ypxl2 + 1, (yend % 1) * xgap)
        
        # Основной цикл
        for x in range(xpxl1 + 1, xpxl2):
            if steep:
                plot(int(intery), x, 1 - (intery % 1))
                plot(int(intery) + 1, x, intery % 1)
            else:
                plot(x, int(intery), 1 - (intery % 1))
                plot(x, int(intery) + 1, intery % 1)
            intery += gradient
        
        return points