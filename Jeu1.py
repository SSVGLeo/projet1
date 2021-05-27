import pygame           #Import du module pygame.
from pygame import mixer#Import du module mixer venant de pygame permettant de jouer des sons.
import os               #Import du module os.
import random           #Import du module random.

from pygame.constants import FULLSCREEN    #Import du module FULLSCREEN de pygame pour mettre le jeu en grand écran.

mixer.init()  #initialise le module mixer
pygame.init() #initialise les modules importé de pygame


Largeur_fenetre = 1200                     #Variable largeur de la fenetre
hauteur_fenetre = int(Largeur_fenetre0.8) #variable hauteur de la fenetre

fenetre = pygame.display.set_mode((Largeur_fenetre, hauteur_fenetre),FULLSCREEN) #Création de la fenêtre. avec ajout de l'argument FULLSCREEN pour mettre en grand écran la fenêtre mais en gardant la taille qui à était défini, soit 1200x(12000.8).
pygame.display.set_caption('Jeu')

#fréquence d'image/temps
clock = pygame.time.Clock()     #timer
FPS = 60                        #images par secondes.


#création variables du jeu:
GRAVITE = 0.75                     #création de gravité pour permettre au joueur de tomber.
Unite = 40                         #définition d'une "Unite de mesure" du jeu.

#variables de mouvements du joueur:
bouger_gauche = False
bouger_droite = False
frapper = False


#sonds et effets du jeu:
pygame.mixer.music.load('images/sound/musique1.mp3')            #musique de fond.
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1, 0.0, 5000)

son_saut = pygame.mixer.Sound('images/sound/saut.mp3')          #son de saut.
son_saut.set_volume(0.2)                                        #baisse le volume du son.
son_frapper = pygame.mixer.Sound('images/sound/epee1.mp3')      #son d'épée
son_frapper.set_volume(0.2)                                     #baisse le volume du son.

#mportation des images:
projectile_img = pygame.image.load('images/attaque/vent.png').convert_alpha()
projectile_img1 = pygame.image.load('images/attaque/vent1.png').convert_alpha()


#background + couleurs:
Background = pygame.image.load('images/background/decor.png').convert_alpha()       #couleurs d'arrière plan.
Background_Sol = pygame.image.load('images/background/sol.png').convert_alpha()       #couleurs d'arrière plan.
Rouge = (255,0,0)
Vert = (0,190,30)
Gris = (128,128,128)
Blanc= (250,250,250)


font = pygame.font.SysFont('Times new roman', 30)   #police d'écriture
font2 = pygame.font.SysFont('Times new roman', 22)   #police d'écriture n°2
def draw_text(text,font,text_couleur,x,y):
    """
    Fonction permettant d'ajouter du text
    Arguments: 
        text: str du text à afficher
        font: str de la police d'écriture à utiliser
        text_couleur: la couleur du texte
        x: int de la position du texte sur l'axe x
        y: int de la position du texte sur l'axe y
    """    
    img = font.render(text,True,text_couleur)
    fenetre.blit(img,(x,y))



#fonction qui colore l'arrière plan:
def draw_Background():
    """
    Fonction permettant d'ajouter un arrière-plan.
    Arguments: 
        aucun
    """
    fenetre.blit(Background, (0,0))         #affichage de l'arrière plan.
    fenetre.blit(Background_Sol, (0,480))   #affichage de l'arrière plan du sol.


