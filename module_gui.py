# -*- coding: utf-8 -*-
"""Lifie - Module GUI

Ce module gère l'interface graphique utilisateur.

"""
import tkinter
from tkinter.filedialog import *
from tkinter.scrolledtext import *
from module_graphique import *
from module_cartographie import *
from module_principal import Avancer_Simulation
from PIL import Image, ImageTk

def fen_simulation(ile):
	"""Seconde boîte de dialogue accueillant la simulation."""

	ile = ile
	image = ile_vers_image(ile)
	Executer_Simulation = False

	# Actualise l'affichage
	def Actualiser_Canevas():
		global ile
		photo = ImageTk.PhotoImage(ile_vers_image(ile))
		label = Label(image=photo)
		label.image = photo

		Canevas2.delete(ALL)
		Canevas2.configure(width=photo.width(), height=photo.height())
		Canevas2.create_image(0, 0, anchor=NW, image=photo)

	def Arreter_Simulation():
		global Executer_Simulation
		Executer_Simulation = False

	def Commencer_Simulation():
		global Executer_Simulation
		Executer_Simulation = True
		Simulation()
	# Appelle la fonction de simulation du module principal et actualise l'affichage
	def Simulation():
		global Executer_Simulation
		if Executer_Simulation == True:
			# On enregistre le moment exact où le programme a démarré
			moment_depart = time.time()

			global ile
			ile = Avancer_Simulation(ile)
			Actualiser_Canevas()

			# On attend de manière à correspondre à Vitesse (ex. 1 image par seconde)
			duree_exec = time.time() - moment_depart
			Console_Log.after(int((Vitesse.get() - duree_exec)*1000), Simulation)

	# Création d'une nouvelle fenêtre
	Fenetre_Simulation = tkinter.Toplevel()
	Fenetre_Simulation.configure(borderwidth=5, relief=SUNKEN)
	Fenetre_Simulation.title("Lifie - Simulation")

	# Création d'un espace pour l'image
	Canevas2 = Canvas(Fenetre_Simulation, bg='#E3E3E3', cursor='dot')
	photo = ImageTk.PhotoImage(image)
	label = Label(image=photo)
	label.image = photo # keep a reference!
	Canevas2.configure(width=photo.width(), height=photo.height())
	Canevas2.create_image(0, 0, anchor=NW, image=photo)
	Canevas2.grid(row=0, column=0, rowspan=15, columnspan=32)

	# Création d'un bouton de lancement
	Bouton_PlusUn = Button(Fenetre_Simulation, text="+1", state=DISABLED)
	Bouton_Play = Button(Fenetre_Simulation, text="Lancer", command=Commencer_Simulation)
	Bouton_Stop = Button(Fenetre_Simulation, text="Stop", command=Arreter_Simulation)
	Bouton_PlusUn.grid(row=15, column=0)
	Bouton_Play.grid(row=15, column=1)
	Bouton_Stop.grid(row=15, column=2)

	# Création de la zone de vitesse et des boutons
	ZoneVitesse = LabelFrame(Fenetre_Simulation, text="Vitesse de rendu")
	Vitesse = IntVar()
	Vitesse1 = Radiobutton(ZoneVitesse, text="1 FPS", variable=Vitesse, value=1)
	Vitesse2 = Radiobutton(ZoneVitesse, text="Maximum", variable=Vitesse, value=0, state=DISABLED)
	Vitesse1.grid(row=0, column=0)
	Vitesse2.grid(row=0, column=1)
	Vitesse1.select()
	ZoneVitesse.grid(row=15, column=25, columnspan=7, padx=5)

	# Création d'une console où sont affichées les actions
	Console_Log = ScrolledText(Fenetre_Simulation, wrap=tkinter.WORD, width=int(photo.width() / 7.2), height=5)
	Console_Log.grid(row=16, columnspan=32)

	Fenetre_Simulation.mainloop()


def gestion_source():
	"""Première boîte de dialogue permettant de choisir ou de créer la carte à utiliser."""

	source = None
	image = None
	ile = None

	def Nouvelle_Carte():
		global ile
		global image

		ile = creation_ile(1280, 1280)
		image = ile_vers_image(ile)

		Actualiser_Canevas()

	def Ouvrir_Fichier_Carte():
		filename = tkinter.filedialog.askopenfilename(title="Ouvrir une carte", filetypes=[('Carte de jeu','.npy'),('Tous les fichiers','.*')])
		
		global ile
		ile = importer_ile(filename)

		global source
		source = filename

		global image
		image = ile_vers_image(ile)

		Actualiser_Canevas()

	def Sauvegarder_Carte():
		global ile
		filename = tkinter.filedialog.asksaveasfilename(title="Enregistrer une carte", defaultextension=".npy", filetypes=[('Carte de jeu','.npy'),('Tous les fichiers','.*')])
		sauvegarder_ile(ile, chemin=filename.replace(".npy", ""))

		global source
		source = filename

	def Utiliser_Carte():
		global ile
		Fenetre_Gestion_Source.destroy()
		fen_simulation(ile)

	def Actualiser_Canevas():
		global ile
		global image

		photo = ImageTk.PhotoImage(image)
		label = Label(image=photo)
		label.image = photo # keep a reference!

		Canevas.configure(width=photo.width(), height=photo.height())
		Canevas.create_image(0, 0, anchor=NW, image=photo)

		Bouton3['state'] = 'normal'
		Bouton4['state'] = 'normal'

	# Création d'une nouvelle fenêtre
	Fenetre_Gestion_Source = Toplevel(root)
	Fenetre_Gestion_Source.title("Lifie - Menu")

	# Création des boutons du menu
	Bouton1 = Button(Fenetre_Gestion_Source, text="Générer une carte aléatoire", command=Nouvelle_Carte)
	Bouton2 = Button(Fenetre_Gestion_Source, text="Importer un fichier carte (.npy)", command=Ouvrir_Fichier_Carte)
	Bouton4 = Button(Fenetre_Gestion_Source, text="Sauvegarder la carte", command=Sauvegarder_Carte, state=DISABLED)
	Bouton3 = Button(Fenetre_Gestion_Source, text="Utiliser cette carte", command=Utiliser_Carte, font=("DejaVu Sans", 9, "bold"), state=DISABLED)
	Canevas = Canvas(Fenetre_Gestion_Source, width=640, height=640, bg='#E3E3E3')
	Canevas.create_text(310, 300, text="~Carte ~", font=("DejaVu Sans Mono", 32), fill="grey")

	Bouton1.grid(row=1, column=0, padx=5, pady=5)
	Bouton2.grid(row=1, column=1, padx=5, pady=5)
	Bouton3.grid(row=2, column=0, padx=5, pady=5)
	Bouton4.grid(row=2, column=1, padx=5, pady=5)
	Canevas.grid(row=3, columnspan=2, rowspan=6)

	Fenetre_Gestion_Source.mainloop()


if __name__ == "__main__":
    root = Tk()
    root.withdraw()
    gestion_source()
    root.destroy()
