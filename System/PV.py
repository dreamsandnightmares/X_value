import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
from data_load.data_load import data_load
pd_load,pd_price,pd_wea_wind,pd_wea_G_dir,pd_wea_G_diff,pd_wea_T ,pd_wea_G_hor= data_load()



class PVSystem(object):

    def __init__(self,P_PV_rated,pd_wea_T,pd_wea_G_dir,pd_wea_G_diff,pd_wea_G_hor):
        '温度信息'
        self.T = pd_wea_T
        self.pd_wea_G_dir = pd_wea_G_dir
        self.pd_wea_G_diff = pd_wea_G_diff
        self.pd_wea_G_hor =pd_wea_G_hor
        self.NocT =44
        self.P_PV_rated = P_PV_rated
        self.g_all = []

    def PVpower(self,time,f_pv = 0.9,G_stc = 1,gammaT = -0.002,T_cell_STC = 25):

        G = (float(self.pd_wea_G_dir[time])) * math.cos(2 * math.pi / 360 * 26.7) + (float(self.pd_wea_G_diff[time])) * 0.5 + (
            float(self.pd_wea_G_hor[time])) * 0.4 * 0.8

        T_cell = self.T[time] + (float(G)) / 0.8 * (45 - 20) / 1000

        P_PV = f_pv*self.P_PV_rated*(float(G))/G_stc*(1+gammaT*(T_cell-T_cell_STC))/1000


        self.g_all.append(G)
        return P_PV

if __name__ == '__main__':
    x = PVSystem(P_PV_rated=220)
    c= 0
    a = []

    for i in range(8640):
        a.append(x.PVpower(i))

        c+= x.PVpower(i)
    dist  =list(range(len(a)))
    plt.plot(dist,a,label ="PV_power" )
    plt.legend()
    plt.title("PV_power")
    plt.xlabel('Hour [h]')
    print(c)
    print(max(a))

    plt.show()
