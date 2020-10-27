import re 
import io
from PIL import Image, ImageDraw
import pprint
import math
import json


"""
[0,
 [{'delka': 2, 'nazev': 'ethyl', 'pozice': [3, 6], 'smer': [-1, -1]},
  {'delka': 1, 'nazev': 'methyl', 'pozice': [2, 4], 'smer': [-1, -1]},
  {'delka': 3, 'nazev': 'propyl', 'pozice': [4], 'smer': [1]}],
 [{'delka': 2, 'nazev': 'en', 'pozice': [1, 7]}]]
"""

hydrocarbons = json.load(open("hydrocarbons.jsonc"))
numbers = ["mono","di","tri","tetra","penta","hexa","hepta","okta","nona","deka"]
nameOfBonds = ["en","yn"]

uhlovodik = "3,4-ethylnon-1,7-en"
# uhlovodik = "2,3-methylbut-2-en"
uhlovodik = "3-methyl-4-(2-methyl-3-(2-propyl)propyl)oktan"

class GetOutOfLoop(Exception):
    pass

def addYL(s):
    return s + "yl"

def removeBlank(l):
    lOut = []
    for i in l:
        if i != "":
            lOut.append(i)
    return lOut

def oddEven(num):
    if num%2 == 0:
        return 1
    else:
        return -1

def positiveOrNagative(num):
    if num > 0:
        return 1
    elif num < 0:
        return -1
    else:
        return 0

def rstripIfEndingWith(s, chars):
    if s.endswith(chars):
        return s.rstrip(chars)
    else:
        return s

def lstripIfEndingWith(s, chars):
    if s.startswith(chars):
        return s.lstrip(chars)
    else:
        return s

def ifString(s):
    if type(s) == str:
        return s
    else:
        return ""

class HydroCarbon:
    def __init__(self, name):
        self.name = name
        self.get_hydrocarbon()
        self.numberOfCarbons = hydrocarbons.index(self.type)+1
        # self.makePlan()

    def get_hydrocarbon(self):
        hydrocarbonInput = self.name
        self.carbons = {}
        while True:
            try:
                for hc in hydrocarbons:
                    if hydrocarbonInput.endswith(hc):
                        self.type = hc
                        raise GetOutOfLoop
            except GetOutOfLoop:
                break
            hydrocarbonInput = hydrocarbonInput[:-1]
        hydrocarbonInput = rstripIfEndingWith(self.name[:self.name.rfind(self.type)] + self.name[self.name.rfind(self.type)+len(self.type):],"an")
        # print(hydrocarbonInput)
        hydrocarbonList = hydrocarbonInput.split("-")
        print(hydrocarbonList)
        while "(" in "".join(map(ifString,hydrocarbonList)):
            for i, p in enumerate(hydrocarbonList):
                #print(i,p)
                try:
                    if p.startswith("("):
                        for i_, p_ in enumerate(reversed(hydrocarbonList[i+1:])):
                            if p_.endswith(")"):
                                fromTo = i,i+1+len(hydrocarbonList[i+1:])-i_
                                hydrocarbonList.insert(i,Residue("-".join(hydrocarbonList[fromTo[0]:fromTo[1]]).lstrip("(").rstrip(")")))
                                for i__, p__ in enumerate(hydrocarbonList[fromTo[0]+1:fromTo[1]+1]):
                                    hydrocarbonList.pop(fromTo[0]+1)
                except Exception as e:
                    print(e)

        print(hydrocarbonList)

        for carbon in range(1,hydrocarbons.index(self.type)+2):
            if carbon not in self.carbons.keys():
                self.carbons[carbon] = []
            for i, p_ in enumerate(hydrocarbonList):
                try:
                    for p in p_.split(","):
                        try:
                            if int(p) == carbon:
                                if type(hydrocarbonList[i+1]) != Residue:
                                    self.carbons[carbon].append(Residue(hydrocarbonList[i+1]))
                                else:
                                    self.carbons[carbon].append(hydrocarbonList[i+1])
                        except ValueError:
                            pass
                except AttributeError:
                    pass
        print(self.carbons)


    def makePlan(self):
        self.carbons = {}
        for c in range(1,self.numberOfCarbons+1):
            if c not in self.carbons.keys():
                self.carbons[c] = []
            for r in self.residues:
                if r[1] == c:
                    self.carbons[c].append(Residue(r[0]))

            for b in self.bonds:
                if b[1] == c:
                    self.carbons[c].append(b[0])

        print(self.carbons)

    def draw(self):
        direction = (0,1)
        length = 50
        thickness = 3
        bondOfset = 10
        mainChainPlusThicc = 0
        img = Image.new("RGB", (1000, 1000), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        x,y = 50,500
        oldX, oldY = x,y
        nextDrawBond = False
        nextDrawBondTimes = 0
        for c in self.carbons.keys():
            draw.point((x,y), fill=(0,0,0))
            draw.line((oldX, oldY, x, y),fill=(0,0,0), width=thickness+mainChainPlusThicc)

            if nextDrawBond:
                for i in range(1,nextDrawBondTimes+1):
                    draw.line((oldX+oddEven(c)*(oddEven(i)*math.ceil(i/2)*bondOfset), oldY+(oddEven(i)*math.ceil(i/2)*bondOfset), x+oddEven(c)*(oddEven(i)*math.ceil(i/2)*bondOfset), y+(oddEven(i)*math.ceil(i/2)*bondOfset)),fill=(0,0,0), width=thickness+mainChainPlusThicc)
                nextDrawBond = False

            for r in self.carbons[c]:
                if r in nameOfBonds:
                    nextDrawBond = True
                    nextDrawBondTimes = nameOfBonds.index(r)+1

                try:
                    if r.name in hydrocarbons:
                        print(c, r, x,y)
                        r.draw(draw, x,y, oldX, oldY, length, thickness, direction)
                except AttributeError:
                    pass

            oldX, oldY = x,y
            x += length
            y += oddEven(c)*length

        img.save("temp.png", "png")
        with open("temp.png","rb") as f:
            return io.BytesIO(f.read())


class Residue:
    def __init__(self, name):
        self.name = name[:-2]
        try:
            self.carbons = hydrocarbons.index(self.name)+1
        except:
            pass

    
    def draw(self, draw, inX,inY, inOldX, inOldY, length, width, direction):
        if direction[0] == 0:
            direction = (positiveOrNagative(inY - inOldY),0)
        else:
            direction = (0,positiveOrNagative(inX - inOldX))
        x,y = inX, inY
        oldX, oldY = x,y
        for c in range(self.carbons+1):
            draw.line((x,y, oldX, oldY), fill=(0,0,0), width=width)
            oldX, oldY = x,y
            if direction[0] == 0:
                x += length*direction[1]
                y += oddEven(c)*length
            else:
                y += length*direction[0]
                x += oddEven(c)*length

    def __str__(self):
        return f"Residue {self.name}"
    def __repr__(self):
        return self.__str__()

h = HydroCarbon(uhlovodik)
h.draw()