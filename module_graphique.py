# -*- coding: utf-8 -*-
"""Lifie - Module graphique

Ce module gère les fonctions en lien avec l'affichage.

"""
import numpy
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.colors import LinearSegmentedColormap
from numpy import random as rd

def ile_vers_image(ile):
    """
    Fonction graphique
    
    Transforme un array de carte en image RGB.
    Chaque tuple correspond aux valeurs RGB du pixel sous la forme (Red/255, Green/255, Blue/255).
    
    Arguments:
        ile (array): Array à transformer

    Retour:
        PIL.Image: Représentation graphique de la carte.
    """
    print("[i] Création de l'image...          \r", end='')
    couleurs = {
    "ocean" : (10/255, 65/255, 145/255),
    "sable" : (240/255, 230/255, 140/255),
    "plaine"    : (154/255, 205/255, 50/255),
    "foret"     : (34/255, 139/255, 34/255),
    "montagne"  : (0/255, 80/255, 0/255),
    "neige"     : (255/255, 250/255, 250/250) }

    # On colore la carte suivant les couleurs précédentes
    colormap_ile = LinearSegmentedColormap.from_list('tropiques', (couleurs['ocean'], couleurs['sable'], couleurs['plaine'], couleurs['foret'], couleurs['montagne'], couleurs['neige']), N=6, gamma=1.0)

    # On convertit en image
    couleurs_ile = plt.cm.get_cmap(colormap_ile)
    ile_coloriee = couleurs_ile(ile)
    ile_coloriee_int8 = (255 * ile_coloriee).astype('uint8')
    img = Image.fromarray(ile_coloriee_int8)

    # On affiche (l'image est réduite de moitié de manière à ce qu'elle soit plus nette)
    img.thumbnail((img.size[0] / 2, img.size[1] / 2), Image.ANTIALIAS)
    print("[i] Création de l'image... OK.")
    # img.show()

    return img
