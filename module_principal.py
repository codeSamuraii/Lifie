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

- db_tribus :

    * Tribu 0 :
        . Coordonnées de la base (clé: Base)
        . Premier individu (clé: ID Alpha)
        . Nombre d'individus (clé: Population)
        . Nourriture
        . Défense
        . Or

    * Tribu X :
        [...]


- db_individus :

    * (Individu) 100 :
        . N° Tribu (clé: Tribu)
        . Expérience
        . Age

    * 101 :
        . N° Tribu
        . Expérience
        . Age

    * n :
        . N° Tribu
        . Expérience
        . Age
"""
# Ile pour debugging
# ile = numpy.array([[0, 1, 0, 1, 0, 1, 0, 1],
#                    [0, 100, 0, 1, 0, 1, 0, 1],
#                    [0, 1, 0, 1, 101, 1, 0, 1],
#                    [0, 1, 0, 1, 0, 1, 0, 1]])

db_tribus = {}
db_individus = {}
compteur_individus = 100

def initialisation_db(nombre_tribu=2, verbose=True):
    # Gestion du debugging
    vprint = print if verbose else lambda *a, **k: None

    global ile
    global db_tribus
    global compteur_individus

    for tribu in range(0, nombre_tribu):
        coordonnees_individus = numpy.nonzero(ile == tribu + 100)    # Les individus démarrent à partir de la valeur 100.

        db_tribus["Tribu " + str(tribu)] = {"Base":(), "ID Alpha": tribu + 100, "Population": len(coordonnees_individus[0]), "Nourriture":0, "Défense":0, "Or":0}
        ajout_individu(tribu, verbose=True)

    vprint("[*] Base de donnée des tribus initialisée.")
    # vprint(str(db_tribus))
    vprint("[i] Le prochain identifiant libre est le " + str(compteur_individus) + ".")

def mise_a_jour_tribu(action, verbose=True):
    """
    Cette fonction mets à jour la base de données des tribus en fonction de l'action spécifiée.
    Syntaxe : <tribu n°> <paramètre> <+/-nouvelle valeur>
    Exemple : Tribu 0 Nourriture +1
              Tribu 1 Gemmes +5
              Tribu 1 Individus -2
    """
    # Gestion du debugging
    vprint = print if verbose else lambda *a, **k: None

    global db_tribus
    # Extraction des paramètres
    no_tribu = int(action.replace("Tribu ", "")[0:1])
    parametre = action.replace("Tribu ", "")[2:]
    parametre = parametre[0:parametre.find(" ")]
    signe = action.replace("Tribu ", "")[2:]
    signe = signe[signe.find(" ") + 1:signe.find(" ") + 2]
    valeur = action.replace("Tribu ", "")[2:]
    valeur = int(valeur[valeur.find(" ") + 2:])
    # Les paramètres ont été récupérés
    vprint("[i] N° de tribu : {0} | Paramètre : {1} | Valeur : [{2}]{3}".format(no_tribu, parametre, signe, valeur))

    # Application
    try:
        if signe == "-":
            db_tribus["Tribu " + str(no_tribu)][parametre] -= valeur
            vprint("[*] Valeur modifiée.")
        else:
            db_tribus["Tribu " + str(no_tribu)][parametre] += valeur
            vprint("[*] Valeur modifiée.")
    except:
        vprint("[x] Commande invalide !")

def ajout_individu(id_tribu, verbose=True):
    """
    Ajout d'un individu lors d'une naissance, retourne l'identifiant de celui-ci.
    """
    # Gestion du debugging
    vprint = print if verbose else lambda *a, **k: None

    global db_individus
    global compteur_individus
    db_individus[compteur_individus] = {"Tribu": id_tribu, "Expérience":0, "Age":0}
    vprint("[*] Individu n°" + str(compteur_individus) + " ajouté à la base de donnée.")
    compteur_individus += 1
    return compteur_individus - 1

def mise_a_jour_individu(action, verbose=True):
    """
    Cette fonction mets à jour la base de données des individus en fonction de l'action spécifiée.
    Syntaxe : <individu n°> <paramètre> <+/-nouvelle valeur>
    Exemple : 156 Expérience +10
              132 Age +1
    """
    # Gestion du debugging
    vprint = print if verbose else lambda *a, **k: None

    global db_individus
    # Extraction des paramètres
    identifiant = int(action[:action.find(" ")])
    parametre = action[action.find(" ") + 1:]
    parametre = parametre[:parametre.find(" ")]
    signe = action[action.rfind(" ") + 1:action.rfind(" ") + 2]
    valeur = int(action[action.rfind(" ") + 2:])
    # Les paramètres ont été récupérés
    vprint("[i] Individu : {0} | Paramètre : {1} | Valeur : [{2}]{3}".format(identifiant, parametre, signe, valeur))

    # Application
    try:
        if signe == "-":
            db_individus[identifiant][parametre] -= valeur
            vprint("[*] Valeur modifiée.")
        else:
            db_individus[identifiant][parametre] += valeur
            vprint("[*] Valeur modifiée.")
    except:
        vprint("[x] Commande invalide !")
