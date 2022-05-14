"""
Subcontroller module for Alien Invaders

This module contains the subcontroller to manage a single level or wave in
the Alien Invaders game.  Instances of Wave represent a single wave. Whenever
you move to a new level, you are expected to make a new instance of the class.

The subcontroller Wave manages the ship, the aliens and any laser bolts on
screen. These are model objects.  Their classes are defined in models.py.

Most of your work on this assignment will be in either this module or
models.py. Whether a helper method belongs in this module or models.py is
often a complicated issue.  If you do not know, ask on Piazza and we will
answer.

# Sean Katauskas
# March 2022
"""
from game2d import *
from consts import *
from models import *
import math
import random

# PRIMARY RULE: Wave can only access attributes in models.py via getters/setters
# Wave is NOT allowed to access anything in app.py (Subcontrollers are not
# permitted to access anything in their parent. To see why, take CS 3152)


class Wave(object):
    """
    This class controls a single level or wave of Alien Invaders.

    This subcontroller has a reference to the ship, aliens, and any laser bolts
    on screen. It animates the laser bolts, removing any aliens as necessary.
    It also marches the aliens back and forth across the screen until they are
    all destroyed or they reach the defense line (at which point the player
    loses). When the wave is complete, you  should create a NEW instance of
    Wave (in Invaders) if you want to make a new wave of aliens.

    If you want to pause the game, tell this controller to draw, but do not
    update.  See subcontrollers.py from Lecture 24 for an example.  This
    class will be similar to than one in how it interacts with the main class
    Invaders.

    All of the attributes of this class ar to be hidden. You may find that
    you want to access an attribute in class Invaders. It is okay if you do,
    but you MAY NOT ACCESS THE ATTRIBUTES DIRECTLY. You must use a getter
    and/or setter for any attribute that you need to access in Invaders.
    Only add the getters and setters that you need for Invaders. You can keep
    everything else hidden.

    """
    # HIDDEN ATTRIBUTES:
    # Attribute _ship: the player ship to control
    # Invariant: _ship is a Ship object or None
    #
    # Attribute _aliens: the 2d list of aliens in the wave
    # Invariant: _aliens is a rectangular 2d list containing Alien objects or None
    #
    # Attribute _bolts: the laser bolts currently on screen
    # Invariant: _bolts is a list of Bolt objects, possibly empty
    #
    # Attribute _dline: the defensive line being protected
    # Invariant : _dline is a GPath object
    #
    # Attribute _lives: the number of lives left
    # Invariant: _lives is an int >= 0
    #
    # Attribute _time: the amount of time since the last Alien "step"
    # Invariant: _time is a float >= 0s
    #
    # You may change any attribute above, as long as you update the invariant
    # You may also add any new attributes as long as you document them.
    # LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY

    # Attribute _direction: the right direction of movement is 0 and left is 1
    # Invariant: _direction is a int 1 or 0

    # Attribute _fire_steps: number of steps until alien fires
    # Invariant: _fire_steps int between BOLT_RATE and 1 or None


    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)

    @property
    def ship(self):
        return self._ship

    @ship.setter
    def ship(self,a):
        assert(a==None or type(a)==Ship)
        self._ship=a

    @property
    def aliens(self):
        return self._aliens

    @aliens.setter
    def aliens(self,a):
        assert(type(self._aliens)==list or type(self._aliens)== None)
        if type(self._aliens)==list:
            for row in self._aliens:
                for col in row:
                    assert(col==None or type(col)==Alien)

        self._aliens=a

    @property
    def bolts(self):
        return self._bolts

    @bolts.setter
    def bolts(self,a):
        assert(type(self._bolts)==list)
        for bolt in self._bolts:
            assert(type(bolt)==Bolt)
        self._bolts = a

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self,a):
        assert(self._time>=0)
        self._time = a

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self,a):
        assert(self._direction==0 or self._direction==1)
        self._direction = a


    @property
    def lives(self):
        return self._lives

    @lives.setter
    def lives(self,a):
        assert(type(a)==int)
        self._lives = a

    @property
    def dead(self):
        return self._dead

    @property
    def line(self):
        return self._line
    # @property
    # def firesteps(self):
    #     return self._firesteps
    #
    # @firesteps.setter
    # def firesteps(self,a):
    #     print(self._firesteps)
    #     assert(type(self._firesteps)==int or type(self._firesteps)==None)
    #     self._firesteps = a



