# -*- coding: utf-8 -*-
"""Lifie - Module principal

Ce module contient le script du programme.

"""
import numpy
from module_graphique import *
from module_cartographie import *


# FONCTION CONTENANT LES RÈGLES D'ÉVOLUTION :
def Avancer_Simulation(ile):
	ile = numpy.true_divide(ile, 1.2)
	return ile


"""
Ces fonctions permettent de tenir une base de données (dictionnaire) des paramètres de la simulation sous la forme :
    * Tribu 0 :
        - Nombre d'individus
        - Nourriture
        - Défense (bois)
        - Or
        - Gemmes

    * Tribu X :
        [...]

    * Individus :
        - ID
        - Tribu mère
        - Santé
"""

def initialisation_db(nombre_tribu=2):
    db_tribus = {}

    for tribu in range(0, nombre_tribu):
        coordonnees_individus = numpy.nonzero(ile == tribu + 12)    # Les individus démarrent à partir de la valeur 12.

        db_tribus["Tribu " + str(tribu)] = {"ID": tribu + 12, "Individus": len(coordonnees_individus[0]), "Nourriture":0, "Défense":0, "Or":0, "Gemmes":0}

    print(str(db_tribus))
#initialisation_db()

def mise_a_jour_db(action, db, verbose=False):
    """
    Cette fonction mets à jour la base de données suivant les actions spécifiées.
    Syntaxe : <tribu> <paramètre> <nouvelle valeur>
    Exemple : Tribu 0 Nourriture +1
              Tribu 1 Gemmes +5
              Tribu 1 Individus -2
    """
    # Gestion du debugging
    vprint = print if verbose else lambda *a, **k: None

    # Extraction des paramètres
    no_tribu = int(action.replace("Tribu ", "")[0:1])
    parametre = action.replace("Tribu ", "")[2:]
    parametre = parametre[0:parametre.find(" ")]
    signe = action.replace("Tribu ", "")[2:]
    signe = signe[signe.find(" ") + 1:signe.find(" ") + 2]
    valeur = action.replace("Tribu ", "")[2:]
    valeur = int(valeur[valeur.find(" ") + 2:])
    vprint("N° de tribu : {0} | Paramètre : {1} | Signe : {2} | Valeur : {3}".format(no_tribu, parametre, signe, valeur))
