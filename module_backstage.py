# -*- coding: utf-8 -*-
"""Lifie - Module backstage

Ce module contient des fonctions diverses placées séparément pour alléger le code.
(Module bordel)

"""
import numpy
from numpy import random as rd
from PIL import Image, ImageDraw

def get_rect(x, y, width, height, angle):
    rect = numpy.array([(0, 0), (width, 0), (width, height), (0, height)])
    theta = (numpy.pi / 180.0) * angle
    R = numpy.array([[numpy.cos(theta), -numpy.sin(theta)],
                  [numpy.sin(theta), numpy.cos(theta)]])
    offset = numpy.array([x, y])
    transformed_rect = numpy.dot(rect, R) + offset
    return transformed_rect

def poser_terrain(ile, pos_x, pos_y, rayon, forme, type_terrain):
    if forme == "rond":
        y, x = numpy.ogrid[-rayon : rayon, -rayon : rayon]
        index = x**2 + y**2 <= rayon**2
        ile[pos_x - rayon:pos_x + rayon, pos_y - rayon:pos_y + rayon][index] = type_terrain
        return ile
    elif forme == "rectangle":
        img = Image.fromarray(ile)
        drawing = ImageDraw.Draw(img)
        rect = get_rect(pos_x, pos_y, rd.randint(rayon/2, rayon), rd.randint(rayon/2, rayon), rd.randint(0, 90))
        drawing.polygon([tuple(p) for p in rect], fill=type_terrain)
        ile = numpy.asarray(img)
        ile.flags.writeable = True
        return ile
        
        
# def ile_vers_image_old(ile):
#     """
#     Fonction graphique
    
#     /!\ OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD /!\
#     /!\ OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD /!\
#     /!\ OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD /!\
    
#     Transforme un array de carte en image RGB.
#     Chaque tuple correspond aux valeurs RGB du pixel sous la forme (R, G, B).
    

#     Arguments:
#         ile (array): Array à transformer

#     Retour:
#         PIL.Image: Image sous forme de tableau contenant des tuples (R, G, B)
#     """
#     print("[i] Création de l'image...          \r", end='')
#     ile_rgb_applatie = numpy.zeros(ile.size, dtype='int, int, int').ravel()
#     ile_decimale_applatie = ile.ravel()
    
#     for case in range(0, len(ile_decimale_applatie)):
        
#         # Les variations permettent de donner un effet "moquette" au terrain.
#         var_r, var_g, var_b = rd.randint(-10, 10), rd.randint(-10, 10), rd.randint(-10, 10)

#         if ile_decimale_applatie[case] == 0:
#             ile_rgb_applatie[case] = (10, 65, 145)                # Bleu marine
#         elif ile_decimale_applatie[case] == 1:
#             ile_rgb_applatie[case] = (240 + 0.5*var_r, 230 + 0.5*var_g, 140 + 0.5*var_b)      # Jaune sable (faibles variations) 
#         elif ile_decimale_applatie[case] == 2:
#             ile_rgb_applatie[case] = (154 +   1*var_r, 205 +   1*var_g, 50 +    1*var_b)      # Vert clair (variation normales)
#         elif ile_decimale_applatie[case] == 3:
#             ile_rgb_applatie[case] = (34 +    2*var_r, 139 +   2*var_g, 34 +    2*var_b)      # Vert (variations marquées)
#         elif ile_decimale_applatie[case] == 4:
#             ile_rgb_applatie[case] = (0 +     3*var_r, 80 +    3*var_g, 0 +     3*var_b)      # Vert (fortes variations)
#         elif ile_decimale_applatie[case] == 5:
#             ile_rgb_applatie[case] = (224, 255, 255)            # Bleu très clair


#     liste_rgb = ile_rgb_applatie.tolist()
#     image = Image.new('RGB', ile.shape)
#     image.putdata(liste_rgb)
    
#     print("[*] Création de l'image... OK.")
#     image.show()
#     return image
