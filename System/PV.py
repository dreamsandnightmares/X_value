import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
from data_load.data_load import data_load
pd_load,pd_price,pd_wea_wind,pd_wea_G_dir,pd_wea_G_diff,pd_wea_T ,pd_wea_G_hor= data_load()



class PVSystem(object):

    def __init__(self,P_PV_rated):

        self.NocT = 44
        self.P_PV_rated = P_PV_rated

        pass

    def T_cell(self,t,G,):
        T_cell = pd_wea_T[t]+G[t]/0.8*(self.NocT-20)
        return T_cell

    # def G(self,t,G_hor,theta=50,F_cs=0.84,p_g=0.2,F_cg=0.84):
    #
    #     G = pv_data_dir[t]*math.cos(2*math.pi/360*theta)+pv_data_dif(t)*F_cs+G_hor[t]*p_g*F_cg
    #     return G
    def PVpower(self,time,f_PV = 0.86,G_STC = 1,gammaT = 0.003, T_cell_STC = 25):

        # print(math.cos(2 * math.pi / 360 * 50) )
        G = (float(pd_wea_G_dir[time])) *math.cos(2*math.pi/360*50)+(float(pd_wea_G_diff[time]))*0.84+(float(pd_wea_G_hor[time]))*0.2*0.84
        T_cell =pd_wea_T[time]+(float(G))/0.8*(44-20)/1000
        # print( T_cell,'T')
        P_PV = f_PV*self.P_PV_rated*(float(G))/G_STC*(1+gammaT*(T_cell-T_cell_STC))/1000

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
