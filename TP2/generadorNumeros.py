from random import uniform
from math import log, sqrt, sin, cos, pi

def random():
    return uniform(0,1)

def generar_uniforme(a, b):
    return round((random() * (b - a) + a), 4)

def generar_exponencial(lamda):
    return round(((log(1 - random())) / - lamda), 4)

def generar_normal_bm(media, desviacion):
    rnd1 = random()
    rnd2 = random()

    z1 = round((sqrt(-2 * log(rnd1)) * sin(2 * pi * rnd2) * desviacion + media), 4)
    z2 = round((sqrt(-2 * log(rnd1)) * cos(2 * pi * rnd2) * desviacion + media), 4)

    return z1, z2