#Classe permettant de créer de spersonnages:
class Personnage(pygame.sprite.Sprite):
    def __init__(self,char_type,x,y,scale,speed,stamina):
        """
        méthode d'initialisation de la classe.
        Arguments: 
            self
            x: int de la position du joueur sur l'axe x
            y: int de la position du joueur sur l'axe y
            scale: int de la taille du joueur
        """
        pygame.sprite.Sprite.__init__(self)
        self.vivant = True                                 #variable qui vérifie que le personnage est vivant.
        self.char_type = char_type                         #type de personnage qui va permettre de faire des animations pendants les mouvements.
        self.speed = speed                                 #vitesse de mouvement du joueur.
        self.stamina = stamina                             #création d'une variable de stamina mais qui va varier.                                                           
        self.start_stamina = stamina                       #variable qui ajoute de la stamina au jouer, variable de base.
        self.frapper_cd = 0                                #création d'un temps de récupération (cooldown).
        self.PV = 100                                      #création de point de vie des personnages qui va varier avec les dégats etc.
        self.PV_max = self.PV                              #variable point de vie de base                        
        self.direction = 1                                 #direction du personnage.
        self.mvt_y = 0                                     #variable de mouvement vertical.
        self.saut = False                                  #variable qui vérifie que le joueur saute.
        self.in_air = True                                 #variable qui vérifie quand le joueur est en l'air.
        self.flip = False                                  #permet de changer la direction du personnage quand il avance à droite ou à gauche .
        self.animation_list = []                           #création d'une liste qui accueilleras les animations du personnage
        self.frame_index = 0                               #repère de frame d'animation.
        self.action = 0                                    #variable qui permet d'accéder aux différente animation par exemple 1 pour courir.
        self.update_delay = pygame.time.get_ticks()        #délai à laquelle se rafraichi l'animation
        self.timer = 0                                     #création d'un timer.
        
        #varaible de l'IA.
        self.immobile = False                              #variable qui défini quand l'IA est immobile.
        self.Timer_Immobile = 0                            #variable qui défini un timer de tout les combien de temps l'IA seras immobile.
        self.FovIA = pygame.Rect(0, 0, 300 ,20)            #on créer un champs de vision (Fov = field of view) de l'ennemi qui va servir à détecter le joueur.
        
        #importation des images du personnage:
        animation_types = ['Immobile', 'Courir', 'Sauter', 'Mort', 'Taper']
        for animation in animation_types:
            #réinitialise la liste temporaire des images:
            temp_list=[]                                                                                        #liste temporaire dans laquel vont être stocké les animations pour éviter qu'elle s'accumulent l'une après les autres dans "animation_list".
            #compte le nombre d'image dans le dossier:
            nombre_images = len(os.listdir(f'images/{self.char_type}/{animation}'))                             #créer une liste de tout les élément du répertoire.
            for i in range (nombre_images):
                img = pygame.image.load(f'images/{self.char_type}/{animation}/{i}.png').convert_alpha()                                     
                img = pygame.transform.scale(img, (int(img.get_width()*scale), int(img.get_height()*scale)))    #on agrandit l'image du joueur.
                temp_list.append(img)                                                                           #on ajoute les animations à la fin de la liste animation_list.
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()                                                                   #création d'un réctangle autour du jouer pour permettre d'appliquer les collisions/mouvement etc.
        self.rect.center = (x,y)                                                                            #on positionne le réctangle sur les coordonée x et y.

    

    def update(self):
        """
        Méthode qui permet d'appeler toute les updates que l'on utilise.
        Arguments:
            self
        """
        self.rafraichissement_animation()
        self.check_vivant()
        #update cooldown:
        if self.frapper_cd > 0:
            self.frapper_cd -= 1


    def bouger(self,bouger_gauche,bouger_droite):
        """
        méthode qui permet au joueur de pouvoir bouger
        Arguments:
            self
            bouger_gauche : variable permettant de bouger à gauche.
            bouger_droite :  variable permettant de bouger à droite.
        """ 
        #réinitialisé les variables de mouvement:
        dx=0            #variables de mouvement sur l'axe x.
        dy=0            #variables de mouvement sur l'axe y.

        #attribution des variables si on bouge à gauche ou à droite:
        if bouger_gauche:
            dx = -self.speed                    #mouvement à valeurs négatif car on bouge vers la gauche.
            self.flip = True                    #on change le joueur de sens.
            self.direction = -1                 #direction = -1 donc vers la gauche
        if bouger_droite:
            dx = self.speed                     #mouvement à valeurs positif car on bouge vers la droite.
            self.flip = False
            self.direction = 1                  #direction = 1 donc vers la droite

        #pour sauter:
        if self.saut == True and self.in_air == False:
            self.mvt_y = -11                    #chiffre négatif car l'axe y commence à 0 en haut de l'écran et augmente quand on descend, étant donné que l'on va vers le haut quand on saute, alors on créer une valeur négative.
            self.saut = False
            self.in_air = True

        #application de la gravité pour que le joueur retombe après avoir sauté:
        self.mvt_y += GRAVITE
        if self.mvt_y > 10:
            self.mvt_y
        dy += self.mvt_y

        #vérifie les collision avec le sol:
        if self.rect.bottom + dy > 480:
            dy = 480 - self.rect.bottom
            self.in_air = False 

        #update de la position du rectangle:
        self.rect.x += dx                       #mouvement du rectangles sur l'axe x.
        self.rect.y += dy                       #mouvement du rectangles sur l'axe y.

    
    def collision(self):
        """
        Méthode qui permet aux personnage de ne pas sortir de l'écran
        arguments:
            self
        """
        if self.rect.right > Largeur_fenetre:
            self.rect.right = Largeur_fenetre
        if self.rect.left < 0:
            self.rect.left = 0


    def frapper(self):
        """
        Méthode qui permet au joueur de frapper
        Arguments:
            self
        """ 
        #permet d'attendre une certains temps avant de pouvoir récrer un projectile pour éviter d'en avoir en boucle:
        if self.frapper_cd == 0 and self.stamina > 0:        
            self.frapper_cd = 20
            projectile = Projectile(self.rect.centerx + (0.7 * self.rect.size[0] * self.direction), self.rect.centery, self.direction,self.flip,self.stamina)   #créer un instance projectile centrer sur le rectangle du joueur.
            projectile_group.add(projectile)    #ajoute l'instance projectile au groupe
            #Rougeuction de la stamina:
            self.stamina -= 1
            self.update_action(4)  #joue l'animation de frapper
            son_frapper.play()



    def IA(self):
        """
        Méthode qui permet de créer des IA (ennemis qui bouge tout seul)
        Arguments:
            self
        """
        #si le joueur est vivant:
        if self.alive and joueur.alive:
            
            #choisi un nombre aléatoire entre 1 et 200 pendant que l'IA est en mouvement, si le nombre est 1 l'IA deviens immobile.
            if self.immobile == False and random.choice(range(1,200)) == 1:
                self.immobile = True
                self.update_action(0)                   #quand l'IA est immobile l'animation 0=immobile est appelé.
                self.Timer_Immobile = 100
            
            #si l'ennemi est vivant:
            if ennemi.vivant == True and joueur.vivant == True:
                #vérifie si l'IA est proche du joueur:
                if self.FovIA.colliderect(joueur.rect):
                    self.update_action(4)       #4=frapper l'IA arrête de bouger et s'arrête devant le joueur.
                    self.frapper()              #frappe 
                else:
                    #quand l'IA n'est pas immobile:
                    if self.immobile == False:
                        if self.direction == 1:                 #si il est tourné vers la droite
                            ia_moving_right = True              #l'IA va vers la droite.
                        else:
                            ia_moving_right = False
                        ia_moving_left = not ia_moving_right            #inverse de l'IA qui va vers la droite, autrement dit l'IA va vers la gauche.
                        self.bouger(ia_moving_left, ia_moving_right)
                        self.update_action(1)                           #quand l'IA est en mouvement l'animation 1=courir est appelé.
                        self.timer += 1
                        
                        #le champ de vision de l'ennemi bouge en même temps que lui:
                        self.FovIA.center = (self.rect.centerx + 150 * self.direction, self.rect.centery)

                        if self.timer > Unite*3:
                            self.direction *= -1
                            self.timer *= -1
                    else:
                        #permet de faire en sorte que l'IA soit immobile un temps données puis reprend sa course.
                        self.Timer_Immobile -= 1
                        if self.Timer_Immobile <= 0:
                            self.immobile = False
            
            if joueur.vivant == False and ennemi.vivant:
                ennemi.update_action(0)       #les ennemies prennent un position immobile quand le joueur est mort.
                
    def rafraichissement_animation(self):
        """
        Méthode qui met à jour l'animation du joueur.
        Arguments:
            self
        """ 
        DELAI_ANIMATION = 170                                                               #on défini la vitesse à laquelle l'animation se joue.
        self.image = self.animation_list[self.action][self.frame_index]                     #rafraichi l'animation en fonction de la frame actuelle.
        #vérifie si il y a assez de temps qui est passé depuis le dernier rafraichissement:
        if pygame.time.get_ticks() - self.update_delay > DELAI_ANIMATION:  
            self.update_delay = pygame.time.get_ticks()
            self.frame_index += 1
        
        #si l'animation est finie elle reviens au début:
        if self.frame_index >= len(self.animation_list[self.action]):     
            if self.action == 3:                        
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
        

        

    def update_action(self, new_action):
        """
        méthode qui met à jour l'animation des actions
        Arguments:
            self
            new_action: nouvelle action qui permet de la comparer avec la précédente pour voir si elle est différente.
        """        
        #vérifie si la nouvelle action est différente à la précédente.
        if new_action != self.action:
            self.action = new_action
            #met à jour les paramétre d'animation
            self.frame_index = 0
            self.update_delay = pygame.time.get_ticks()


    def check_vivant(self):
        """
        méthode qui vérifie si le joueur est vivant.
        Arguments:
            self
        """       
        if self.PV <=0: 
            self.PV = 0
            self.speed = 0
            self.vivant = False
            self.update_action(3)  #joue l'animation de mort.
    

        #si le joueur est vivant:
        if joueur.vivant:
            #quand le timer atteind un certains nombre la stamina remonte
            self.timer += 1
            self.collision()
            if self.timer > Unite*3:
                joueur.stamina += 1
                joueur.PV += 5
                self.timer *= -1

            #permet de ne pas faire déborder la bar de stamina:     
            if joueur.stamina > joueur.start_stamina:
                joueur.stamina = joueur.start_stamina

            #permet de ne pas faire déborder la bar de vie:
            if joueur.PV > joueur.PV_max:
                joueur.PV = joueur.PV_max
            
        else:
            joueur.stamina = 0  #la bar de stamina du jouer tombe à 0 quand il meurt.
            joueur.kill()


    def apparition(self):
        """
        méthode qui affiche le joueur dans la fenêtre.
        Arguments:
            self
        """
        fenetre.blit(pygame.transform.flip(self.image, self.flip, False), self.rect) 


