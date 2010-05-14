# coding: utf-8


import gtk
#import cairo
import gobject
import pygtk

import random
from operator import indexOf

pygtk.require('2.0')

from sprite import Sprite
from virus import Virus
from cell import Cell
from virus import DEFAULT_WIDTH as VIRUS_WIDTH, DEFAULT_HEIGHT as VIRUS_HEIGHT
from cell import DEFAULT_WIDTH as CELL_WIDTH, DEFAULT_HEIGHT as CELL_HEIGHT
from display import display_simulation
from hud import Hud
from constants import WINDOW_SIZE, TOTAL_VIRUS, MAX_CELLS, TRAIN_CELLS
from constants import CHARACTERISTICS_DICT
from constants import TRAINING_ZONE_LIMIT
virList =[]
cellList =[]
from QLearning.qlearn import QAgent
from QLearning.qlearn import QAction
from QLearning.qlearn import Table

#Lienzo es donde se pintara todo
class Lienzo(gtk.DrawingArea):
    def __init__(self, ventana):
        super(Lienzo, self).__init__()
        #Cambiar el color de fondo de la ventana
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,0))
        # Pedir el tamano de la ventana
        self.set_size_request(WINDOW_SIZE,WINDOW_SIZE)
        #Asignar la ventana que recibe de paramentro a la ventana que se
        #utilizara en el lienzo
        self.ventana=ventana
        #expose-event es una propiedad de DrawingArea que le dice como
        #dibujares, aqui le decimos que utilize nuestra funcion paint
        #para ese evento en vez del que trae por defaul.
        self.connect("expose-event", self.paint)
        #reconocer cuando oprimes y sueltas el mouse
        self.connect("button_press_event",self.button_press)
        self.connect("button_release_event",self.button_release)
        self.connect("motion_notify_event",self.actualizar_dragged)
        self.set_events(gtk.gdk.BUTTON_PRESS_MASK|gtk.gdk.BUTTON_RELEASE_MASK|gtk.gdk.POINTER_MOTION_MASK)
        self.hud=Hud()
        self.minTimeToNextCell=100
        self.maxTimeToNextCell=300
        self.ticksToNextCell=random.randint(self.minTimeToNextCell,self.maxTimeToNextCell)

        #cells
        self.virus=[]
        self.cells=[]
        
        self.draggingObject = None
        self.objetoSeleccionado=[]

        self.currentState="Running"
        self.classificationList=["Target","Enemy","Food"]
        self.divisionPoints=[]
        self.trainingSet=[]

        self.trainingZoneLimit=WINDOW_SIZE-100
        self.currentCell = 0
        self.apareciendo = []
        self.numCells = 0
        self.read_file()

        self.r_table = Table()
        self.qagent = QAgent(self.r_table,'A')

        self.init_simulation()

    def read_file(self):
        file = open("list.txt",'r')
        self.apareciendo = []
        for linea in file.readlines():
            self.apareciendo.append(linea)
        self.numCells = len(self.apareciendo)
        print self.numCells
        return self.apareciendo


    def actualizar_dragged(self,widget,event):
        if self.draggingObject:
            self.draggingObject.posX=event.x
            self.draggingObject.posY=event.y

    def on_timer(self):
        self.update()
        return True

    def init_simulation(self):
        """Inicializacion de valores"""
        self.reset()
        gobject.timeout_add(20, self.on_timer)

    def run_simulation(self,extra=0):
        if self.currentState=="Training":
            self.currentState="Running"
            for cell in self.cells:
                cell.width=20
                cell.height=20
                cell.velX=random.randint(1,5)/5.0
                cell.velY=random.random()

