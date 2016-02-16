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
