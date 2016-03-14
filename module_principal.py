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
        . Coordonnées en X (clé: Coordx)
        . Coordonnées en Y (clé: Coordy)
        . Identifiant de l'ennemi (clé: Identifiant_ennemi)

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

        db_tribus["Tribu " + str(tribu)] = {"Base":(), "ID Alpha": tribu + 100, "Population": len(coordonnees_individus[0]), "Nourriture":0, "Défense":0, "Or":0, "Coordx":-1, "Coordy":-1, "Identifiant_ennemi":-1}
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

def poser_tribu(matrice, nombre_tribus, type_terrain=2):
    
    terrain_actuel = None

    coordonnees_eligibles = numpy.nonzero(ile == type_terrain)
    intervalle_recherche = (len(coordonnees_eligibles[0]) // nombre_tribus )  
   
    for k in range(0, nombre_tribus):
        nom_tribu = "Tribu " + str(k)
        index_pos = rd.randint(k*intervalle_recherche, (k+1)*intervalle_recherche)
        db_tribus[nom_tribu]["Base"] = (coordonnees_eligibles[0][index_pos], coordonnees_eligibles[1][index_pos])
        ile[db_tribus[nom_tribu]["Base"]] = k + 100
        # compteur_individus += 1   Est-ce qu'on laisse cette ligne sachant que pour connaitre le nombre d'individus il suffit d'additionner les Population des tribus (et si on veut connaître le nombre de morts, autant ajouter la clef "Morts" dans db_tribus.  
        
    return(ile)

"""La fonction deplacement_alea fait se déplacer un individu sur un des 8 pixels qui l'entourent. Il faudra probablement la modifier 
pour que l'individu se dirige dans une direction privilégiée.
"""
def deplacement_alea (individu):
    alea_ligne = rd.choice((-1, 0, 1))
    alea_colonne = rd.choice((-1, 0, 1))
    db_individus[individu]["Coordx"] += alea_ligne
    db_individus[individu]["Coordy"] += alea_colonne
    
    
"""La fonction combat_potentiel prend en argument l'identifiant d'un individu et parcourt un carré de côté portee centré en les coordonnees de l'individu et s'arrete si elle rencontre un individu d'une tribu ennemie ou si elle a fini de parcours les pixels du carré. Dans le premier cas, elle stocke l'identifiant de l'ennemi dans 
db_individus[individu]["Identifiant_ennemi"].
"""
def combat_potentiel (individu, portee = 5):
    k=0
    i=0
    x = db_individus[individu]["Coordx"] - portee
    y = db_individus[individu]["Coordy"] - portee
    while k < 2*portee and ile[(x,y)] < 100:
        x = db_individus[individu]["Coordx"] - portee + k
        while i < 2*portee and ile[(x,y)] < 100:
            y = db_individus[individu]["Coordy"] - portee + i
            if ile[(x,y)] >= 100 :
                if db_individus[ile[(x,y)]]["Tribu"] == db_individus[individu]["Tribu"]:
                    x = 0; # Cela permet de revenir dans la boucle du k. Problème si il y a un individu au pixel (0,0) mais cela a peu de chances d'arriver.
                    y = 0; 
                else:
                    db_individus[individu]["Identifiant_ennemi"]=ile[(x,y)]  
                    db_individus[ile[(x,y)]]["Identifiant_ennemi"]=individu
            i += 1
        k += 1

"""
La fonction rencontre prend en arguments deux identifiants et fait progresser d'une étape la rencontre des deux individus (ils font chacun un
pas vers l'autre).
"""
def rencontre (individu1, individu2):
    
    # Deplacement du premier individu.
    
    if db_individus[individu1]["Coordx"] < db_individus[individu2]["Coordx"]:
        db_individus[individu1]["Coordx"]+=1
    if db_individus[individu1]["Coordx"] < db_individus[individu2]["Coordx"]:
        db_individus[individu2]["Coordx"]-=1
    if db_individus[individu1]["Coordy"] < db_individus[individu2]["Coordy"]:
        db_individus[individu1]["Coordy"]+=1
    if db_individus[individu1]["Coordy"] < db_individus[individu2]["Coordy"]:
        db_individus[individu2]["Coordy"]-=1
        
    # Deplacement du second individu.
    
    if db_individus[individu2]["Coordx"] < db_individus[individu2]["Coordx"]:
        db_individus[individu2]["Coordx"]+=1
    if db_individus[individu2]["Coordx"] < db_individus[individu2]["Coordx"]:
        db_individus[individu1]["Coordx"]-=1
    if db_individus[individu2]["Coordy"] < db_individus[individu2]["Coordy"]:
        db_individus[individu2]["Coordy"]+=1
    if db_individus[individu2]["Coordy"] < db_individus[individu2]["Coordy"]:
        db_individus[individu1]["Coordy"]-=1
        
"""
La fonction combat prend en argument l'identifiant d'un individu et suppose qu'il a un ennemi. Elle stocke dans deux variables l'expérience de l'individu et de son ennemi (pour la lisibilité).
Elle sélectionne deux réels situés entre chaque valeur d'expérience et 10.
Ensuite, elle les compare et si celle de l'individu est supérieure à celle de son ennemi, l'individu gagne de l'expérience et son ennemi est supprimé du db_individus.
Dans le cas contraire, l'ennemi gagne del'expérience et l'individu est supprimé du db_individus.
"""
def combat (individu):
    exp_indiv = db_individus[individu]["Expérience"]
    exp_ennemi = db_individus[db_individus[individu]["Identifiant_ennemi"]]["Expérience"]
    alea_indiv = random.uniform(exp_indiv, 10)
    alea_ennemi = random.uniform(exp_ennemi, 10)
    # ennemi = 
    if alea_indiv >= alea_ennemi:
        db_individus[individu]["Expérience"]+=(10-exp_indiv)/2
        db_individus[individu]["Identifiant_ennemi"] = 99                       # L'important c'est qu'il soit <100 pour rentrer à nouveau dans la fonction 
        del db_individus["Identifiant_ennemi"]                                  # combat_potentiel.
    else:
        db_individus["Identifiant_ennemi"]["Expérience"]+=(10-exp_ennemi)/2
        db_individus[db_individus[individu]["Identifiant_ennemi"]]["Identifiant_ennemi"] = 99
        del db_individus[individu]

"""
La fonction etape_suivante détermine l'action de chaque individu du dictionnaire pour passer de la carte à la carte suivante.
"""
def etape_suivante(dico_indiv):
    for identifiant in dico_indiv:
        if dico_indiv[identifiant]["Identifiant_ennemi"]<100:                             # Si l'individu n'a pas d'ennemi, on regarde s'il y en a un a portee de vue.
            combat_potentiel(identifiant)
            
            if dico_indiv[identifiant]["Identifiant_ennemi"]<100:                         # Il n'y a pas d'ennemi à portee de vue.
                deplacement_alea(individu)
            
            else:                                                                         # Il y a un ennemi à portée de vue.
                
                if (dico_indiv[identifiant]["Coordx"]==dico_indiv[dico_indiv[identifiant]["Identifiant_ennemi"]]["Coordx"] and dico_indiv[identifiant]["Coordy"]==dico_indiv[dico_indiv[identifiant]["Identifiant_ennemi"]]["Coordy"]):
                    combat(identifiant)                                                   # L'ennemi est sur le même pixel donc on lance le combat.
                
                else:                                                                                        
                    rencontre(identifiant, dico_indiv[identifiant]["Identifiant_ennemi"]) # S'il y en a un mais qui n'est pas sur le même pixel : ils vont l'un vers l'autre.              
        else: 																			  # S'il y en avait deja un, on lance les memes tests de combat.
                if (dico_indiv[identifiant]["Coordx"]==dico_indiv[dico_indiv[identifiant]["Identifiant_ennemi"]]["Coordx"] and                     dico_indiv[identifiant]["Coordy"]==dico_indiv[dico_indiv[identifiant]["Identifiant_ennemi"]]["Coordy"]):
                    combat(identifiant)                                                   
                
                else:                                                                                        
                    rencontre(identifiant, dico_indiv[identifiant]["Identifiant_ennemi"])   