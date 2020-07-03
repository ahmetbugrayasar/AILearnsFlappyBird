import pygame
import neat
import time
import os
import random
pygame.font.init() #Required to print out text on screen
WIN_WIDTH = 570 #Adjust to your own taste
WIN_HEIGHT = 800 #Adjust to your own taste
GEN = 0 #How many genomes have passed
STAT_FONT = pygame.font.SysFont("comicsans",50) #Please don't kinkshame me, i love comicsans


# These get the images from imgs folder
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bg.png")))

#Class of our birds
class Bird:
    IMGS = BIRD_IMGS #Calls the 3 images
    MAX_ROTATION = 25 #25 so it won't flip that much
    ROT_VEL = 20 #This is Rotation Velocity, so that the bird won't get dizzy.
    ANIMATION_TIME = 5 #Animation Time.

    #Initializer
    def __init__(self,x,y):
        self.x=x
        self.y=y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

        #Functions so the bird jumps
    def jump(self):
        self.vel = -10.5
        self.tick_count=0
        self.height = self.y

    #Functions so the bird goes forward
    def move(self):
        self.tick_count +=1
        #d is distance.
        d = self.vel * self.tick_count + 1.5*self.tick_count**2
        if d >= 16:
            d =16
        if d<0 :
            d -=2

        self.y = self.y + d


        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION

        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    #Draw function prints the bird and it's animations on screen.
    def draw(self, win):
        self.img_count +=1
        #It goes 1 -> 2 -> 3 -> 2 -> 1. Because that's what you do.
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <self.ANIMATION_TIME*2:
            self.img=self.IMGS[1]
        elif self.img_count <self.ANIMATION_TIME*3:
            self.img=self.IMGS[2]
        elif self.img_count <self.ANIMATION_TIME*4:
            self.img=self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4+1:
            self.img=self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft= (self.x,self.y)).center)
        win.blit(rotated_image,new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

#Class of our obstacles (not metaphorically)
class Pipe:
    GAP =200
    VEL = 5

    #Initializer
    def __init__(self,x):
        self.x= x
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP  = pygame.transform.flip(PIPE_IMG,False,True) # Top Obstacles are just Bottom obstacles in reverse.
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    #Sets a random height for each obstacle
    def set_height(self):
        self.height = random.randrange(40,450)
        self.top = self.height - self.PIPE_TOP.get_height() #So it won't collide
        self.bottom = self.height + self.GAP

    #So the obstacles go back. It's not just the birds that move.
    def move(self):
        self.x -= self.VEL

    #Draws the obstacles on screen.
    def draw(self,win):
        win.blit(self.PIPE_TOP,(self.x,self.top))
        win.blit(self.PIPE_BOTTOM,(self.x,self.bottom))


    #Detects collision with Birds
    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset =  (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask,bottom_offset) #Bottom point Boolean
        t_point = bird_mask.overlap(top_mask,top_offset) #Top Point Boolean

        if t_point or b_point:
            return True
        return False


#We will only have 2 bases at a time. Bases are the ground textures.
class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    #Initializer
    def __init__(self,y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
    #So the Ground moves.
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
    #It's like a treadmill. As soon as 1 Base unit's rear end touches the leftmost frame, it resets.
        if self.x1 + self.WIDTH <0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH <0:
            self.x2 = self.x1+ self.WIDTH

    #Prints the ground on screen
    def draw(self,win):
        win.blit(self.IMG, (self.x1,self.y))
        win.blit(self.IMG, (self.x2,self.y))

#This function puts everything on screen.
def draw_window(win,birds,pipes,base,score,gen):
    win.blit(BG_IMG,(0,0))

    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Score: "+ str(score),1,(255,255,255))
    win.blit(text,(WIN_WIDTH-10-text.get_width(),10))


    text = STAT_FONT.render("Gen: "+ str(gen),1,(255,255,255))
    win.blit(text,(10,10))

    base.draw(win)

    #Since there are multiple birds, we use a for loop
    for bird in birds:
        bird.draw(win)

    pygame.display.update()


def main(genomes,config):
    global GEN
    GEN +=1
    nets = []
    ge = []
    birds = []

    #Since genomes have 2 values in them
    #and i don't need the first 1
    #I just used a _.
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g,config)
        nets.append(net)
        birds.append(Bird(230,350))
        g.fitness = 0
        ge.append(g)

    base = Base(730)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
    clock = pygame.time.Clock()

    score = 0

    run =True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        pipe_ind = 0
        #If there still are birds flying,the game will go on until we say so.
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x >pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break
        #As the birds fly, they become more and more POWERFUL
        #For 'tis the life: You get busy flying; or you get busy dying.
        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness +=0.1

            #This gets the TANH of Heights differences of
            #1-) Each bird and Ground
            #2-) Each bird and the nearest tip of the obstacle ABOVE them
            #3-) Each bird and the nearest tip of the obstacle BELOW them
            output = nets[x].activate((bird.y,abs(bird.y-pipes[pipe_ind].height), abs(bird.y-pipes[pipe_ind].bottom)))
            #After birds calculate that it's better to jump than not to, they ASCEND
            if output[0] > 0.5:
                bird.jump()
        add_pipe=False
        rem = []

        #This checks each bird if they're a dumb dumb and they hit the obstacles.
        #If they pass the obstacles, it will add a new pipe for that is life :/.
        for pipe in pipes:
            for x,bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -=1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                if not pipe.passed and pipe.x<bird.x:
                    pipe.passed = True
                    add_pipe = True
            if pipe.x + pipe.PIPE_TOP.get_width()<0:
                rem.append(pipe)
            pipe.move()

        #Adds to the score everytime the winner bird passes an obstacle
        #Also adds a new obstacle everytime as well.
        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(700))
        for r in rem:
            pipes.remove(r)

        #If the birds enter illegal zones, they pop.
        #Also, if the birds become too fit, we have to stop them :(
        for x,bird in enumerate(birds):
            if bird.y +bird.img.get_height() > 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
        if score > 50:
            break
        base.move()
        draw_window(win,birds,pipes,base,score,GEN)


#Our birds are trying to get fit. They are flying in the name of fitness.
#More fitness points they have, better they fly; and vice versa.
#Run function sets the configuration file as default. Any changes you want to make, you can change them from there.
def run(config_path):
    config= neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,neat.DefaultSpeciesSet,neat.DefaultStagnation,config_path)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main,50)
if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
