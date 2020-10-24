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
uhlovodik = "3-methyl-4-(2-methylpropyl)oktan"

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

class HydroCarbon:
    def __init__(self, name):
        self.name = name
        self.bonds, self.residues, self.type = self.get_hydrocarbon()
        self.numberOfCarbons = hydrocarbons.index(self.type)+1
        self.o = self.old()
        self.makePlan()

    def get_hydrocarbon(self):
        hydrocarbonInput = self.name
        hydrocarbonList = []
        for i in hydrocarbonInput.split("-"):
            if len(i.split("yl")) >= 2:
                hydrocarbonList.extend(list(map(addYL, i.split("yl")[:-1])))
                hydrocarbonList.append(i.split("yl")[-1])
            else:
                hydrocarbonList.append(i)

        hydrocarbonList = removeBlank(hydrocarbonList)

        residues = []
        hydrocarbon = ""
        bonds = []
        for i, r in enumerate(hydrocarbonList):
            if r.endswith("yl"):
                a = 1
                while True:
                    try:
                        int(hydrocarbonList[i-a].split(",")[0])
                    except ValueError:
                        a += 1
                        continue
                    else:
                        for i_ in hydrocarbonList[i-a].split(","):
                            residues.append((r, int(i_)))
                        break

            elif r.endswith("an"):
                hydrocarbon = r[:-2]

            else:
                try:
                    int(r.split(",")[0])
                except ValueError:
                    if r in hydrocarbons:
                        hydrocarbon = r
                    elif r in nameOfBonds:
                        a = 1
                        while True:
                            try:
                                int(hydrocarbonList[i-a].split(",")[0])
                            except ValueError:
                                a += 1
                                continue
                            else:
                                for i_ in hydrocarbonList[i-a].split(","):
                                    bonds.append((r, int(i_)))
                                break
                else:
                    continue
        return bonds, residues, hydrocarbon

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


    def old(self):
        out = [hydrocarbons.index(self.type)]
        rs = []
        rD={}
        for r in self.residues:
            a = False
            for _ in rs:
                if r[0] in _.values():
                    rD = _
                    a = True
                    break
            if not a:
                rD =  {}

            rD["delka"] = hydrocarbons.index(r[0][:-2])+1
            rD["nazev"] = r[0]
            if not "pozice" in rD.keys():
                rD["pozice"] = []
            rD["pozice"].append(r[1])
            if not "smer" in rD.keys():
                    rD["smer"] = []
            rD["smer"].append(1 if a else -1)
            if not a:
                rs.append(rD)
        out.append(rs)

        rs = []
        for r in self.bonds:
            a = False
            for _ in rs:
                if r[0] in _.values():
                    rD = _
                    a= True
                    break
            if not a:
                rD =  {}

            rD["delka"] = nameOfBonds.index(r[0])+2
            rD["nazev"] = r[0]
            if not "pozice" in rD.keys():
                rD["pozice"] = []
            rD["pozice"].append(r[1])
            if not a:
                rs.append(rD)
        out.append(rs)
        return out

class Residue:
    def __init__(self, name):
        self.name = name[:-2]
        self.carbons = hydrocarbons.index(self.name)+1

    
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

def make_img(hydrocarbon):
    mainHydrocarbonLenght, residues, bonds = HydroCarbon(hydrocarbon).o

    pprint.pprint(HydroCarbon(hydrocarbon).o)

    #velikost
    maxResidueTop, maxResidueBottom = 0,0
    add_padding_x = [0,0]
    for i in residues:
        for p in range(len(i["pozice"])):
            #padding stuff
            if i["pozice"][p] == 1:
                add_padding_x[0] = 50
            if i["pozice"][p] == mainHydrocarbonLenght and i["smer"][p] == 1:
                add_padding_x[1] = 50
            if i["pozice"][p]%2 == 1 and i["delka"] > maxResidueTop:
                maxResidueTop = i["delka"]
            elif i["delka"] > maxResidueBottom:
                maxResidueBottom = i["delka"]

    z_size_start = 45 #délka první vazby
    z_normal_size = 35 #délka ostatních vazeb

    padding_x = 20
    padding_y = 20

    start_x, start_y = padding_x+add_padding_x[0], padding_y+maxResidueTop*z_normal_size+(z_size_start-z_normal_size)
    width = (mainHydrocarbonLenght-1)*50+padding_x*2+sum(add_padding_x)
    height = 2*padding_y + 50 + (maxResidueBottom+maxResidueTop)*z_normal_size+2*(z_size_start-z_normal_size)

    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    #hlavní řetězec
    
    for i in range(mainHydrocarbonLenght-1):
        if i%2==0:
            draw.line((start_x+i*50,start_y, start_x+i*50+50,start_y+50), fill=(0,0,0), width=5)
        else:
            draw.line((start_x+i*50,start_y+50, start_x+i*50+50,start_y), fill=(0,0,0), width=5)
    #vazby
    off = 5

    for i in bonds:
        for x in range(len(i["pozice"])):
            for d in range(i["delka"]):
                real_x = start_x+50*(i["pozice"][x]-1)
                off = 5*-d
                if i["pozice"][x]%2 == 1:
                    draw.line((real_x+off,start_y-off, real_x+off+50,start_y-off+50), fill=(0,0,0), width=2)
                else:
                    draw.line((real_x+off,start_y+off+50, real_x+off+50,start_y+off), fill=(0,0,0), width=2)

    #zbytky
    for i in residues:
        for x in range(len(i["pozice"])):
            for d in range(i["delka"]):

                direction = i["smer"][x]

                z_size = z_size_start if d == 0 else z_normal_size

                if d > 0:
                    real_x = start_x+50*(i["pozice"][x]-1)+z_size*direction+(z_size_start-z_normal_size)*direction
                else:
                    real_x = start_x+50*(i["pozice"][x]-1)

                if i["pozice"][x]%2 == 0:
                    if d>0: real_y = start_y+z_size*d+50+(z_size_start-z_normal_size)
                    else: real_y = start_y+z_size*d+50
                else:
                    if d>0: real_y = start_y-z_size*d-(z_size_start-z_normal_size)
                    else: real_y = start_y-z_size*d
                
                directionY = 1 if i["pozice"][x]%2 == 0 else -1
                
                if d%2 == 1 and d > 0:
                    direction*=-1
                elif d > 0:
                   real_x+=z_size*-direction

                if d == 0:
                    draw.line((real_x,real_y, real_x+z_size*direction,real_y+z_size*directionY), fill=(0,0,0), width=2)
                else:
                    draw.line((real_x,real_y, real_x+z_size*direction,real_y+z_size*directionY), fill=(0,0,0), width=2)
 


    img.save("temp.png", "png")
    with open("temp.png","rb") as f:
        return io.BytesIO(f.read())

#pprint.pprint(get_hydrocarbon(uhlovodik))

# make_img(uhlovodik)
h = HydroCarbon(uhlovodik)
h.draw()