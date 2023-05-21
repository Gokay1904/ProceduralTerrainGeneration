import pygame as pg
import numpy as np

from OpenGL.GL import *

import matplotlib.pyplot as plt

import tkinter as tk
from tkinter import Scale, Label


from OpenGL.raw.GLU import gluPerspective


class TerrainModel:
    @staticmethod
    def lerp(a, b, x):
        # Linearly interpolates between two points. In this model
        return a + x * (b - a)

    @staticmethod
    def fade(f):
        # Apply fading to displacement vector. Decide whether it is close to the vertices or not.
        return 6 * f ** 5 - 15 * f ** 4 + 10 * f ** 3

    @staticmethod
    def gradient(c, x, y):
        # These are the displacement vectors of our corners from the selected point.
        vectors = np.array([[0, 1], [0, -1], [1, 0], [-1, 0]])
        gradient_co = vectors[c % 4]

        return gradient_co[:, :, 0] * x + gradient_co[:, :, 1] * y

    @staticmethod
    def perlin(x, y, seed=0):

        np.random.seed(seed)
        # Create values from 0 to 2^n. Here 2^n defined as 128.
        ptable = np.arange(128, dtype=int)

        # To make a random permutation table shuffle the array.
        np.random.shuffle(ptable)

        ptable = np.stack([ptable, ptable]).flatten()

        # Grid coordinates.
        xi, yi = x.astype(int), y.astype(int)
        # Displacement vectors.
        xg, yg = x - xi, y - yi
        # Apply fading operation to the displacement vectors.
        xf, yf = TerrainModel.fade(xg), TerrainModel.fade(yg)
        # Create a gradient vectors for upper right, upper left, lower right and lower left. Then multiply it by displacement vectors.
        n00 = TerrainModel.gradient(ptable[ptable[xi] + yi], xg, yg)
        n01 = TerrainModel.gradient(ptable[ptable[xi] + yi + 1], xg, yg - 1)
        n11 = TerrainModel.gradient(ptable[ptable[xi + 1] + yi + 1], xg - 1, yg - 1)
        n10 = TerrainModel.gradient(ptable[ptable[xi + 1] + yi], xg - 1, yg)

        # Apply interpolation horizontally (bottom left corner, bottom right corner)
        x1 = TerrainModel.lerp(n00, n10, xf)
        x2 = TerrainModel.lerp(n01, n11, xf)

        # Find the height value (it will be the height in 3D mesh)
        return TerrainModel.lerp(x1, x2, yf)

    @staticmethod
    def getTerrain2DView(cell_size, seed=0,terrain_resolution = 10):
        lin_array = np.linspace(1, terrain_resolution, cell_size + 1, endpoint=False)
        x, y = np.meshgrid(lin_array, lin_array)

        _terrain_model = TerrainModel.perlin(x, y, seed=seed)
        _terrain_model *= 8
        plt.imshow(_terrain_model, origin='upper')
        plt.show()