#################################################################
    #Initializer
    #Helper Methods for initializer
    def alienlist2d(self):
        tot_l = []
        y = GAME_HEIGHT - ALIEN_CEILING
        count = 0
        ALIEN_IMAGES=('alien1.png','alien2.png','alien3.png')

        for a in range(ALIEN_ROWS):
            l = []
            x = ALIEN_H_SEP + (ALIEN_WIDTH/2)
            for b in range(ALIENS_IN_ROW):
                l.append(Alien(x,y,source=ALIEN_IMAGES[math.floor(count)%3]))
                x+=ALIEN_H_SEP+ALIEN_WIDTH
            y-=(ALIEN_V_SEP+ALIEN_HEIGHT)
            tot_l.append(l)

            if (ALIEN_ROWS%2)!=0 and a==0:
                count+=1
            else:
                count+=0.5

        return tot_l

    # INITIALIZER (standard form) TO CREATE SHIP AND ALIENS
    def __init__(self):
        self._aliens = self.alienlist2d()
        self._ship = Ship(GAME_WIDTH/2)
        self._dline = GPath(points=[0,DEFENSE_LINE,GAME_WIDTH,DEFENSE_LINE],
                                                linewidth=2,linecolor="grey")
        self._time = 0
        self._direction = 0
        self._bolts = []
        self._firesteps = None
        self._animator = None
        self._lives= 3
        self._dead = False
        self._line = False



#################################################################
    #Animate Ship
    #Helper Methods for _animateShip
    def notshipmax(self):
        """
        return: boolean
        """
        if type(self.ship)==Ship:
            if self.ship.x < GAME_WIDTH-(SHIP_WIDTH/2):
                return True
            else:
                False

    def notshipmin(self):
        """
        return: boolean
        """
        if type(self.ship)==Ship:
            if self.ship.x > (SHIP_WIDTH/2):
                return True
            else:
                False

    def check_collision_ship(self):
        #check for ship if there is a collision, remove that alien from _aliens and change to None
        #implement range to get positions
        for bolt in range(len(self.bolts)):
            if type(self.ship)==Ship:
                if self.ship.collides(self.bolts[bolt]):
                    del self.bolts[bolt]
                    #REMOVES THE SHIP WITH ANIMATION
                    self._animator = self._ship_explosion()
                    next(self._animator)
                    break




    def _ship_explosion(self):
        """
        courtine animate slide
        DEATH_SPEED = 0.3
        self.count = 7
        """
        # print("MMMM")
        dt = (yield)
        # Number of iterations to complete
        steps = DEATH_SPEED/dt
        animating = True
        #Number of iteration before change
        amount = steps/7

        # print("XXX")
        while animating:
            # Get the current time
            dt = (yield)
            amount-=1
            if amount <=0:
                self.ship.frame += 1
                amount = steps/7

            # If we go to far, clamp and stop animating
            if self.ship.frame >= 7:
                self.bolts= []
                self.ship = None
                # self._animator = None
                animating = False




    def _shipmovement(self,input):
        if input.is_key_down('right') and self.notshipmax():
            if type(self.ship)==Ship:
                self.ship.x += SHIP_MOVEMENT
        if input.is_key_down('left') and self.notshipmin():
            if type(self.ship)==Ship:
                self.ship.x -= SHIP_MOVEMENT

    def _playerfire(self,input):
        #player firing bolt
        if input.is_key_down('spacebar') and self.playerBolt():
            if type(self.ship)==Ship:
                self.bolts.append(Bolt(x=self.ship.x,
                            y=self.ship.y+(SHIP_HEIGHT/2),velocity=BOLT_SPEED))

    #Animate Ship
    def _animateShip(self,input,dt):
        #check if coroutine is active
        if self._animator == None:
            #check if there is a collision and change ship to none if so
            self.check_collision_ship()
            #player firing bolt
            self._playerfire(input)
            #move ship left or right with boundardy
            self._shipmovement(input)
        else:
            try:
                self._animator.send(dt)         # Tell it how far to animate
            except:
                self._animator = None

#################################################################
    #Animate Alien
    #Helper Method for _animateAliens


    #make columns of only aliens and then from there check if an item
    #in each of the columns hits the right or left and then process movement for all aliens

    def shift_left(self):
        """
        shift to left
        make list of columns alien to then measure from
        """
        cols = self.make_column()

        #first alien in most right column
        c = cols[len(cols)-1][0]
        if c.x > (GAME_WIDTH-ALIEN_H_SEP-(ALIEN_WIDTH/2)):
            self.direction = 1
            for rows in self.aliens:
                for alien in rows:
                    #UPDATE1
                    if type(alien)==Alien:
                        alien.y -= ALIEN_V_WALK
                        alien.x -= ALIEN_H_WALK


    def shift_right(self):
        """
        shift to right
        make list of columns alien to then measure from
        """
        cols = self.make_column()

        #first alien in most left column

        c = cols[0][0]
        if c.x < ALIEN_H_SEP+(ALIEN_WIDTH/2):
            self.direction = 0
            for rows in self.aliens:
                for alien in rows:
                    if type(alien)==Alien:
                        alien.y -= ALIEN_V_WALK
                        alien.x += ALIEN_H_WALK

    def alien_step(self):
        """
        step depending on alien speed
        """
        if self.time > ALIEN_SPEED:
            self.time = 0
            for rows in self.aliens:
                for alien in rows:
                    #UPDATE1
                    if type(alien)==Alien:
                        if self.direction ==0:
                            alien.x += ALIEN_H_WALK
                        elif self.direction ==1:
                            alien.x -= ALIEN_H_WALK
            if self._firesteps >= 1:
                self._firesteps-=1

    def check_collision(self):
        #check for every alien if there is a collision, remove that alien from _aliens and change to None
        #implement range to get positions
        for row in range(len(self.aliens)):
            for alien in range(len(self.aliens[row])):
                for bolt in range(len(self.bolts)):
                    if type(self.aliens[row][alien])==Alien:
                        if self.aliens[row][alien].collides(self.bolts[bolt]):
                            self.aliens[row][alien]=None
                            del self.bolts[bolt]


    #Animate Aliens
    def _animateAliens(self,dt):
        self.time += dt

        self.check_collision()
        self.alien_step()
        if not self._deadAliens():
            if self.direction==0:
                self.shift_left()
            elif self.direction==1:
                self.shift_right()

            #alien bolt firing
            self.alien_fire()



