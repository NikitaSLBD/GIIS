import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

class Matrix4x4:
    def __init__(self):
        self.matrix = np.identity(4, dtype=np.float32)
    
    def translate(self, dx, dy, dz):
        translation = np.identity(4, dtype=np.float32)
        translation[0, 3] = dx
        translation[1, 3] = dy
        translation[2, 3] = dz
        self.matrix = np.dot(translation, self.matrix)
    
    def scale(self, sx, sy, sz):
        scaling = np.identity(4, dtype=np.float32)
        scaling[0, 0] = sx
        scaling[1, 1] = sy
        scaling[2, 2] = sz
        self.matrix = np.dot(scaling, self.matrix)
    
    def rotate_x(self, angle):
        rad = np.radians(angle)
        rotation = np.identity(4, dtype=np.float32)
        rotation[1, 1] = np.cos(rad)
        rotation[1, 2] = -np.sin(rad)
        rotation[2, 1] = np.sin(rad)
        rotation[2, 2] = np.cos(rad)
        self.matrix = np.dot(rotation, self.matrix)
    
    def rotate_y(self, angle):
        rad = np.radians(angle)
        rotation = np.identity(4, dtype=np.float32)
        rotation[0, 0] = np.cos(rad)
        rotation[0, 2] = np.sin(rad)
        rotation[2, 0] = -np.sin(rad)
        rotation[2, 2] = np.cos(rad)
        self.matrix = np.dot(rotation, self.matrix)
    
    def rotate_z(self, angle):
        rad = np.radians(angle)
        rotation = np.identity(4, dtype=np.float32)
        rotation[0, 0] = np.cos(rad)
        rotation[0, 1] = -np.sin(rad)
        rotation[1, 0] = np.sin(rad)
        rotation[1, 1] = np.cos(rad)
        self.matrix = np.dot(rotation, self.matrix)
    
    def reflect(self, axis):
        reflection = np.identity(4, dtype=np.float32)
        if axis == 'x':
            reflection[0, 0] = -1
        elif axis == 'y':
            reflection[1, 1] = -1
        elif axis == 'z':
            reflection[2, 2] = -1
        self.matrix = np.dot(reflection, self.matrix)
    
    def perspective(self, d):
        perspective = np.identity(4, dtype=np.float32)
        perspective[3, 2] = -1/d
        self.matrix = np.dot(perspective, self.matrix)
    
    def apply_to_point(self, point):
        homogeneous = np.append(point, 1)
        transformed = np.dot(self.matrix, homogeneous)
        if transformed[3] != 0:
            return transformed[:3] / transformed[3]
        return transformed[:3]

class Model3D:
    def __init__(self):
        self.vertices = []
        self.edges = []
        self.transform = Matrix4x4()
    
    def load_from_file(self, filename):
        try:
            with open(filename, 'r') as file:
                for line in file:
                    if line.startswith('v '):
                        parts = line.strip().split()
                        if len(parts) >= 4:
                            vertex = list(map(float, parts[1:4]))
                            self.vertices.append(vertex)
                    elif line.startswith('e '):
                        parts = line.strip().split()
                        if len(parts) >= 3:
                            edge = list(map(int, parts[1:3]))
                            self.edges.append(edge)
            print(f"Загружено {len(self.vertices)} вершин и {len(self.edges)} ребер")
            if self.vertices:
                print("Пример вершины:", self.vertices[0])
            if self.edges:
                print("Пример ребра:", self.edges[0])
        except Exception as e:
            print(f"Ошибка загрузки файла: {e}")
    
    def draw(self):
        if not self.vertices or not self.edges:
            print("Нет данных для отображения!")
            return
        
        glBegin(GL_LINES)
        for edge in self.edges:
            if edge[0] < len(self.vertices) and edge[1] < len(self.vertices):
                v1 = self.transform.apply_to_point(self.vertices[edge[0]])
                v2 = self.transform.apply_to_point(self.vertices[edge[1]])
                glVertex3fv(v1)
                glVertex3fv(v2)
            else:
                print(f"Ошибка: ребро ссылается на несуществующую вершину: {edge}")
        glEnd()

