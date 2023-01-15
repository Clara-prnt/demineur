# --- Bibliothèques utilisées ---
from functools import partial
import tkinter as tk
from random import seed
from random import randint


# --- Préparation du jeu ---
def diff_size(diff):
    """
        sert à déterminer le nombre de cases du jeu
        entrées : diff (difficulté) avec trois valeurs possibles : easy, normal, hard
        sortie : renvoie les coordonées de x (colonnes) et y (lignes) correspondant à la difficulté
    """
    global col, row
    if diff == "hard":
        col = 15
        row = 15
    elif diff == "normal":
        col = 12
        row = 10
    elif diff == "easy":
        col = 8
        row = 7
    else:
        print("Nous ne pouvons pas recourir à la demande, veuillez réessayer \n")
        return diff_size(str(input("Difficulté : easy/normal/hard \n")))

# --- Initialisation des grilles ---
class Grid:

    def new_grid2(m):
        TT = []

        for j in range(m):
            TT.extend([j])

        return TT

    def new_grid(n, m):
        T = []

        for i in range(n):
            T.append(Grid.new_grid2(m))

        return T

    def init_grid(n, m, grid):
        for i in range(n):
            for j in range(m):
                grid[i][j] = 0

    def bombe_grid(n, m, coord_bombes):
        """
        Création d'un tableau référençant les bombes (1) et le reste des cases (0) aléatoirement
        entrée : n, m = limites du démineur, coord_bombes = liste de liste (= grille de bombes)
        sortie : aucune (mais retenue des coordonées des bombes)
        """
        global bombes
        seed()
        for i in range(n):
            for j in range(m):
                if 2 > randint(0, 20):
                    coord_bombes[i][j] = 1
                else:
                    coord_bombes[i][j] = 0

    def how_bombe(n, m, coord_bombes, near_bombes):
        """
        Permet de déterminer le chiffre présent dans les cases au alentour d'une bombe (1,2,3,4...)
        """
        chiffre = 0
        for i in range(n):
            for j in range(m):
                for k in range(-1, 2, 1):
                    for h in range(-1, 2, 1):
                        try:
                            if (coord_bombes[i + k][j + h] == 1) and (i + k >= 0) and (j + h >= 0) and (
                                    (k != 0) or (h != 0)):  # si case autour = bombe,
                                chiffre = chiffre + 1  # ajout de 1 à la case autour des bombes
                        except IndexError:
                            pass
                near_bombes[i][j] = chiffre
                chiffre = 0

    def flag_bombes(n, m, flag_count):
        """
        Permet de créer une grille qui par la suite pourra changer la valeur de flag_count[i][j] en 1
        lorsqu'il y a un drapeau posé sur une bombe
        """
        for i in range(n):
            for j in range(m):
                flag_count[i][j] = 0

# --- Préparation des grilles ---
class Plateau:

    def __init__(self, n, m):
        self.n = n
        self.m = m

        self.all_grid()
        self.all_init_grid()

    def all_grid(self):
        """
        forme les différentes "sous-grilles" cachées sous les boutons du démineur
        entrées : aucune
        sortie : grille coord_bombes, near_bombes, dig_case et flag_count
        """
        self.coord_bombes = Grid.new_grid(self.n,
                                          self.m)  # pour les coordonées des bombes (0 : pas de bombe / 1 : bombe)
        self.near_bombes = Grid.new_grid(self.n,
                                         self.m)  # pour les cases adjacentes aux bombes (x bombes autour = chiffre x)
        self.flag_count = Grid.new_grid(self.n,
                                        self.m)  # compter le nombre de drapeaux posés sur une bombe
        self.dig_case = Grid.new_grid(self.n,
                                      self.m)  # savoir si une case est creusée (0 : pas creusée, 1 creusée)

    def all_init_grid(self):
        """
        Attribue les valeurs coorespondantes aux différentes grilles créées
        """
        Grid.bombe_grid(self.n, self.m, self.coord_bombes)
        Grid.how_bombe(self.n, self.m, self.coord_bombes, self.near_bombes)
        Grid.flag_bombes(self.n, self.m, self.flag_count)
        Grid.init_grid(self.n, self.m, self.dig_case)


