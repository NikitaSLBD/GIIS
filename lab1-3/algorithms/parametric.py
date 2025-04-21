class ParametricAlgorithms:
    def __init__(self, logger):
        self.log = logger
    
    def hermite(self, p1, p4, r1, r4, steps=1000):
        """Кубическая интерполяция Эрмита"""
        # Матрица Эрмита
        M = [
            [2, -2, 1, 1],
            [-3, 3, -2, -1],
            [0, 0, 1, 0],
            [1, 0, 0, 0]
        ]
        
        # Вектор геометрии
        Gx = [p1[0], p4[0], r1[0], r4[0]]
        Gy = [p1[1], p4[1], r1[1], r4[1]]
        
        points = []
        for i in range(steps + 1):
            t = i / steps
            T = [t**3, t**2, t, 1]
            
            x = sum(T[i] * sum(M[i][j] * Gx[j] for j in range(4)) for i in range(4))
            y = sum(T[i] * sum(M[i][j] * Gy[j] for j in range(4)) for i in range(4))
            
            points.append((round(x), round(y)))
            self.log(f"Эрмит t={t:.2f}: ({x:.2f}, {y:.2f})")
        
        return points
    
    def bezier(self, p1, p2, p3, p4, steps=1000):
        """Кривая Безье"""
        # Матрица Безье
        M = [
            [-1, 3, -3, 1],
            [3, -6, 3, 0],
            [-3, 3, 0, 0],
            [1, 0, 0, 0]
        ]
        
        # Вектор геометрии
        Gx = [p1[0], p2[0], p3[0], p4[0]]
        Gy = [p1[1], p2[1], p3[1], p4[1]]
        
        points = []
        for i in range(steps + 1):
            t = i / steps
            T = [t**3, t**2, t, 1]
            
            x = sum(T[i] * sum(M[i][j] * Gx[j] for j in range(4)) for i in range(4))
            y = sum(T[i] * sum(M[i][j] * Gy[j] for j in range(4)) for i in range(4))
            
            points.append((round(x), round(y)))
            self.log(f"Безье t={t:.2f}: ({x:.2f}, {y:.2f})")
        
        return points
    
    def bspline(self, points, steps=1000):
        """B-сплайн"""
        # Матрица B-сплайна
        M = [
            [-1, 3, -3, 1],
            [3, -6, 3, 0],
            [-3, 0, 3, 0],
            [1, 4, 1, 0]
        ]
        
        n = len(points)
        if n < 4:
            return []
        
        all_points = []
        for i in range(n - 3):
            G = points[i:i+4]
            Gx = [p[0] for p in G]
            Gy = [p[1] for p in G]
            
            for j in range(steps + 1):
                t = j / steps
                T = [t**3, t**2, t, 1]
                
                x = sum(T[k] * sum(M[k][l] * Gx[l] for l in range(4)) for k in range(4)) / 6
                y = sum(T[k] * sum(M[k][l] * Gy[l] for l in range(4)) for k in range(4)) / 6
                
                all_points.append((round(x), round(y)))
                self.log(f"B-сплайн сегмент {i}, t={t:.2f}: ({x:.2f}, {y:.2f})")
        
        return all_points