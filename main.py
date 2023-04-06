import pygame as pg
import numpy as np
from OpenGL.GL import *
import ctypes
from OpenGL.GL.shaders import compileProgram,compileShader
import sys

from OpenGL.raw.GLU import gluPerspective


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

        gluPerspective(45,display[0]/display[1],0.1,50.0)

        glTranslatef(0.0, 0.0, -10)

        glRotatef(0, 0, 0, 0)

        running = True

        while(running):

            for event in pg.event.get():
                if(event.type == pg.QUIT):
                    running = False
            glRotatef(1, 3, 0, 0)
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
            MeshSurface()
            pg.display.flip()
            pg.time.wait(10)

        self.quit()



    def quit(self):
        pg.quit()

class MeshSurface:
    def __init__(self):
        cell_size = 30
        _vertices = np.zeros(((cell_size+1) ** 2,3))

        x_idx = 0
        z_idx = 0

        ##First create the vertices
        for i in range(0, _vertices.shape[0]):
            _vertices[i] = [x_idx,0,z_idx]

            x_idx +=1
            if(x_idx > (cell_size)):
                x_idx = 0
                z_idx += 1


        _edges = np.zeros(((cell_size + 1) * (cell_size) * 2, 2),dtype="int")

        while(True):
            edge_index = 0

            for e in range(0, _edges.shape[0], 2):
                _edges[e] = (edge_index, edge_index + 1)

                edge_index += 1
                if (edge_index % (cell_size+1) == cell_size):
                    edge_index += 1

                    if (edge_index == 100):
                        break

            edge_index = 0

            for k in range(1, _edges.shape[0], 2):
                _edges[k] = (edge_index, edge_index + cell_size+1)
                edge_index += 1

                if (edge_index + cell_size >= 100):
                    break



            break


        print(_edges)


        glBegin(GL_LINES)

        for edge in _edges:
            for vertex in edge:
                print(_vertices[vertex])
                glVertex3fv(_vertices[vertex])

        glEnd()

        # self.vertices = np.array(self.vertices,dtype = np.float32)
        # self.vertex_count = 3
        #
        # self.vao = glGenVertexArrays(1)
        # glBindVertexArray(self.vao)
        # self.vbo = glGenBuffers(1)
        # glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        # glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        # glEnableVertexAttribArray(0)
        # glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        # glEnableVertexAttribArray(1)
        # glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(1))

    def destroy(self):

        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))



class Cube:
    def __init__(self):
        #x y z r g b
        self.verticies = (
            (1,-1,-1),
            (1,1,-1),
            (-1, 1, -1),
            (-1, -1, -1),
            (1, -1, 1),
            (1, 1, 1),
            (-1, -1, 1),
            (-1, 1, 1)
        )

        self.edges = (
            (0,1),
            (0,3),
            (0,4),
            (2,1),
            (2,3),
            (2,7),
            (6,3),
            (6,4),
            (6,7),
            (5,1),
            (5,4),
            (5,7)
        )


        glBegin(GL_LINES)
        for edge in self.edges:
            for vertex in edge:
                print(self.verticies[vertex])
                glVertex3fv(self.verticies[vertex])
        glEnd()

        #self.vertices = np.array(self.vertices,dtype = np.float32)
        #self.vertex_count = 3
#
        #self.vao = glGenVertexArrays(1)
        #glBindVertexArray(self.vao)
        #self.vbo = glGenBuffers(1)
        #glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        #glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        #glEnableVertexAttribArray(0)
        #glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        #glEnableVertexAttribArray(1)
        #glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(1))



    def destroy(self):

        glDeleteVertexArrays(1,(self.vao,))
        glDeleteBuffers(1,(self.vbo,))


if __name__ == '__main__':
    app = App()
