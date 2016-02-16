# -*- coding: utf-8 -*-
"""Lifie - Module cartographique

Ce module joue le rôle d'interface pour les opérations sur les cartes et les arrays.

"""
import math
import time
import numpy
from PIL import Image
from scipy import ndimage
from numpy import random as rd
from module_backstage import *
from module_graphique import *

def creation_ile(taille_x, taille_y, densite_cible=50, taillemax_terrain=45, lissage=20, verbose=False):
    """
    Fonction de création de carte

    Permet de créer un monde aléatoire de type insulaire constitué de plusieurs éléments,
    sur lequel la simulation peut prendre place. Le processus se fait couche par couche dans l'ordre.

    Arguments:
        taille_x, taille_y (int): Dimensions de la carte à créer.
        densite_cible (Optional(int)): Part de la carte à couvrir par du terrain en pourcentage.
        taillemax_terrain (Optional(int)): Taille maximale que peut prendre un terrain en part de la carte.
            Une valeur plus élevée permet un terrain plus diversifié mais un temps de traitement plus long.
        lissage (Optional(int)): Degré du filtre moyenneur sur la matrice.
            Permet de faire disparaître les formes géométriques et donner une image plus réaliste.
        verbose (Optional(int)): Degré de debugging.

    Retour:
        array: Array contenant les informations de la carte.
            Correspondances :
                0 = Océan
                1 = Sable
                2 = Plaine
                3 = Forêt
                4 = Montagne
                5 = Neige

    Autre:
        v_print(str): Affiche les messages de debugging si en mode verbose.

    """
    # Gestion du debugging
    vprint = print if verbose else lambda *a, **k: None

    # Variables de la carte
    surface = taille_x * taille_y
    shape = (taille_x, taille_y)
    densite_actuelle = 0
    surfacemax_terrain = surface // taillemax_terrain
    rayonmax_terrain = math.sqrt(surfacemax_terrain / numpy.pi) 

    # Dictionnaire faisant la correspondance entre chaque terrain et son entier dans l'array
    vprint("Création du dictionnaire des entiers...")
    dic_ord = ["sable", "plaine", "foret", "montagne", "neige"]
    entiers = {
    "sable"     : 1,
    "plaine"    : 2,
    "foret"     : 3,
    "montagne"  : 4,
    "neige"     : 5 }

    # Dictionnaire faisant la correspondance entre chaque terrain et sa densité sur le terrain d'en dessous
    vprint("Création du dictionnaire des densités...")
    densites = {
    "sable"     : (densite_cible / 100),
    "plaine"    :  0.90,
    "foret"     : 0.50,
    "montagne"  : 0.50,
    "neige"     : 0.20 }

    # Création d'une carte vide
    vprint("Création de la carte vide...")
    ile = numpy.zeros(shape, dtype=numpy.uint8)

    # Remplissage de la carte chaque terrain à la fois avec la densité correspondante
    densite_precedente = surface
    for terrain in dic_ord:
        densite_actuelle = 0
        print("[i] Génération en cours... [", terrain, "]   \r", end='')
        while densite_actuelle < densites[terrain]:

            # Détermine la taille et la forme du terrain
            rayon = rd.randint(1, rayonmax_terrain)
            forme = rd.choice(['rond', 'rectangle'])

            # Détermine le centre
            pos_x_min = rayon
            pos_y_min = rayon
            pos_x_max = taille_x - rayon
            pos_y_max = taille_y - rayon
            pos_x = rd.randint(pos_x_min, pos_x_max)
            pos_y = rd.randint(pos_y_min, pos_y_max)

            # Poser un terrain si celui d'en dessous le permet
            if ile[pos_x, pos_y] <= entiers[terrain]:
                ile = poser_terrain(ile, pos_x, pos_y, rayon, forme, entiers[terrain])

            densite_actuelle = (ile == entiers[terrain]).sum() / densite_precedente
            vprint(densite_actuelle, "\r", end='')

        densite_precedente = (ile == entiers[terrain]).sum()

    ile = ndimage.median_filter(ile, size=lissage)
    return ile


def sauvegarder_ile(ile, image=None, chemin=None):
    """
    Sauvegarde l'array de la carte au format .npy (et optionnellement l'image) pour être importé plus tard.
    """
    if chemin == None:
        nom_fichier = "monde_" + time.asctime(time.localtime()).replace(" ", "")
    else:
        nom_fichier = chemin

    if image != None:
        image.save(nom_fichier + ".png")
        print("[*] Image sauvegardée sous : '" + nom_fichier + ".png'")
    else:
        print("")
        
    numpy.save(nom_fichier + ".npy", ile)
    print("[*] Carte sauvegardée sous : '" + nom_fichier + ".npy'")


def importer_ile():
    """
    Importe une carte au format .npy pour utilisation.
    Retourne un array d'île.
    """
    if chemin_fichier == '':
        raise SystemExit("[x] Importation en cours... Erreur : pas de fichier spécifié.")

    try:
        print("[i] Importation en cours... ", end='\r')
        ile = numpy.load(chemin_fichier)
        print("[*] Importation en cours... OK.")
        return ile
    except Exception as e:
        raise SystemExit("[x] Importation en cours... Erreur : " + str(e.strerror))