#class pour la bar de vie:
class BarDeVie():
    def __init__(self,x,y,PV,PV_max):
        """
        méthode d'initialisation de la classe.
        Arguments: 
            self
            x: int de la position de la bar sur l'axe x
            y: int de la position du la bar sur l'axe y
            PV: int du nombre de point de vie actuelle du joueur.
            PV_max: int du nombre de point de vie max du joueur.
        """
        self.x = x                              
        self.y = y
        self.PV = PV
        self.PV_max = PV_max

    def draw(self,PV):
        """
        méthode qui permet de mettre à jour la bar de vie
        Arguments:
            self
            stamina: int du nombre de point de vie actuelle du joueur.
        """
        self.PV = PV
        ratio = self.PV / self.PV_max                                       #le ratio représente la vie divisé par la vie maximal ce qui va permettre de réduire la taille de la bar de vie au fur et a mesure que l'on prend des dégats.
        pygame.draw.rect(fenetre, Gris, (self.x, self.y, 400, 20))          #on dessine une bar grise.
        pygame.draw.rect(fenetre, Rouge, (self.x, self.y, 400*ratio, 20))     #on dessine une bar rouge par dessus la bar grise, comme ça dès que la vie va baisser on verras la bar grise apparaitre au fur et à mesure.
        draw_text('Point De Vie', font, Rouge, self.x+140, self.y+25)