# --- Début des actions du joueur ---
class Game:

    def creuser(i, j, Plat, A):
        """
        Détermine ce qu'affiche un bouton une fois cliqué (ou creusé par récursion)
        """
        Plat.dig_case[i][j] = 1  # case est creusée
        if Plat.coord_bombes[i][j] == 1:  # si bombe sous la case
            A.pt[i][j] = tk.Button(A.plateau, width=5, height=1, text="BOUM", bg="red",
                                   command=partial(Game.is_mine, i, j, Plat, A))
            A.pt[i][j].grid(row=i, column=j)

        elif (Plat.coord_bombes[i][j] == 0) and (Plat.near_bombes[i][j] != 0):  # si pas de bombe et bombes autour
            A.pt[i][j] = tk.Button(A.plateau, width=5, height=1, text=Plat.near_bombes[i][j], bg="blue",
                                   command=partial(Game.is_mine, i, j, Plat, A))
            A.pt[i][j].grid(row=i, column=j)

        elif (Plat.coord_bombes[i][j] == 0) and (Plat.near_bombes[i][j] == 0):  # pas une bombe et pas de bombes autour
            A.pt[i][j] = tk.Button(A.plateau, width=5, height=1, text="", bg="gray",
                                   command=partial(Game.is_mine, i, j, Plat, A))
            A.pt[i][j].grid(row=i, column=j)

    def recur(i, j, Plat, A):
        """
        Permet de creuser par récursivité des cases (grises) qui ne sont à coté d'aucune bombe, et la récursivité
        stoppe à l'approche d'une bombe (apparition de cases avec chiffres)
        """
        if Plat.coord_bombes[i][j] == 0:  # si pas de mine sur les coordonnées ij
            Game.creuser(i, j, Plat, A)  # on creuse le bouton sur les coordonnées ij
            for k in range(-1, 2, 1):
                for h in range(-1, 2, 1):
                    try:
                        if (Plat.dig_case[i + k][j + h] == 0) and (Plat.near_bombes[i + k][j + h] == 0) and \
                                (i + k >= 0) and (j + h >= 0) and \
                                ((k != 0) or (h != 0)):  # si case pas déjà creusée et si pas de mines autour
                            try:
                                Game.recur(i + k, j + h, Plat, A)  # on relance
                            except:
                                pass
                    except IndexError:
                        pass
                    try:
                        if Plat.near_bombes[i + k][j + h] != 0:  # si mine autour
                            try:
                                Game.creuser(i + k, j + h, Plat, A)
                            except:
                                pass
                    except IndexError:
                        pass

    def is_mine(i, j, Plat, A):
        Game.creuser(i, j, Plat, A)

        if Plat.near_bombes[i][j] == 0:  # si case est "grise" / sans chiffre
            Game.recur(i, j, Plat, A)

        if Plat.coord_bombes[i][j] == 1:  # si mine
            A.life.configure(text='GAME OVER, YOU LOST')

    def replay(col, row, Plat, A):
        A.all_supp()
        Plat.all_init_grid()
        A.fen_1()
        A.fen_2(col, row, Plat)  # mêmes coordonnées qu'au début
        A.fen_3(col, row, Plat)


    def clic_droit(self, A, i, j, Plat, bouton):
        bouton.configure(text="FLAG", bg="green")
        if Plat.coord_bombes[i][j] == 1:  # si présence d'une bombe en dessous du drapeau
            Plat.flag_count[i][j] = 1 # le drapeau est posé sur une bombe
        if Game.compare(Plat.flag_count, Plat.coord_bombes, i=0) == 1:  # si les grilles sont identiques
            A.life.configure(text='GAME OVER, YOU WON')

    def compare(liste_flag, liste_bombe, i):
        """
        permet de comparer si les grilles de bombes et de flag sont identiques (le joueur a trouvé toutes les bombes)
        """
        next = 0
        nb_ligne = Plat.n
        for val_flag in liste_flag[i]:
            if val_flag != liste_bombe[i][next]:
                return None
            next += 1
        if i >= nb_ligne - 1:  # si i (allant de 0 à x = nb_lignes = x+1)
            return True
        return Game.compare(liste_flag, liste_bombe, i + 1)


# --- Définition des fenêtres Tkinter ---
class App:

    def __init__(self, col, row, Plat):

        self.fen_set()

        self.fen_1()
        self.fen_2(col, row, Plat)
        self.fen_3(col, row, Plat)

        self.fen.mainloop()

    def fen_set(self):
        self.fen = tk.Tk()
        self.fen.title('demineur')
        self.fen.geometry('800x500')

    def fen_1(self):
        self.content = tk.Frame(self.fen, width=900, height=800)  # contient tout les groupes de widgets
        self.plateau = tk.Frame(self.content, width=500, height=500)  # groupe widgets des grilles

        self.content.place(x=0, y=0)
        self.plateau.place(x=80, y=80)

    def fen_2(self, col, row, Plat):
        self.pt = Grid.new_grid(col, row)
        for i in range(col):
            for j in range(row):
                self.pt[i][j] = tk.Button(self.plateau, width=5, height=1, text="",
                                          command=partial(Game.is_mine, i, j, Plat, self))
                self.pt[i][j].bind("<Button-3>",
                                   partial(Game.clic_droit, A=self, i=i, j=j, Plat=Plat, bouton=self.pt[i][j]))
                self.pt[i][j].grid(row=i, column=j)

    def fen_3(self, col, row, Plat):
        self.life = tk.Label(text="GAME")
        self.replay = tk.Button(text="Rejouer", command=lambda: Game.replay(col, row, Plat, self))

        self.life.place(x=10, y=10)
        self.replay.place(x=10, y=30)

    def all_supp(self):
        self.life.destroy()


# --- Jeu d'essais ---



# --- mise en place du programme ---
diff_size(str(input("Difficulté : easy/normal/hard \n")))
Plat = Plateau(col, row)
A = App(col, row, Plat)
