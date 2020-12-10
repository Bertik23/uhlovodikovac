from uhlovodikovac import *

h = HydroCarbon("test")

with open("img.png","wb") as f:
    f.write(h.draw().read())