class BarDeStamina():
    def __init__(self,x,y,stamina,stamina_max):
        """
        méthode d'initialisation de la classe.
        Arguments: 
            self
            x: int de la position de la bar sur l'axe x
            y: int de la position du la bar sur l'axe y
            stamina: int du nombre de point de stamina actuelle du joueur.
            stamina_max: int du nombre de point stamina max du joueur.
        """
        self.x = x
        self.y = y
        self.stamina = stamina
        self.stamina_max = stamina_max

    def draw(self,stamina):
        """
        méthode qui permet de mettre à jour la bar de stamina
        Arguments:
            self
            stamina: int du nombre de point de stamina actuelle du joueur.
        """
        self.stamina = stamina
        ratio = self.stamina / self.stamina_max                             #le ratio représente la stamina divisé par la stamina maximal ce qui va permettre de réduire la taille de la bar de stamina au fur et a mesure que l'on en perd.
        pygame.draw.rect(fenetre, Gris, (self.x, self.y, 400, 20))          #on dessine une bar grise.
        pygame.draw.rect(fenetre, Vert, (self.x, self.y, 400*ratio, 20))   #on dessine une bar verte par dessus la bar grise, comme ça au fur et à mesure que la stamina va baisser on verras apparaitre la bar grise. 
        draw_text('stamina', font, Vert, self.x+140, self.y+25)




