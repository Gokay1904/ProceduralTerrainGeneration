import pygame as pg
import numpy as np
import random

from OpenGL.GL import *
from pyopengltk import OpenGLFrame
import tkinter as tk
import ctypes
from OpenGL.GL.shaders import compileProgram,compileShader
import sys

from OpenGL.raw.GLU import gluPerspective
from numba import njit


class TerrainModel:
    @staticmethod
    def lerp(a, b, x):
        "linear interpolation i.e dot product"
        return a + x * (b - a)
        # smoothing function,
        # the first derivative and second both are zero for this function

    @staticmethod
    def fade(f):
        return 6 * f ** 5 - 15 * f ** 4 + 10 * f ** 3
        # gradyan vektörlerini ve noktasal çarpımları hesapla

    @staticmethod
    def gradient(c, x, y):
        vectors = np.array([[0, 1], [0, -1], [1, 0], [-1, 0]])
        gradient_co = vectors[c % 4]
        return gradient_co[:, :, 0] * x + gradient_co[:, :, 1] * y

    @staticmethod
    def perlin(x, y, seed=0):
        # pixel sayılarını esas alarak permütasyon tablosu oluştur.
        # seed değeri bağlangıç değeridir.
        # seed fonksiyonunu ayrıca aynı yapıları oluşturmak için kullanabiliriz.
        # this helps to keep our perlin graph smooth
        np.random.seed(seed)
        ptable = np.arange(128, dtype=int)
        # permütasyon tablosundaki değerleri karıştır.
        np.random.shuffle(ptable)
        # bir boyutlu permütasyon tablosunu iki boyutluya çevir.
        # böylece interpolasyon işlemlerinde dot product kolay yapılsın.
        ptable = np.stack([ptable, ptable]).flatten()
        # ızgara koordinatları
        xi, yi = x.astype(int), y.astype(int)
        # uzaklık vektörü koordinatları
        xg, yg = x - xi, y - yi
        # fade(sönme) işlemi uygula
        xf, yf = TerrainModel.fade(xg), TerrainModel.fade(yg)
        # sol üst sağ üst sol alt ve sağ alt için gradyan vektörleri
        n00 = TerrainModel.gradient(ptable[ptable[xi] + yi], xg, yg)
        n01 = TerrainModel.gradient(ptable[ptable[xi] + yi + 1], xg, yg - 1)
        n11 = TerrainModel.gradient(ptable[ptable[xi + 1] + yi + 1], xg - 1, yg - 1)
        n10 = TerrainModel.gradient(ptable[ptable[xi + 1] + yi], xg - 1, yg)
        # iki gradyan vektörü arasındaki değişime interpolasyon uygulayarak ortalamayı hesapla.
        x1 = TerrainModel.lerp(n00, n10, xf)
        x2 = TerrainModel.lerp(n01, n11, xf)
        return TerrainModel.lerp(x1, x2, yf)



class App:
    def __init__(self):

        pg.init()
        display = (640,480)
        pg.display.set_mode(display,pg.OPENGL|pg.DOUBLEBUF)

        self.clock = pg.time.Clock()


        self.mainLoop()

    def mainLoop(self):
        display = (640, 480)

        glClearColor(0.1, 0.2, 0.2, 1)

        gluPerspective(90, display[0] / display[1], 0.1, 120.0)

        glTranslatef(0, -10, -10)

        glRotatef(0, 0, 0, 0)

        running = True

        mesh_surface = MeshSurface(64)

        while (running):

            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False
            glRotatef(2, 0, 15, 0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            mesh_surface.render();
            pg.display.flip()
            pg.time.wait(10)

        self.quit()



    def quit(self):
        pg.quit()



class MeshSurface:

    def update_terrain(self):
        lin_array = np.linspace(1, 20, self.cell_size + 1, endpoint=False)
        x, y = np.meshgrid(lin_array, lin_array);
        # print(TerrainModel.perlin(x, y, seed=32));
        # print(TerrainModel.perlin(x, y, seed=32).shape);
        _vertices = np.zeros(((self.cell_size + 1) ** 2, 3))
        _terrain_model = TerrainModel.perlin(x, y, seed=random.randint(0,32))
        _terrain_model *= 8;

        x_idx = 0
        z_idx = 0

        ##First create the vertices

        for i in range(0, _vertices.shape[0]):
            _vertices[i] = [x_idx, _terrain_model[z_idx, x_idx], z_idx]

            x_idx += 1
            if (x_idx > (self.cell_size)):
                x_idx = 0
                z_idx += 1

        _edges = np.zeros(((self.cell_size + 1) * (self.cell_size) * 2, 2), dtype="int")
        _triangulation_edges = np.zeros(((self.cell_size) * (self.cell_size), 2), dtype="int")

        while (True):

            # for j in range(0,_edges.shape[0],1):
            #    if(j < cell_size*cell_size):
            #        _triangulation_edges[j,j+cell_size+2]

            edge_index = 0

            for e in range(0, _edges.shape[0], 2):
                _edges[e] = (edge_index, edge_index + 1)

                edge_index += 1
                if (edge_index % (self.cell_size + 1) == self.cell_size):
                    edge_index += 1

                    if (edge_index == 100):
                        break

            edge_index = 0

            for k in range(1, _edges.shape[0], 2):
                _edges[k] = (edge_index, edge_index + self.cell_size + 1)
                edge_index += 1

                if (edge_index + self.cell_size >= (self.cell_size + 1) ** 2):
                    break

            break

        print(_vertices)
        print(_triangulation_edges.shape);
        print(_edges)
        self.edges = _edges
        self.vertices = _vertices

    def __init__(self,cell_size = 10):
        self.cell_size = cell_size;
        self.update_terrain();




    def render(self):
        self.update_terrain();
        glBegin(GL_LINES)
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.vertices[vertex])
        glEnd()


    def destroy(self):

        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

#if __name__ == '__main__':
#    app = App()


class AppWindow(OpenGLFrame):
    def initgl(self):

        display = (640, 480)

        glClearColor(0.1, 0.2, 0.2, 1.0)
        gluPerspective(45, self.width / self.height, 0.1, 50.0)
        glTranslatef(0.0, 0.0, -5.0)

        self.mesh_surface = MeshSurface(64)
        self.mesh_surface.render()

        # Schedule the first update after 10 milliseconds
        self.after(10, self.update_frame)

    def redraw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.mesh_surface.render();
        self.update()

    def update_frame(self):

        self.redraw()

        # Schedule the next update after 10 milliseconds
        self.after(10, self.update_frame)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("640x480")
    app = AppWindow(root, width=640, height=480)
    app.pack(fill=tk.BOTH, expand=tk.YES)
    app.mainloop()
