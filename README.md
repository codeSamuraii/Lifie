# Lifie
Lifie est un générateur de carte aléatoire et simulateur de comportement tribal.

La carte générée est composée de plusieurs terrains ayant chacun leurs attributs. Un certain nombre de tribus sera ensuite placé sur celle-ci et on étudiera leur comportement. Les individus viseront à se reproduire grâce à la nourriture qu’ils collectent. Les différentes ressources de la carte leur permettront ou non de prospérer.

On distinguera plusieurs types de ressources : les ressources basiques et les ressources spéciales. Les ressources basiques, nourriture et fer, permettent respectivement de se reproduire et d’être plus résistant aux attaques. Les ressources spéciales (or et gemmes) apportent des bonus : l’or permet une meilleure reproduction lorsque la population atteint un certain niveau, les gemmes permettent de se sortir d’un combat perdu.

Chaque type de terrain possède des caractéristiques différentes quant à l’apparition de nourriture et la vitesse de déplacement des individus.

La simulation s’arrête lorsqu’une colonie a atteint un nombre maximal d’individus ou n’en a plus.

## Lancement
### Installation des dépendances (GNU/Linux)
- SciPy : 
`sudo apt-get install python3-dev python3-numpy python3-scipy python3-matplotlib ipython3 ipython3-notebook python3-pandas python3-sympy python3-nose`
- Pillow : 
`sudo apt-get install python3-pil.imagetk`
`sudo pip3 install pillow`
- Tkinter : 
`sudo apt-get install python3-tk`
- Matplotlib : 
`sudo pip3 install matplotlib`

### Lancement du programme
`python3 module_gui.py`