#création d'une classe projectile pour l'attaque:
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, flip, stamina):
        """
        méthode d'initialisation de la classe.
        Arguments: 
            self
            x: int de la position du projectile sur l'axe x
            y: int de la position du projectile sur l'axe y
            direction: int de la direction du joueur

        """        
        pygame.sprite.Sprite.__init__(self)
        self.stamina = stamina
        self.flip = flip                       
        self.speed = 10                        #variable de la vitesse du projectile.
        self.image = projectile_img            #image du projectile.
        if self.flip:                          #si le joueur est tourné vers la gauche le projectile change de sens.
            self.image = projectile_img1
        self.rect = self.image.get_rect()      #création d'un réctangle autour du projectile pour permettre d'appliquer les collisions/mouvement etc.
        self.rect.center = (x, y)              #position du rectangle.
        self.direction = direction             #direction du projectile.
        self.flip = False
        
    def update(self):
        """
        Méthode qui permet de controller le projectile (mouvement etc.)
        Arguments:
            self
        """
        #faire bouger le projectile:
        self.rect.x += (self.direction * self.speed)
        #vérifie si le projectile à quitter l'écran:
        if self.rect.right < 0 or self.rect.left > Largeur_fenetre:
            self.kill()

        #vérifie les collisions entre les personnages:
        if pygame.sprite.spritecollide(joueur, projectile_group, False):
            if joueur.vivant:
                joueur.PV -= 10
                self.kill()         #supprime le projectiles.
        
        for ennemi in ennemies_group:
            if pygame.sprite.spritecollide(ennemi, projectile_group, False):
                if ennemi.vivant:
                    ennemi.PV -= 25
                    self.kill()     #supprime le projectiles.



#création des groupes de sprites:
ennemies_group = pygame.sprite.Group()
projectile_group = pygame.sprite.Group()



#création du joueur et de ses bars de vie et stamina:
joueur = Personnage('personnages',200,400,1,5,10)
BarDeStamina = BarDeStamina(10,700, joueur.stamina, joueur.stamina)
BarDeVie = BarDeVie(540,700, joueur.PV, joueur.PV)

#création des ennemis:
ennemi = Personnage('ennemies',400,450,1,2,10)
ennemi2 = Personnage('ennemies',700,450,1,2,10)
ennemi3 = Personnage('ennemies',1000,450,1,2,10)
ennemies_group.add(ennemi)
ennemies_group.add(ennemi2)
ennemies_group.add(ennemi3)


run = True
while run: #Boucle contenant les différent événement de la fenêtre pendant qu'elle est en route.

    clock.tick(FPS)

    draw_Background()

    BarDeStamina.draw(joueur.stamina)
    BarDeVie.draw(joueur.PV)
    
    draw_text('Q=aller à gauche', font2, Blanc, 10, 0)
    draw_text('D=aller à droite', font2, Blanc, 10, 25)
    draw_text('Espace=sauter', font2, Blanc, 10, 50)
    draw_text('R=Attaquer', font2, Blanc, 10, 75)
    draw_text('Echap=Quitter', font2, Blanc, 10, 100)

    joueur.update()
    joueur.apparition()
    
    for ennemi in ennemies_group:
        ennemi.IA()
        ennemi.update()
        ennemi.apparition()

    #update et groupes de dessin:
    projectile_group.update()
    projectile_group.draw(fenetre)



    #met à jour les actions du joueur:
    if joueur.vivant:
        #pour frapper:
        if frapper:
            joueur.frapper()
        #pour sauter:
        elif joueur.in_air:
            joueur.update_action(2)         #2=sauter.
        #pour bouger:
        elif bouger_gauche or bouger_droite:
            joueur.update_action(1)         #1=courir.
        else:
            joueur.update_action(0)         #0=immobile.
        joueur.bouger(bouger_gauche,bouger_droite)


    for event in pygame.event.get():  #Boucle qui parcourt les différent evénement de la fenêtre.
        #Commande permettant de quitter la fenêtre:
        if event.type == pygame.QUIT:
            run = False
        #touches du claviers appuyé:
        if event.type == pygame.KEYDOWN:  
            if event.key == pygame.K_q:   #quand la touche a est appuyé.
                bouger_gauche = True
            if event.key == pygame.K_d:   #quand la touche d est appuyé.
                bouger_droite = True
            if event.key == pygame.K_r:   #quand la touche r est appuyé.
                frapper = True
            if event.key == pygame.K_SPACE and joueur.vivant:   #quand la touche espace est appuyé et si le joueur est vivant.
                joueur.saut = True
                son_saut.play()         
            if event.key == pygame.K_ESCAPE:    #quand échape est appuyé.
                run = False

        
        #touches n'est plus appuyé:
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_q:      #quand la touche a est relaché.
                bouger_gauche = False
            if event.key == pygame.K_d:      #quand la touche d est relaché.
                bouger_droite = False
            if event.key == pygame.K_r:      #quand la touche r est relaché.
                frapper = False


    pygame.display.update() #Afficher le joueur à l'écran.

pygame.quit() #Désactive l'initialisation des modules importé de pygame.