class GraphicsApp:
    def __init__(self):
        self.model = Model3D()
        self.angle = 0
        self.window_width = 800
        self.window_height = 600
        self.camera_distance = 5.0
    
    def init_gl(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, self.window_width/self.window_height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
    
    def update_camera(self):
        glLoadIdentity()
        gluLookAt(0, 0, self.camera_distance, 0, 0, 0, 0, 1, 0)
    
    def init(self):
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(self.window_width, self.window_height)
        glutCreateWindow(b"3D Affine transformations")
        
        self.init_gl()
        
        
        # Регистрация обработчиков
        glutDisplayFunc(self.display)
        glutReshapeFunc(self.reshape)
        glutKeyboardFunc(self.keyboard)
        glutSpecialFunc(self.special_keys)
        glutIdleFunc(self.idle)
    
    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.update_camera()
        
        # Отладочная информация
        glColor3f(1.0, 1.0, 1.0)
        self.render_text(10, 20, "Use WASD for moving, arrows for rotating")
        self.render_text(10, 40, "RTY - reflection for x, y, z axes")
        self.render_text(10, 60, "ZX - scale P - perspective")
        self.render_text(10, 80, "-+ - cam scale 0 - reset")
        self.render_text(10, 100, "123 - square, tetrahedron, triangle")
        self.render_text(10, 120, f"Cam: {self.camera_distance:.1f}")
        
        # Оси координат
        glBegin(GL_LINES)
        # X - красный
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(2.0, 0.0, 0.0)
        # Y - зеленый
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 2.0, 0.0)
        # Z - синий
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 2.0)
        glEnd()
        
        # Модель
        glColor3f(1.0, 1.0, 0.0)
        self.model.draw()
        
        glutSwapBuffers()
    
    def render_text(self, x, y, text):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, self.window_width, 0, self.window_height)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glRasterPos2i(x, y)
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    def reshape(self, width, height):
        self.window_width = width
        self.window_height = height
        glViewport(0, 0, width, height)
        self.init_gl()
    
    def keyboard(self, key, x, y):
        key = key.decode('latin-1').lower()
        if key == '1':  # Перемещение вперед
            self.model = Model3D()
            self.model.load_from_file("square.txt")
        elif key == '2':  # Перемещение назад
            self.model = Model3D()
            self.model.load_from_file("tetrahedron.txt")
        elif key == '3':  # Перемещение влево
            self.model = Model3D()
            self.model.load_from_file("simple_model.txt")
        elif key == 'w':  # Перемещение вперед
            self.model.transform.translate(0, 0, -0.1)
        elif key == 's':  # Перемещение назад
            self.model.transform.translate(0, 0, 0.1)
        elif key == 'a':  # Перемещение влево
            self.model.transform.translate(-0.1, 0, 0)
        elif key == 'd':  # Перемещение вправо
            self.model.transform.translate(0.1, 0, 0)
        elif key == 'q':  # Перемещение вверх
            self.model.transform.translate(0, 0.1, 0)
        elif key == 'e':  # Перемещение вниз
            self.model.transform.translate(0, -0.1, 0)
        elif key == 'z':  # Масштабирование увеличение
            self.model.transform.scale(1.1, 1.1, 1.1)
        elif key == 'x':  # Масштабирование уменьшение
            self.model.transform.scale(0.9, 0.9, 0.9)
        elif key == 'r':  # Отражение по X
            self.model.transform.reflect('x')
        elif key == 't':  # Отражение по Y
            self.model.transform.reflect('y')
        elif key == 'y':  # Отражение по Z
            self.model.transform.reflect('z')
        elif key == 'p':  # Перспектива
            self.model.transform.perspective(5)
        elif key == '=':  # Приближение камеры
            self.camera_distance = max(1.0, self.camera_distance - 0.5)
        elif key == '-':  # Отдаление камеры
            self.camera_distance += 0.5
        elif key == '0':  # Сброс преобразований
            self.model.transform = Matrix4x4()
            self.camera_distance = 5.0
        elif key == 27:  # ESC - выход
            sys.exit()
        
        glutPostRedisplay()
    
    def special_keys(self, key, x, y):
        if key == GLUT_KEY_LEFT:  # Поворот вокруг Y влево
            self.model.transform.rotate_y(-5)
        elif key == GLUT_KEY_RIGHT:  # Поворот вокруг Y вправо
            self.model.transform.rotate_y(5)
        elif key == GLUT_KEY_UP:  # Поворот вокруг X вверх
            self.model.transform.rotate_x(-5)
        elif key == GLUT_KEY_DOWN:  # Поворот вокруг X вниз
            self.model.transform.rotate_x(5)
        
        glutPostRedisplay()
    
    def idle(self):
        self.angle += 0.5
        glutPostRedisplay()
    
    def run(self):
        glutMainLoop()

if __name__ == "__main__":
    app = GraphicsApp()
    app.init()
    app.run()