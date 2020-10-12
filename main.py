import re 
import io
from PIL import Image, ImageDraw

hydrocarbons = ["meth","eth","prop","but","pent","hex","hept","okt","non","dek"]
numbers = ["mono","di","tri","tetra","penta","hexa","hepta","okta","nona","deka"]
nameOfBonds = ["en","yn"]

uhlovodik = "3,6-diethyl-2,4-dimethyl-4-propylokta-1,7-dien"


def get_uhlovodik(hydrocarbonInput):
    hydrocarbonInput = list(filter(None, re.split("[,-]+", hydrocarbonInput)))

    #osekání vstupu na hlavní část
    mainChain = 0
    mainChainC = 0 #počet uhlovodíků v hlavní části (1,2)
    for i in hydrocarbonInput:
        c = 0
        for u in hydrocarbons:
            if u in i: 
                c+=1
        if c >= mainChainC: 
            mainChainC = c
            mainChain = i
    #nalezení hlavního uhlovodíku
    mainHydrocarbon = ""
    if mainChainC > 1:
        highest_index = 0
        for index, h in enumerate(hydrocarbons):
            if index > highest_index:
                highest_index = index
        mainHydrocarbon = mainChain[highest_index:]
    else:
        mainHydrocarbon = mainChain
    #délka hlavního uhlovodíku
    mainHydrocarbonLenght = 0
    for i in hydrocarbons:
        if i in mainHydrocarbon:
            mainHydrocarbonLenght = hydrocarbons.index(i)+1
    #nalezení zbytků
    residues = []
    indexesOfResidues = []
    for i in range(hydrocarbonInput.index(mainChain)+1):
        if hydrocarbonInput[i].isdigit():
            indexesOfResidues.append(int(hydrocarbonInput[i]))
        else:
            name = hydrocarbonInput[i]
            for c in numbers:
                name = name.replace(c,"")
            if i == hydrocarbonInput.index(mainChain):
                name = name.replace(mainHydrocarbon,"")

            #print(f"{nazev}: {indexy_zbytku}")
            lenght = 0

            if name[-1] == "n": name = name[:-1] #nevim proč to tam dává 'n' a jsem línej to zjišťovat

            for u in hydrocarbons:
                if name[:-2] in u:
                    lenght = hydrocarbons.index(u)+1
            
            residues.append({"nazev":name,"delka": lenght,"pozice":indexesOfResidues, "smer": [-1 for i in range(len(indexesOfResidues))]})
            indexesOfResidues = []
    #nalezení vazeb
    indexOfBonds = []
    bonds = []
    for i in range(hydrocarbonInput.index(mainChain)+1,len(hydrocarbonInput)):
        if hydrocarbonInput[i].isdigit():
            indexOfBonds.append(int(hydrocarbonInput[i]))
        else:
            name = hydrocarbonInput[i]
            for c in numbers:
                name = name.replace(c,"")
            lenght = nameOfBonds.index(name)+2
            
            #print(f"{nazev} ({delka}): {index_vazeb}")
            bonds.append({"nazev":name,"delka": lenght,"pozice":indexOfBonds})
            indexOfBonds = []

    doubleResidues = []
    #nastavení směru vykreslení zbytku (když jsou 2)
    for i in residues:
        for j in i["pozice"]:
            c = 0
            to_change = {"index":0,"pos_index":0}
            for k in residues:
                for l in k["pozice"]:
                    if j == l:
                        c+=1
                        to_change = {"index":residues.index(k),"pos_index":k["pozice"].index(l)}
            if c > 1:
                residues[to_change["index"]]["smer"][to_change["pos_index"]] = 1

    #print(f"Hlavní řetězec: {hlavni_uhlovodik}, délka: {hlavni_uhlovodik_delka}")
    return [mainHydrocarbonLenght,residues,bonds]


def make_img(uhlovodik):
    hlavni_uhlovodik_delka,zbytky,vazby = get_uhlovodik(uhlovodik)

    #velikost
    max_zbytek_top, max_zbytek_bot = 0,0
    add_padding_x = [0,0]
    for i in zbytky:
        for p in range(len(i["pozice"])):
            #padding stuff
            if i["pozice"][p] == 1:
                add_padding_x[0] = 50
            if i["pozice"][p] == hlavni_uhlovodik_delka and i["smer"][p] == 1:
                add_padding_x[1] = 50

            if i["pozice"][p]%2 == 1 and i["delka"] > max_zbytek_top:
                max_zbytek_top = i["delka"]
            elif i["delka"] > max_zbytek_bot:
                max_zbytek_bot = i["delka"]

    z_size_start = 45 #délka první vazby
    z_normal_size = 35 #délka ostatních vazeb

    padding_x = 20
    padding_y = 20

    start_x, start_y = padding_x+add_padding_x[0], padding_y+max_zbytek_top*z_normal_size+(z_size_start-z_normal_size)
    width = (hlavni_uhlovodik_delka-1)*50+padding_x*2+sum(add_padding_x)
    height = 2*padding_y + 50 + (max_zbytek_bot+max_zbytek_top)*z_normal_size+2*(z_size_start-z_normal_size)

    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    #hlavní řetězec
    
    for i in range(hlavni_uhlovodik_delka-1):
        if i%2==0:
            draw.line((start_x+i*50,start_y, start_x+i*50+50,start_y+50), fill=(0,0,0), width=5)
        else:
            draw.line((start_x+i*50,start_y+50, start_x+i*50+50,start_y), fill=(0,0,0), width=5)
    #vazby
    off = 5

    for i in vazby:
        for x in range(len(i["pozice"])):
            for d in range(i["delka"]):
                real_x = start_x+50*(i["pozice"][x]-1)
                off = 5*-d
                if i["pozice"][x]%2 == 1:
                    draw.line((real_x+off,start_y-off, real_x+off+50,start_y-off+50), fill=(0,0,0), width=2)
                else:
                    draw.line((real_x+off,start_y+off+50, real_x+off+50,start_y+off), fill=(0,0,0), width=2)

    #zbytky
    for i in zbytky:
        for x in range(len(i["pozice"])):
            for d in range(i["delka"]):

                smer = i["smer"][x]

                z_size = z_size_start if d == 0 else z_normal_size

                if d > 0:
                    real_x = start_x+50*(i["pozice"][x]-1)+z_size*smer+(z_size_start-z_normal_size)*smer
                else:
                    real_x = start_x+50*(i["pozice"][x]-1)

                if i["pozice"][x]%2 == 0:
                    if d>0: real_y = start_y+z_size*d+50+(z_size_start-z_normal_size)
                    else: real_y = start_y+z_size*d+50
                else:
                    if d>0: real_y = start_y-z_size*d-(z_size_start-z_normal_size)
                    else: real_y = start_y-z_size*d
                
                y_smer = 1 if i["pozice"][x]%2 == 0 else -1
                
                if d%2 == 1 and d > 0:
                    smer*=-1
                elif d > 0:
                   real_x+=z_size*-smer

                if d == 0:
                    draw.line((real_x,real_y, real_x+z_size*smer,real_y+z_size*y_smer), fill=(0,0,0), width=2)
                else:
                    draw.line((real_x,real_y, real_x+z_size*smer,real_y+z_size*y_smer), fill=(0,0,0), width=2)
 


    img.save("temp.png", "png")
    with open("temp.png","rb") as f:
        return io.BytesIO(f.read())

make_img(uhlovodik)