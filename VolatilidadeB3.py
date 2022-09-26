from lib2to3.pgen2.token import STAR
from DownloadDados import *
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np

import tkinter as tk
from tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class VolatilidadeB3():
    def __init__(self):

        #Cria Janela
        self.root = Tk()
        self.root.title('Volatilidade')
        self.root.geometry("500x670")

        self.top_frame = Frame(self.root, width=500, height=140)
        self.top_frame.pack(side='top', expand='True', fill = BOTH)

        self.graph_frame = Frame(self.root, width=500, height=530, bg = 'blue')
        self.graph_frame.pack(side='bottom', expand='True', fill = BOTH)

        #Drop menu dos ativos
        f = open("listaEmpresas.txt", "r", encoding="utf8")
        self.listaEmpresas = []
        for x in f:
            self.listaEmpresas.append(x[:-1].replace("%20", " "))
        f.close()

        self.ativo =  StringVar(self.top_frame)
        self.ativo.set(self.listaEmpresas[0])

        self.lbl_ativo = tk.Label(self.top_frame, width=10, height = 1, text="Ativo:", justify=LEFT)
        self.lbl_ativo.place(y = 20, x = 10)

        self.dropDown_ativo = OptionMenu(self.top_frame, self.ativo, *self.listaEmpresas)
        self.dropDown_ativo.place(y = 20, x = 85)

        self.lbl_intervalo = tk.Label(self.top_frame, width=10, height = 1, text="Num Dias")
        self.lbl_intervalo.place(y = 50, x = 10)
        self.intervalo = IntVar(self.top_frame)
        self.intervalo.set(360)
        self.input_intervalo = tk.Text(self.top_frame, width = 10, height = 1)
        self.input_intervalo.insert("1.0", str(self.intervalo.get()))
        self.input_intervalo.place(y = 50, x = 90)

        self.lbl_intervalo_vi = tk.Label(self.top_frame, width=10, height = 1, text="Num Dias VI")
        self.lbl_intervalo_vi.place(y = 50, x = 200)
        self.intervalo_vi = IntVar(self.top_frame)
        self.intervalo_vi.set(10)
        self.input_intervalo_vi = tk.Text(self.top_frame, width = 10, height = 1)
        self.input_intervalo_vi.insert("1.0", str(self.intervalo_vi.get()))
        self.input_intervalo_vi.place(y = 50, x = 280)

        self.lbl_num_vol = tk.Label(self.top_frame, width=10, height = 1, text="Num Dias Vol")
        self.lbl_num_vol.place(y = 80, x = 10)
        self.num_vol = IntVar(self.top_frame)
        self.num_vol.set(45)
        self.input_num_vol = tk.Text(self.top_frame, width = 10, height = 1)
        self.input_num_vol.insert("1.0", str(self.num_vol.get()))
        self.input_num_vol.place(y = 80, x = 90)

        self.lbl_media_vol = tk.Label(self.top_frame, width=10, height = 1, text="Size Media")
        self.lbl_media_vol.place(y = 110, x = 10)
        self.media_vol = IntVar(self.top_frame)
        self.media_vol.set(21)
        self.input_media_vol = tk.Text(self.top_frame, width = 10, height = 1)
        self.input_media_vol.insert("1.0", str(self.media_vol.get()))
        self.input_media_vol.place(y = 110, x = 90)


        #############################################################################
        ##### Botão
        
        #Botão Atualizar
        self.btn_update = Button(self.top_frame, text="Atualizar Dados", command=self.atualizar_dados, height = 2, width = 15)
        self.btn_update.place(y = 100, x = 380)


        #Criar figura do Gráfico
        self.fig_graph = Figure(figsize=(5,5), dpi=100)
        self.ax_fig_graph = self.fig_graph.add_subplot()

        self.canvas_graph = FigureCanvasTkAgg(self.fig_graph, self.graph_frame)
        self.canvas_graph.draw()
        self.canvas_graph.get_tk_widget().pack(side = TOP, fill=NONE, expand = True)

        self.tool_bar_graph = NavigationToolbar2Tk(self.canvas_graph, self.graph_frame)
        self.canvas_graph._tkcanvas.pack(side=BOTTOM, fill='both', expand=True)


        self.root.mainloop()

    def atualizar_dados(self):
        self.num_vol.set(int(self.input_num_vol.get("1.0", END)))
        self.intervalo.set(int(self.input_intervalo.get("1.0", END)))
        self.media_vol.set(int(self.input_media_vol.get("1.0", END)))
        self.intervalo_vi.set(int(self.input_intervalo_vi.get("1.0", END)))

        volHist = DownloadVolHist(self.ativo.get(), self.num_vol.get(), self.intervalo.get(), self.media_vol.get()).get_volHistorica()

        volImp = DownloadVolImp(self.ativo.get(), self.intervalo_vi.get(), 0.1375).get_volImplicita()

       

        #Atualiza o Grafico
        self.ax_fig_graph.clear()
        self.ax_fig_graph.set_title(" Volatilidade de " + self.ativo.get())

        self.ax_fig_graph.plot(volHist["Dia"], volHist["Volatilidade"], label="Volatilidade")
        self.ax_fig_graph.plot(volHist["Dia"], volHist["Media"], label="Média")

        self.ax_fig_graph.plot(volImp["Dia"], volImp["Vol Call"], label="VI Call")
        self.ax_fig_graph.plot(volImp["Dia"], volImp["Vol Put"], label="VI Put")

        self.ax_fig_graph.legend()
        self.ax_fig_graph.set_xlabel("Dias")
        self.ax_fig_graph.set_ylabel("Volatilidade")
        #self.ax_fig_graph.grid()
        self.canvas_graph.draw()

    
       


VolatilidadeB3()

