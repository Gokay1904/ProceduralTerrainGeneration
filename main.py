import pygame as pg
import numpy as np
from OpenGL.GL import *
import ctypes
from OpenGL.GL.shaders import compileProgram,compileShader
import moderngl as mgl
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

        glTranslatef(0.0, 0.0, -5)

        glRotatef(0, 0, 0, 0)

        running = True
        while(running):

            for event in pg.event.get():
                if(event.type == pg.QUIT):
                    running = False
            glRotatef(1, 3, 1, 1)
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
            Cube()
            pg.display.flip()
            pg.time.wait(10)

        self.quit()



    def quit(self):
        pg.quit()



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


