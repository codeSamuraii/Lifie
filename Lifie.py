"""
  _      _  __ _
 | |    (_)/ _(_)
 | |     _| |_ _  ___
 | |    | |  _| |/ _ \
 | |____| | | | |  __/
 |______|_|_| |_|\___|

Écrit en Python par Yves Olsen et Rémi Héneault.

Le code est documenté et les conventions d'écritures PEP8 ont été
réspectées dans la mesure du possible afin d'en faciliter la lecture.
La documentation complète se trouve dans le fichier README.

"""
import matplotlib.animation as anim
import matplotlib.pyplot as plt
import numpy
import time

from PIL import Image, ImageDraw
from copy import copy, deepcopy
from math import sqrt
from matplotlib.colors import ListedColormap, from_levels_and_colors
from numpy import random as rd
from scipy import misc, ndimage
from threading import Thread

class Carte():
    """Classe de gestion de l'environnement de simulation.

    La classe Carte contient les méthodes nécessaires à la génération
    de matrices et d'images sur lesquelles se basent la simulation, ainsi
    que les méthodes qui permettent l'évolution des individus sur
    celles-ci. Elle est héritée de Thread de manière à pouvoir paralléliser
    les tâches.

    Attributs:
        largeur, hauteur (int):
            Dimensions de la simulation en pixels.
        densite_cible (int):
            Pourcentage minimal de remplissage de la matrice par des
            terrains.
        indice_terrains (int):
            Permet de faire varier la taille maximale d'un terrain
            et par conséquent la diversité de la carte. Optimal
            entre 20 et 200.
        lissage (int):
            Degré d'adoucissement de la carte brute (composée à
            l'origine uniquement de carré et de ronds) afin de lui
            donner un effet d'île.
        echelle (int):
            Degré de baisse de résolution de la matrice de simulation
            par rapport à la matrice d'image.
        verbose (bool):
            Active ou désactive le retour utilisateur sur console
            via la fonction vprint()

    Méthodes:
        TODO : méthodes Carte

    """
    liste_tribus = []
    liste_tribus_int = []
    liste_individus = []
    cimetiere = []

    def __init__(self, largeur, hauteur, densite_cible=60, indice_terrains=45, lissage=20, echelle=6, verbose=True):
        """Constructeur de classe.
        
        Permet d'initialiser à l'aide des paramètres du constructeur
        toutes les variables nécessaires à la gestion des matrices et
        des images.

        Attributs:
            largeur_img, hauteur_img (int):
                Taille de l'image de carte qui sera initialement générée
                avant d'être réduite pour éviter l'aliasing.
            largeur_matrice, hauteur_matrice (int):
                Taille de la matrice sur laquelle se déroulera la
                simulation, elle est à l'échelle 1/6ème par défaut.
            surface (int):
                Résolution de l'image de carte initialement générée.
            img_carte (array):
                Array d'image (RGB) représentation la carte en haute
                définition.
            img_matrice (array):
                Array d'image (RGB) représentant la matrice sur laquelle
                prend place la simulation.
            img_transp (array):
                Array d'image (RGBA) représentant uniquement les individus
                à des fins de superposition.
            matrice (array):
                Tableau d'entiers et d'objets (Individu) sur lequel
                s'éxecutent les fonctions d'évolution de la simulation.
            matrice_originale (array):
                Copie de la matrice à son état d'origine.

        """
        global vprint
        vprint = print if verbose else lambda *a, **k: None

        self.largeur_img = largeur * 2
        self.hauteur_img = hauteur * 2
        self.largeur_matrice = largeur // echelle
        self.hauteur_matrice = hauteur // echelle
        self.surface = (self.largeur_img * self.hauteur_img)
        self.densite_cible = densite_cible
        self.indice_terrains = indice_terrains
        self.lissage = lissage
        self.verbose = verbose
        self.img_carte = numpy.empty([self.largeur_img, self.hauteur_img])
        self.img_matrice = numpy.empty([self.largeur_matrice, self.hauteur_matrice])
        self.img_transp = numpy.empty([self.largeur_matrice, self.hauteur_matrice])
        self.matrice = numpy.empty([self.largeur_matrice, self.hauteur_matrice])
        self.matrice_tribus = numpy.empty([self.largeur_matrice, self.hauteur_matrice])
        self.matrice_originale = numpy.empty([self.largeur_matrice, self.hauteur_matrice])
        self.norm = None
        self.colormap_indiv = None
        self.cycles = 0

        vprint(" *  Instance de carte initialisée.")
        vprint("     > Le mode debugging est activé.")
        vprint("     > Image : " + str(self.hauteur_img) + "x" + str(self.largeur_img) + " px", end=" | ")
        vprint("Matrice : " + str(self.hauteur_matrice) + "x" + str(self.largeur_matrice) +" px")

    def Matrice(self):
        return self.matrice   
    
    def _get_rect(self, x, y, largeur, hauteur, angle):
        """Assiste à la création des rectangles.

        On applique les fonctions trigonométriques aux coordonnées de
        base d'un rectangle dans un repère orthonormé afin d'obtenir les
        coordonnées du rectangle incliné. Enfin, on ajoute la position
        initiale pour que le rectangle soit correctement placé.

        Arguments:
            x, y (int):
                Position du rectangle dans la future matrice.
            largeur, hauteur(int):
                Dimensions de celui-ci.
            angle (int):
                Inclinaison du polygône.

        Retour (array):
            Tableau contenant les _coordonnées_ du nouveau rectangle 
            dans la matrice d'origine.

        """
        rectangle_original = numpy.array([(0, 0), (largeur, 0), (largeur, hauteur), (0, hauteur)])
        theta = (numpy.pi / 180.0) * angle
        facteur = numpy.array([[numpy.cos(theta), -numpy.sin(theta)], [numpy.sin(theta), numpy.cos(theta)]])
        decalage = numpy.array([x, y])
        transformed_rect = numpy.dot(rectangle_original, facteur) + decalage
        return transformed_rect

    def _poser_terrain(self, pos_x, pos_y, cote, forme, type_terrain):
        """Ajoute un cercle ou un rectangle à la matrice.

        * Si la forme sélectionée est un rond, un masque (index) remplissant les conditions d'appartenance à un disque est
        créé. Toutes les valeurs de la matrice y appartenant sont changées suivant le type de terrain selectionné.
        * Si la forme sélectionnée est un rectangle, on transforme la matrice en image et on remplit un rectangle grâce aux
        coordonnées que nous donne la fonction _get_rect. On retransforme ensuite l'image en matrice.

        Arguments:
            pos_x, pos_y (int):
                Coordonnées du centre du polygone.
            cote (int):
                Taille maximale que peut avoir le polygone.
            forme (str):
                Nature du polygone.
            type_terrain (int):
                Entier qui remplira l'aire de la forme.

        Retour:
            Modifie img_carte par référence interne.

        """
        if forme == "rond":
            y, x = numpy.ogrid[-cote: cote, -cote: cote]
            index = x**2 + y**2 <= cote**2
            self.img_carte[pos_x - cote:pos_x + cote, pos_y - cote:pos_y + cote][index] = type_terrain

        elif forme == "rectangle":
            img = Image.fromarray(self.img_carte)
            drawing = ImageDraw.Draw(img)
            rect = self._get_rect(pos_x, pos_y, rd.randint(cote / 2, cote), rd.randint(cote / 2, cote), rd.randint(0, 90))

            # Une fois les coordonnées des sommets du rectangle récupérées, on le remplit à l'aide de la méthode "polygon".
            drawing.polygon([tuple(p) for p in rect], fill=type_terrain)

            # On retransforme l'image en array.
            self.img_carte = numpy.asarray(img)
            self.img_carte.flags.writeable = True

    def _toint(self, matrice):
        """Retourne une matrice compréhensible par le constructeur d'images."""
        return int(str(matrice))

    def generer_matrice_tribus(self):
        """Retourne la matrice où les individus sont remplacés par leur n° de tribu.""" 

        self.matrice_tribus = copy(self.matrice)
        for individu in self.liste_individus:
            self.matrice_tribus[individu.position_t] = individu.tribu

        self.liste_tribus_int = [int(str(tribu)) for tribu in self.liste_tribus]

    def generer_carte(self):
        """Fonction de création de carte.

        Permet de créer un monde aléatoire de type insulaire constitué de
        plusieurs éléments, sur lequel la simulation peut prendre place.
        Le processus se fait couche par couche dans l'ordre.

        Le dictionnaire de densité est modifiable de manière à changer
        l'aspect de la carte.

        Retour:
            Modifie img_carte par référence interne.

        """
        vprint(" *  Lancement de la génération du terrain...")
        densite_actuelle = 0
        surfacemax_terrain = self.surface // self.indice_terrains
        cotemax_terrain = sqrt(surfacemax_terrain / numpy.pi)

        # Dictionnaire faisant la correspondance entre chaque terrain et son entier dans la matrice.
        vprint("     > Création du dictionnaire des entiers...")
        dic_ord = ["sable", "plaine", "foret", "montagne", "neige"]
        entiers = {"sable": 1, "plaine": 2, "foret": 3, "montagne": 4, "neige": 5 }

        # Dictionnaire faisant la correspondance entre chaque terrain et sa densité sur le terrain d'en dessous.
        vprint("     > Création du dictionnaire des densités...")
        densites = {"sable" : (self.densite_cible / 100), "plaine" :  0.95, "foret" : 0.65, "montagne" : 0.50, "neige" : 0.20 }

        # Remplissage de la carte avec de l'eau.
        vprint("     > Création de l'océan...")
        self.img_carte = numpy.zeros(self.img_carte.shape, dtype=numpy.uint8)

        # Remplissage de la carte chaque terrain à la fois avec la densité correspondante
        densite_precedente = self.surface
        for terrain in dic_ord:
            densite_actuelle = 0
            vprint("     > Génération en cours... (zone: " + terrain + ") : 0% \r", end='')
            while densite_actuelle < densites[terrain]:
                # Détermine la taille et la forme du terrain
                cote = rd.randint(1, cotemax_terrain)
                forme = rd.choice(['rond', 'rectangle'])

                # Détermine le centre
                pos_x_min = cote
                pos_y_min = cote
                pos_x_max = self.largeur_img - cote
                pos_y_max = self.hauteur_img - cote
                pos_x = rd.randint(pos_x_min, pos_x_max)
                pos_y = rd.randint(pos_y_min, pos_y_max)

                # Poser un terrain si celui d'en dessous le permet
                if self.img_carte[pos_x, pos_y] <= entiers[terrain]:
                    self._poser_terrain(pos_x, pos_y, cote, forme, entiers[terrain])

                densite_actuelle = (self.img_carte == entiers[terrain]).sum() / densite_precedente
                avancement = int((densite_actuelle / densites[terrain]) * 100)
                if avancement > 100:
                    avancement = 100

                vprint("     > Génération en cours... (zone: " + terrain + ") : " + str(avancement) + "%", end='   \r')

            densite_precedente = (self.img_carte == entiers[terrain]).sum()

        # Le median_filter permet d'adoucir l'image et de la faire ressembler à une carte.
        self.img_carte = ndimage.median_filter(self.img_carte, size=self.lissage)

        # On fait une copie de img_carte pour conserver le tableau d'entiers.
        self.matrice = deepcopy(self.img_carte)

        vprint("\n *  Génération terminée.                        ")

    def generer_image(self):
        """Fonction graphique.

        Transforme un array de carte en image RGB.
        Chaque tuple correspond aux valeurs RGB du pixel sous la forme
        (Red/255, Green/255, Blue/255). On fait appel au module PIL.Image
        pour créer une image à partir du tableau.

        Arguments:
            verbose (bool):
                Active ou désactive la sortie console.

        Retour:
            Modifie img_carte par référence interne.

        """
        couleurs = {"ocean": (10/255, 65/255, 145/255), "sable": (240/255, 230/255, 140/255),
        "plaine": (154/255, 205/255, 50/255), "foret": (34/255, 139/255, 34/255), "montagne": (0/255, 80/255, 0/255),
        "neige": (255/255, 250/255, 250/255) }

        # On colore la carte suivant les couleurs précédentes
        colormap_ile = ListedColormap([couleurs['ocean'], couleurs['sable'], couleurs['plaine'], couleurs['foret'],
                                           couleurs['montagne'], couleurs['neige']], N=6)

        # On convertit en image
        couleurs_ile = plt.cm.get_cmap(colormap_ile)
        ile_coloriee = couleurs_ile(self.matrice)
        ile_coloriee_int8 = (255 * ile_coloriee).astype('uint8')
        img = Image.fromarray(ile_coloriee_int8)

        self.img_carte = img

    def generer_image_transp(self):
        """Fonction graphique.

        Elle est identique à la fonction précédente mais permet de générer
        une image transparente sauf pour les individus qui possèdent une
        couleur par tribu. Les deux images sont ensuite superposée pour
        donner l'illusion que la simulation se déroule sur la carte du
        dessous.

        Arguments:
            verbose (bool):
                Active ou désactive la sortie console.

        Retour:
            Modifie img_transp par référence interne.

        """
        nombre_tribus = len(self.liste_tribus)

        levels = list(range(0, 6)) + self.liste_tribus_int
        colors_void = [(0., 0., 0., 0.) for i in range(0, 6)]
        jet = plt.get_cmap('gist_rainbow')
        colors_tribu = [jet(x/(max(self.liste_tribus_int) - 10)) for x in range(0, nombre_tribus)]
        colors = colors_void + colors_tribu

        self.colormap_indiv, self.norm = from_levels_and_colors(levels, colors, extend='max')

        self.img_transp = self.matrice_tribus.astype(str).astype(int)

    def generer_matrices(self):
        """Génère matrices et images correspondantes.

        Génère l'image de la carte telle qu'elle sera affichée (antialisée),
        l'image de la carte qui sera utilisée, et la matrice d'ile.

        On génère d'abord une matrice d'île deux fois plus grande que la
        taille cible, on la copie en réduisant six fois (par défaut) la
        définition de manière à avoir une matrice à gérer beaucoup plus
        petite que l'image.

        """
        # On génère la matrice d'entiers redimensionnée (un sixième)
        self.matrice = misc.imresize(self.matrice, (self.largeur_matrice, self.hauteur_matrice), interp='nearest')
        self.matrice_originale = deepcopy(self.matrice)
        self.matrice = self.matrice.astype(object)

        # On génère sa représentation brute
        self.img_matrice = self.img_carte.copy()
        self.img_matrice.thumbnail((self.largeur_matrice, self.hauteur_matrice), Image.NEAREST)
        self.img_matrice = self.img_matrice.resize((self.hauteur_img // 2, self.largeur_img // 2), Image.NEAREST)
        
        # On génère sa représentation antialiasée
        self.img_carte = self.img_carte.resize((self.hauteur_img // 2, self.largeur_img // 2), Image.ANTIALIAS)

    def poser_tribu(self, nombre_tribus, type_terrain=2):
        """Place les premiers individus de la simulation.

        On va d'abord rechercher les cellules correspondant au type de 
        terrain désiré, puis définir des zones de taille équivalentes où
        l'on placera la "base".

        Arguments:
            nombre_tribus (int): 
                Nombre de tribus différentes à poser.
            type_terrain (Optional(int)):
                Type de terrain sur lequel sera placée la tribu.

        """

        # Recherche des emplacements disponibles et partage par tribu.
        coordonnees_eligibles = numpy.nonzero(self.matrice == type_terrain)
        intervalle_recherche = (len(coordonnees_eligibles[0]) // nombre_tribus)

        for k in range(0, nombre_tribus):
            index_pos = rd.randint(k * intervalle_recherche, (k + 1) * intervalle_recherche)
            base = (coordonnees_eligibles[0][index_pos], coordonnees_eligibles[1][index_pos])
            tribu = Tribu(base)

            self.matrice[(coordonnees_eligibles[0][index_pos], coordonnees_eligibles[1][index_pos])] = Individu(list(base), tribu)
            self.liste_tribus.append(tribu)

        self.generer_matrice_tribus()
    
    def mise_a_jour(self):
        """
        Mets à jour la matrice en fonction des nouvelles caractéristiques
        de chaque individu.
        TODO : améliorer

        """
        self.cycles += 1
        
        def _creer_enfant(tribu):
            self.matrice[tribu.base] = Individu(list(tribu.base), tribu)

        def _bilan():    
            if self.cycles >= 100:
                vprint("    ========")
                for tribu in Carte.liste_tribus:
                    vprint(" ⛺  Tribu " + str(tribu.numero_tribu - 10) + ":\n    ⮡   " + str(len(tribu.membres)) + " ⛄" + "\n    ⮡   " + str(tribu.nourriture) + " 🍗\n    ⮡   {0:.2f}% 💕 ".format(tribu.fertilite * 100))
                self.cycles = 0
                vprint("    ========")

        def _deplacement_alea(individu):
            """Déplace d'une case un individu.

            On choisit d'abord le déplacement que va effectuer l'indivu
            puis on vérifie que celui-ci est dans les limites de la matrice,
            ne va pas dans l'eau ou sur un autre ennemi.
            On change la l'attribu position de l'individu de manière à
            ce qu'il soit déplacé plus tard.

            """
            alea_ligne = rd.choice((-1, 0, 1))
            alea_colonne = rd.choice((-1, 0, 1))
            x_ini = deepcopy(individu.position[0])
            y_ini = deepcopy(individu.position[1])

            # On vérifie que le déplacement est dans les limites de la matrice.
            if 0 <= x_ini + alea_ligne and x_ini + alea_ligne < self.matrice.shape[0]:
                if int(str(self.matrice[individu.position[0] + alea_ligne, individu.position[1]])) < 100 and int(str(self.matrice[individu.position[0] + alea_ligne, individu.position[1]])) != 0:
                    individu.position[0] += alea_ligne
                
            if 0 <= y_ini + alea_colonne and y_ini + alea_colonne < self.matrice.shape[1]:
                if int(str(self.matrice[individu.position[0], individu.position[1] + alea_colonne])) < 100 and int(str(self.matrice[individu.position[0], individu.position[1] + alea_colonne])) != 0:
                    individu.position[1] += alea_colonne

            individu.ex_position = [x_ini, y_ini]

        def _combat_potentiel(individu, cote=10):
            """Recherche si un ennemi se trouve à proximité.

            Retour:
                True: si l'individu a toujours un ennemi potentiel.
                False: si l'individu n'a pas d'ennemi.

            """
            if individu.ennemi == None:
                pos_x = individu.position[0]
                pos_y = individu.position[1]

                # Fixe le cadre de recherche.
                #TODO : à revoir
                a = (pos_x - cote)
                b = (pos_x + cote)
                c = (pos_y - cote)
                d = (pos_y + cote)
                if a < 0:
                    a = 0
                if b >= self.matrice.shape[0]:
                    b = self.matrice.shape[0] - 1
                if c < 0:
                    c = 0
                if d >= self.matrice.shape[1]:
                    d = self.matrice.shape[1] - 1

                # Recherche autour de l'individu un potentiel ennemi qui n'est pas déjà engagé.
                ennemis = {(x, y) for x in range(a, b + 1) for y in range(c, d + 1)
                           if (self._toint(self.matrice[(x, y)]) >= 100 and self.matrice[(x, y)].ennemi is None)}

                # On copie l'ensemble pour ne pas le modifier en même temps qu'on le traverse.
                ennemis_copy = deepcopy(ennemis)
                for couple in ennemis_copy:
                    # On enlève les aliés

                    if type(self.matrice[couple]) == Individu and type(self.matrice[(pos_x, pos_y)]) == Individu:
                        if self.matrice[couple].tribu == self.matrice[(pos_x, pos_y)].tribu:
                            ennemis.remove(couple)

                if ennemis:
                    distances = {sqrt((x - pos_x)**2 + (y - pos_y)**2): (x, y) for (x, y) in ennemis}
                    if distances:
                        mind = min(distances)
                        vprint(" 👁  N°" + str(individu) + " a repéré un ennemi !")
                        vprint("    ⮡ " + str(self.matrice[distances[mind]]) + " est à {:.1f} mètres".format(mind))

                        # Les deux individus ont maintenant l'identifiant de leur cible
                        self.matrice[distances[mind]].ennemi = individu
                        individu.ennemi = self.matrice[distances[mind]]
                        return True
                else:
                    return False

            return True

        def _rencontre(individu):
            """Gère le déplacement d'un individu vers un autre."""
            x1 = deepcopy(individu.position[0])
            y1 = deepcopy(individu.position[1])
            x2 = deepcopy(individu.ennemi.position[0])
            y2 = deepcopy(individu.ennemi.position[1])

            # Deplacement du premier individu.
            if x1 < x2 and self._toint(self.matrice[x1 + 1, y1]) < 100 and self._toint(self.matrice[x1 + 1, y1]) != 0:
                individu.position[0] += 1
            elif x1 > x2 and self._toint(self.matrice[x1 - 1, y1]) < 100 and self._toint(self.matrice[x1 - 1, y1]) != 0:
                individu.position[0] -= 1
            if y1 < y2 and self._toint(self.matrice[x1, y1 + 1]) < 100 and self._toint(self.matrice[x1, y1 + 1]) != 0:
                individu.position[1] += 1
            elif y1 > y2 and self._toint(self.matrice[x1, y1 - 1]) < 100 and self._toint(self.matrice[x1, y1 - 1]) != 0:
                individu.position[1] -= 1

            individu.ex_position = [x1, y1]

        def _combat(individu):
            """Gère les combats.

            Lorsque deux individus se recontrent, chacun de leur score
            de combat est déterminé par leur expérience. C'est un nombre
            aléatoire compris entre un tiers de celle-ci et son maximum.
            L'individu ayant le meilleur score gagne, et récupère un tiers
            de l'expérience du perdant.

            """
            exp_indiv = individu.experience
            exp_ennemi = individu.ennemi.experience

            vprint(" 🔪  Combat entre " + str(individu) + " (exp: " + str(individu.experience) + ") et " + str(individu.ennemi) + " (exp: " + str(individu.ennemi.experience) + ").")

            if exp_indiv > 0:
                alea_indiv = rd.randint(exp_indiv / 3, exp_indiv)
            elif exp_indiv <= 0:
                alea_indiv = rd.randint(exp_indiv, exp_indiv + 30)
            if exp_ennemi > 0:
                alea_ennemi = rd.randint(exp_ennemi / 3, exp_ennemi)
            elif exp_ennemi <= 0:
                alea_ennemi = rd.randint(exp_ennemi, exp_ennemi + 30)

            
            vprint("    ⮡ Score : " + str(int(alea_indiv)) + " vs. " + str(int(alea_ennemi)))

            if alea_indiv >= alea_ennemi:
                individu.experience += (exp_ennemi // 3)
                individu.ennemi.vivant = False
                individu.ennemi.raison = " tué par " + str(individu.rang)
                individu.ennemi = None

            else:
                individu.ennemi.experience += (exp_indiv // 3)
                individu.vivant = False
                individu.raison = " tué par " + str(individu.ennemi.rang)
                individu.ennemi.ennemi = None

        while Carte.liste_individus and len(Carte.liste_tribus) > 1:
            
            for individu in Carte.liste_individus:

                if individu.vivant:
                    
                    # 1. VIEILLESSE
                    individu.etape()
                    
                    # 2. DÉPLACEMENT
                    if _combat_potentiel(individu):
                        if sqrt((individu.ennemi.position[0] - individu.position[0])**2 + (individu.ennemi.position[1] - individu.position[1])**2) <= 1:
                            _combat(individu)
                        else:
                            _rencontre(individu)
                    else:
                        _deplacement_alea(individu)
                    
                    self.matrice[individu.ex_position_t] = self.matrice_originale[individu.ex_position_t]
                    self.matrice[individu.position_t] = individu
                    
                    # 3. GESTION TERRAIN
                    if self.matrice_originale[individu.position_t] == 3: 
                        alea = rd.randint(0, 100)
                        if alea > 95:
                            individu.tribu.nourriture += 1
                    elif self.matrice_originale[individu.position_t] == 4:
                        alea = rd.randint(0, 100)
                        if alea > 85:
                            individu.tribu.nourriture += 1
                        if alea < 15:
                            if individu.experience >= 10:
                                individu.experience -= 10
                    elif self.matrice_originale[individu.position_t] == 5:
                        individu.age += 1
                        if individu.experience >= 2:
                            individu.experience -= 2

                    # 4. REPRODUCTION
                    if individu.tribu.fertilite > 1:
                        _creer_enfant(individu.tribu)
                        individu.tribu.nourriture = 0

                else:
                    Carte.liste_individus.remove(individu)
                    individu.tribu.membres.remove(individu)
                    ancienne_position = deepcopy(individu.position_t)
                    self.matrice[ancienne_position] = self.matrice_originale[ancienne_position]
                
                _bilan()
                
            for tribu in self.liste_tribus:
                tribu.calc_nb_indiv()
                if len(tribu.membres) == 0:
                    self.liste_tribus.remove(tribu)
                    vprint("\033[91m 🚫  La tribu " + str(tribu.numero_tribu - 10) + " a été anéantie !\033[0m")
                    
                self.generer_matrice_tribus()
                self.generer_image_transp()              
                    
            return True 

        vprint(" *  Fin de la simulation.")
        return False


class Tribu(Carte):
    """TODO: docstring """
    numero_tribu = 9

    def __init__(self, base):
        """TODO: docstring """
        Tribu.numero_tribu += 1
        self.numero_tribu = Tribu.numero_tribu
        self.base = base
        self.nourriture = 0
        self.membres = []
        vprint("\033[92m ⛳  La base de la tribu " + str(self.numero_tribu - 10) + " est placée en " + str(base) + ".\033[0m")

    def __str__(self):
        return str(self.numero_tribu)

    def calc_nb_indiv(self):
        for individu in Carte.liste_individus:
            if individu.tribu == self and individu not in self.membres:
                self.membres.append(individu)

    @property
    def fertilite(self):
        if len(self.membres) != 0:
            return self.nourriture / len(self.membres)
        else:
            return 0
    


class Individu(Tribu):
    """Classe des individus.

    Chaque individu placé dans la matrice est un objet et possède des
    propriétés ainsi que des méthodes.

    Variables:
        rang_individu (int):
            Variable de classe, est la même pour chaque instance créée.
            Comme elle est incrémentée à chaque nouvel individu, cela
            donne son rang.

    Attributs:
        position (list):
            Liste des coordonnées où est placé l'individu.
        tribu (int):
            Numéro de tribu à laquelle appartient l'individu.

    Propriétés:
        position_t (tuple):
            Retourne la position sous forme de tuple et non de liste,
            utile quand on doit la placer dans un index.
        ex_position_t (tuple):
            De même pour la variable ex_position.

    """
    rang_individu = 99

    def __init__(self, position, tribu):
        """Constructeur de classe.

        Permet d'initialiser les variables supplémentaires nécessaires à
        la simulation.

        Attributs:
            ex_position (list):
                Position précédente avant déplacement.
            age (int):
                Nombre de cycles qu'à traversé l'individu, il décède
                quand l'age maximal est atteint.
            experience (int):
                Permet de faire varier l'issue des combats. Elle est
                croissante jusqu'au cycle 100 puis décroit à partir du
                cycle 900.
            ennemi (Individu):
                Référence objet à l'individu en chasse. En tant qu'objet
                mutable, il est possible de modifier les attributs de
                celui-ci depuis cette une autre instance.
            vivant (bool):
                État de vie ou de mort de l'indivu, permet de le retirer
                de la carte et de la liste des individus.
            raison (str):
                Raison de la mort pour la sortie console.

        """
        self.position = position
        self.ex_position = position
        self.tribu = tribu
        self.age = 0
        self.experience = 0
        self.ennemi = None
        self.vivant = True
        self.raison = ""
        
        Individu.rang_individu += 1
        self.rang = Individu.rang_individu
        Carte.liste_individus.append(self)
        
        vprint(" ⛄  N°" + str(self.rang) + " est né dans la tribu " + str(tribu.numero_tribu - 10) + ".")
        
    def __str__(self):
        return str(self.rang)

    def __del__(self):
        vprint(" ✝  N°" + str(self.rang) + " est mort" + self.raison + ".")

    @property
    def position_t(self):
        return tuple(self.position)
    @property
    def ex_position_t(self):
        return tuple(self.ex_position)

    def _croissance(self):
        """Incrémente le cycle et modifie l'expérience si nécessaire."""
        if self.age < 500:
            self.age += 1

            if self.age <= 100:
                self.experience += 1
            if self.age >= 400:
                self.experience -= 1
        else:
            self.raison = " de vieillesse"
            self.vivant = False
                
    def etape(self):
        self._croissance()

        
if __name__ == "__main__":

    # monEnv = Carte(1366, 768)
    monEnv = Carte(720, 720, echelle=10)
    monEnv.generer_carte()
    monEnv.generer_image()
    monEnv.generer_matrices()   
    monEnv.poser_tribu(4)
    monEnv.generer_matrice_tribus()
    monEnv.mise_a_jour()

    dpi = 96
    figsize = monEnv.img_carte.size[0] / float(dpi), monEnv.img_carte.size[1] / float(dpi)
    fig = plt.figure(figsize=figsize, dpi=dpi, facecolor=(10/255, 65/255, 145/255))
    fig.add_axes([0.0, 0.0, 1.0, 1.0], frameon=False)

    plt.figimage(monEnv.img_carte)
    im = plt.imshow(monEnv.img_transp, cmap=monEnv.colormap_indiv, norm=monEnv.norm, interpolation='nearest', animated=True)

    def updatefig(*args):
        monEnv.mise_a_jour()
        im.set_array(monEnv.img_transp)
        return im,

    ani = anim.FuncAnimation(fig, updatefig, interval=100)
    plt.show()