#            self.cells =[Cell(
#               random.randint(0,WINDOW_SIZE),
#               random.randint(0,TRAINING_ZONE_LIMIT-CELL_HEIGHT),
#               -(random.random()+1)*2,0, "NormalCell"
#                ) for i in xrange(MAX_CELLS)]
            self.virus =[Virus(
               random.randint(0,WINDOW_SIZE-VIRUS_WIDTH),
               random.randint(0,TRAINING_ZONE_LIMIT-CELL_HEIGHT),
                ) for i in xrange(TOTAL_VIRUS)]
        else:
            pass

    #esto ya no se deberia llamar classify_cell
    def classify_cell(self, widget):
        for virus in self.virus:
            virus.analyze()

    def print_r_table(self,widget):
        self.qagent.q_table.print_table()

    def reset(self,extra=0):
        self.currentState="Training"
        self.trainingSet=[]
        for i in xrange(len(self.classificationList)):
            self.divisionPoints.append((WINDOW_SIZE/len(self.classificationList))*(i+1))
        self.cells =[Cell(
           random.randint(0,WINDOW_SIZE-CELL_WIDTH),
           random.randint(0,WINDOW_SIZE-CELL_HEIGHT),
            ) for i in xrange(TRAIN_CELLS)]

    def update(self):
        self.queue_draw()
        
        cellsToPop=[]
        for cell in self.cells:
            cell.update(self.currentState)
            if cell.type=="NormalCell":                
                if(cell.status=="Dead" and len(cell.dyingParticles)<=0):
                    cellsToPop.append(cell)
        for cell in cellsToPop:
            self.cells.pop(indexOf(self.cells,cell))
            if cell==self.virus[0].targetCell:
                self.virus[0].targetCell=None

        if self.currentState=="Running":
            
            if self.ticksToNextCell<=0:                
                if len(self.cells)< MAX_CELLS:#self.currentCell < self.numCells:
                    
                    self.ticksToNextCell=random.randint(self.minTimeToNextCell,self.maxTimeToNextCell)

                    #print "NumCells", self.numCells
                    #print self.apareciendo
    #                print self.apareciendo[self.currentCell]
                    print self.currentCell
                    
                    newCell=Cell(WINDOW_SIZE - CELL_WIDTH*2,
                        random.randint(0,TRAINING_ZONE_LIMIT-CELL_HEIGHT), 0,0,"TrainCell", self.apareciendo[self.currentCell])
                    newCell.velX=-random.random()*2
                    newCell.type="NormalCell"
                    self.cells.append(newCell)
                    self.currentCell=(self.currentCell+1)%self.numCells
            else:
                self.ticksToNextCell-=1

            #update virus
            for virus in self.virus:
                if not virus.isDead:
                    virus.update(self.currentState)
                    if len(self.cells)>0 and virus.targetCell==None:
                        #virus.targetCell=self.cells[len(self.cells)-1]
                        for i in xrange(len(self.cells)):
                            idx = random.randint(0,len(self.cells)-1)
                            if self.cells[idx].hp > 0:
                                virus.targetCell = self.cells[idx]
                                break
                        if virus.targetCell:
                            current_state = self.qagent.update(virus.targetCell)
                            print "Current State", current_state
                            if current_state == "A":
                                virus.status="Attacking"
                            if current_state =="C":
                                virus.status="Eating"
                            if current_state =="D":
                                virus.status="Defending"
                                virus.targetCell.status = "defended"
                            if current_state =="X":
                                virus.isDead = True

                            #virus.status="Defending"
                            #virus.targetCell.status = "defended"
                            #Hacer accion random
                            #aqui clasifica###################################################################
                        
                        
                

                if virus.is_colliding_with(virus.targetCell):
                    if not virus.targetCell.status:
                        if virus.status=="Attacking":
                            virus.targetCell.status="Dying"
                        if virus.status=="Eating":
                            virus.targetCell.status="BeingEaten"
                    if virus.targetCell.status=="Dead":
                        virus.targetCell=None

            for (cell,type) in self.trainingSet:
                for i in xrange(len(self.classificationList)):
                    if type==self.classificationList[i]:
                        rightLimit=self.divisionPoints[i]
                        if i==0:
                            leftLimit=0
                        else:
                            leftLimit=self.divisionPoints[i-1]
                        break
                            
                cell.update(self.currentState,[leftLimit,rightLimit-cell.width,TRAINING_ZONE_LIMIT,WINDOW_SIZE-cell.height])

    def paint(self, widget, event):
        """Nuestro metodo de pintado propio"""

        #Se crea un widget de cairo que despues se usara para desplegar
        #todo en la ventana
        cr = widget.window.cairo_create()
        #Le decimos a cairo que pinte su widget por primera vez.
        cr.set_source_rgb(0,0,0)
        cr.paint()

        #paint game info
        cr.set_source_rgb(1,1,1)
        cr.save()
        cr.move_to(15,15)
        text="To next cell: %d" % (self.ticksToNextCell)
        cr.show_text(text)
        cr.restore()
        #pintar a los agentes
        if self.currentState=="Training":
            pass
        
        if self.currentState=="Running":
            cr.set_source_rgb(1,1,1)
            cr.move_to(15, WINDOW_SIZE-100)
            display_simulation(cr,self.virus,self.cells)
            self.hud.display_cells(cr,self.cells)
            self.hud.display_viruses(cr, self.virus)

        #pintar efecto de selecci√≥n sobre un agente
        if self.objetoSeleccionado:
            cr.set_line_width(2)
            cr.set_source_rgba(random.random(), 1, random.random(), 0.3)
            cr.rectangle(self.objetoSeleccionado.posX-20,self.objetoSeleccionado.posY-20,
                            self.objetoSeleccionado.width+40, self.objetoSeleccionado.height+40)

            cr.stroke()

        #coso <- ¨¨
        if self.currentState == "Running":
            if self.virus[0].status == "Defending":
                cr.set_line_width(2)
                cr.set_source_rgba(1, random.random(), random.random(), 0.7)
                cr.arc(self.virus[0].posX+25,self.virus[0].posY+25, random.randint(40, 60),0, 360)
                cr.stroke()
                
        
    #Para drag & drop
    def button_press(self,widget,event):
        if event.button == 1:
            self.objetoSeleccionado=[]
            lstTemp = self.virus+self.cells
            for ob in lstTemp:
                if ob.drag(event.x,event.y):
                    self.draggingObject = ob
                    self.objetoSeleccionado=ob
                    break
                    
    def button_release(self,widget,event):
        if self.draggingObject:
            self.draggingObject.drop(event.x,event.y)
            self.draggingObject = None

    def pausar(self):
        self.corriendo=False

    def correr(self):
        self.corriendo=True
        