#################################################################
    #Animate Bolts
    #Helper Method for _animateBolts
    def playerBolt(self):
        #check _bolts if there is player bolt
        for b in self.bolts:
            if b.isPlayerBolt() == True:
                return False
        return True

    def remove_bolt(self):
        #removing off the screen
        i = 0
        while i < len(self.bolts):
            if self.bolts[i].y > GAME_HEIGHT-(BOLT_HEIGHT/2) and self.bolts[i].isPlayerBolt():
                del self.bolts[i]
            elif not self.bolts[i].isPlayerBolt() and self.bolts[i].y < 0-(BOLT_HEIGHT/2):
                del self.bolts[i]
            else:
                i += 1
        # print(self._bolts)

    def alien_fire(self):
        #alien bolt firing
        if self._firesteps == None:
            self._firesteps = random.randrange(2,BOLT_RATE+1)
            # print("********")
            # print(self._firesteps)
            # print("xxxxxxx")

        if self._firesteps == 0:
            t = self.choose_rand_alien()
            self.bolts.append(Bolt(t.x,t.y-(ALIEN_HEIGHT/2)-(BOLT_HEIGHT/2),
                                            velocity=(-BOLT_SPEED)))
            self._firesteps = None



    def make_column(self):
        """
        make list of columns alien
        """
        tl= []

        for a in range(len(self.aliens[0])):
            l = []
            for row in range(len(self.aliens)):
                if self.aliens[0][a]!=None:
                    #UPDATE1
                    if type(self.aliens[row][a])==Alien:
                        l.append(self.aliens[row][a])
            if l != []:
                tl.append(l)

        return tl


    def choose_rand_alien(self):
        """
        return bottom alien at random columun
        return: alien object
        """
        #choose an alien from alien columns randomly
        r = random.choice(self.make_column())

        #choose last alien in list
        return r[len(r)-1]

    def moving_bolt(self):
        for bolt in self.bolts:
            if bolt.velocity == BOLT_SPEED:
                bolt.y += BOLT_SPEED
            else:
                bolt.y += -BOLT_SPEED


    #Animate Bolts
    def _animateBolts(self,input):
        #removing off the screen
        self.remove_bolt()
        #moving bolt
        self.moving_bolt()

#################################################################
    #Update

    #Helper Methods

    def _deadAliens(self):
        """
        return True if all dead aliens
        return bool
        """
        for row in self.aliens:
            for alien in row:
                if type(alien)==Alien:
                    return False
        return True

    def _belowline(self):
        """
        return True if the lowest alien is under boundary line
        """
        x = self.make_column()
        mn = x[0][len(x[0])-1]
        for col in range(len(x)):
            for alien in range(len(x[col])):
                if x[col][alien].y<mn.y:
                    mn = x[col][alien]

        if mn.y < DEFENSE_LINE+(ALIEN_HEIGHT/2):
            return True


    def update(self,input,dt):
        #putting animation in method slows it down

        #skip if all aliens are dead or any alien crossed over the line
        #implement cross over line with col and then last item in longest column
        if self._deadAliens():
            self._dead=True

        if not self._deadAliens():
            if self._belowline():
                self._line=True
            #closest alien y value is less than boundary is true
            #check longest column and change self to dead
        self._animateShip(input,dt)
        self._animateAliens(dt)
        self._animateBolts(input)

#################################################################
    #Draw
    # DRAW METHOD TO DRAW THE SHIP, ALIENS, DEFENSIVE LINE AND BOLTS
    # Attribute view : the view (inherited from GameApp)
    # Invariant: view is an instance of GView
    def draw(self,view):
        for rows in self.aliens:
            for alien in rows:
                if type(alien)==Alien:
                    alien.draw(view)
        if type(self.ship)==Ship:
            self.ship.draw(view)
        self._dline.draw(view)
        for bolt in self.bolts:
            bolt.draw(view)

    # HELPER METHODS FOR COLLISION DETECTION