#This part creates a openGL frame to draw our mesh. Initialization values like frame size, lighting type, color type, perspective view, frame time etc are defined here.
class OpenGlFrame:

    #Initilization of OpenGL Panel
    def __init__(self,cell_size,seed,resolution):

        pg.init()
        display = (640,480)
        pg.display.set_mode(display,pg.OPENGL|pg.DOUBLEBUF)

        self.seed = seed
        self.cell_size = cell_size
        self.resolution = resolution
        self.clock = pg.time.Clock()
        self.display = display


        self.mainLoop(display)

    # Main operations like drawing the terrain and updating by each time frame are made here.
    def mainLoop(self,display):

        glClearColor(0.1, 0.2, 0.2, 1)

        gluPerspective(90, display[0] / display[1], 0.1, 120.0)

        glTranslatef(0, -10, -20)

        glRotatef(30, 40, 0, 0)
        glRotatef(135, 0, 20, 0)

        running = True

        terrain = TerrainMesh(self.cell_size,self.seed,self.resolution)

        #In this loop frame is updated each defined waiting time here it is 10 miliseconds.
        while (running):

            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False

            # Rotate our terrain around itself 4 degree in each iteration.
            glRotatef(4, 0, 15, 0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            #Green wireframe color
            glColor3f(0, 1, 0)

            terrain.render()
            pg.display.flip()
            pg.time.wait(10)

        self.quit()



    def quit(self):
        pg.quit()


#Creating the Mesh using vertices and edge matrices, and defining them to OpenGL
class TerrainMesh:

    def __init__(self, cell_size=10, seed=32, terrain_resolution=10):
        self.cell_size = cell_size
        self.seed = seed;
        self.terrain_resolution = terrain_resolution
        self.update_terrain()

    def update_terrain(self):

        # If the terrain resolution increase, there will be more interpolation between points.
        # Briefly, high resolution causes high noise.
        lin_array = np.linspace(1, self.terrain_resolution, self.cell_size + 1, endpoint=False)

        #Make this linear interpolation x and y
        x, y = np.meshgrid(lin_array, lin_array)

        _vertices = np.zeros(((self.cell_size + 1) ** 2, 3))

        _terrain_model = TerrainModel.perlin(x, y, seed=self.seed)
        _terrain_model *= 8

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
        while (True):

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

        self.edges = _edges
        self.vertices = _vertices


    # For a better optimization terrain is only rendered when this method is called.
    # Since there will be a lot of calculations in high cell sizes, I preferred to have it calculated when necessary rather than having it done every time.
    def render(self):
        self.update_terrain()
        glBegin(GL_LINES)
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.vertices[vertex])
        glEnd()

    #To destroy drawn vertices and edges. Not used yet.
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))


# When this method is called the openGL frame will be drawn. This will be used in Ttkinter GUI. Whenever the button is clicked this method will be called.
def showTerrain(cell_size,seed,resolution):
    if __name__ == '__main__':
        terrain_frame = OpenGlFrame(cell_size,seed,resolution)

# This part will be about Tkinter GUI.

# Initialization values of the Tkinter GUI.
root = tk.Tk()
root.geometry('640x480')
root.resizable(False, False)
root.title('Terrain Generator')

# Explanations of adjustments like cell size and seed etc..

#Title text
project_title_text = Label(root,text ="Random Terrain Generator", font='Helvetica 24 bold')
project_title_text.pack(ipady=5)

cell_text = Label(root,text ="Cell Size", font='Helvetica 12 bold')
cell_text.pack(ipady=5)

# For setting the cell size I used a scaler, It is yet 4 to 128 due to lack of optimization.
cell_size_scale = Scale(root, from_=4, to=128,orient = "horizontal")
cell_size_scale.pack()

seed_text = Label(root,text ="Random Seed", font='Helvetica 12 bold')
seed_text.pack(ipady=5)

# Seed is can be also set up by scaler.
seed_scale = Scale(root, from_=1, to=128,orient = "horizontal")
seed_scale.pack()

terrain_res_text = Label(root,text ="Resolution", font='Helvetica 12 bold')
terrain_res_text.pack(ipady=5)

# Terrain res is can be also set up by scaler.
terrain_res_scale = Scale(root, from_=1, to=40,orient = "horizontal")
terrain_res_scale.pack(ipady=5)

def generate_button_clicked():
        showTerrain(cell_size_scale.get(),seed_scale.get(),terrain_res_scale.get())


def perlin_map2D_button_clicked():
    TerrainModel.getTerrain2DView(cell_size_scale.get(), seed_scale.get(),terrain_res_scale.get())


generate_terrain_button = tk.Button(
    root,
    text='Generate Terrain',
    command=lambda: generate_button_clicked()
)

generate_terrain_button.pack(
    ipadx=5,
    ipady=3,
    pady = 2,
    expand=False
)

generate_terrain_button.pack(
    ipadx=5,
    ipady=3,
)

perlin_map2D_button = tk.Button(
    root,
    text='Generate 2D Perlin Map',
    command=lambda: perlin_map2D_button_clicked()
)

perlin_map2D_button.pack(
    ipadx=5,
    ipady=5,
    pady = 2,
    expand=False,
)


seed_text = Label(root,text ="Gökay Akçay", font='Helvetica 7 normal')
seed_text.pack(ipady=5)



root.mainloop()