#    def mainloop(self):
#        while self.corriendo:
#            # Process all pending events.
#            self.update()
#            while gtk.events_pending():
#                gtk.main_iteration(False)
#                # Generate an expose event (could just draw here as well).
#            self.queue_draw()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Main(gtk.Window):
    def __init__(self):
        super(Main, self).__init__()
        self.set_title('Biokterii')
        self.set_size_request(WINDOW_SIZE,WINDOW_SIZE+20)
        self.set_resizable(True)
        self.set_position(gtk.WIN_POS_CENTER)
        #mainBox contiene el menu superior, contentBox(menu,lienzo) y el menu inferior
        self.mainBox = gtk.VBox(False,0)
        self.mainBox.set_size_request(WINDOW_SIZE,WINDOW_SIZE)
        
        #contentBox contiene el menu lateral y lienzo
        self.contentBox= gtk.HBox(False,0) #Recibe False para no se homogeneo
        
        self.lienzo=Lienzo(self)
        self.lienzo.set_size_request(WINDOW_SIZE+20,WINDOW_SIZE)
        
        self.contentBox.pack_start(self.lienzo, expand=True, fill=True, padding=0)

        #Menu bar
        menuBar = gtk.MenuBar()

        filemenu = gtk.Menu()
        filem = gtk.MenuItem("Actions")
        filem.set_submenu(filemenu)

#        annealMenu = gtk.MenuItem("Start Simulation")
#        annealMenu.connect("activate", self.lienzo.run_simulation)
#        filemenu.append(annealMenu)

        annealMenu = gtk.MenuItem("Print q_table")
        annealMenu.connect("activate", self.lienzo.print_r_table)
        filemenu.append(annealMenu)

        exit = gtk.MenuItem("Exit")
        exit.connect("activate", gtk.main_quit)
        filemenu.append(exit)

        menuBar.append(filem)

        menuBox = gtk.HBox(False, 2)
        menuBox.pack_start(menuBar, False, False, 0)

        #Empaquetado de todos los controles
        self.mainBox.pack_start(menuBox,expand=True,fill=True,padding=0)
        self.mainBox.pack_start(self.contentBox,expand=True, fill=True, padding=0)

        #Agregar la caja que contiene todo a la ventana
        self.add(self.mainBox)
        self.connect("destroy", gtk.main_quit)
        self.show_all()
        self.lienzo.run_simulation()

    def pausar_lienzo(self, widget):
        self.lienzo.pausar()

    def correr_lienzo(self, widget):
        self.lienzo.correr()

#    def cerrar_lienzo(self,widget):
#        self.lienzo.corriendo=False
#        gtk.main_quit

if __name__ == '__main__':
    Main()
    gtk.main()
