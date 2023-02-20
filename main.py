from data_load.data_load import data_load
from System.PV import PVSystem
import  matplotlib.pyplot as plt
from draw_plt.plot import draw_data_plt
import math
import numpy as np
from Docplex.solver import solver
import time




def X_gen(pv_power_rate,time_load):
    pv = PVSystem(P_PV_rated=pv_power_rate)
    x_gen =[]
    for i in range(time_load):
        x_gen.append(pv.PVpower(i)/pv_power_rate)
    return x_gen


def load_nor(load:list):
    load_list = []
    for i in range(len(load)):
        load_list.append(load[i]/max(load))
    return load_list

def Revenue_gen(r_x_gen:list,price):
    R = 0
    # print(len(r_x_gen))
    # print(len(price))
    for i in range(len(r_x_gen)):
        R+=r_x_gen[i]*price[i]
    R  =R*220/1000
    return R
def Revenue_all(Revenue_gen:float,x:list,y:list,n,eff,price):
    Revenue_storage = 0
    for i in range(n):

        Revenue_storage+=((x[i])*price[i])

        Revenue_storage-= (y[i]/eff*price[i])
    # print(Revenue_storage,'R_storage')
    # print(Revenue_gen,'gen')
    R_tot = (Revenue_gen+Revenue_storage)/25
    return R_tot

def clip(n:int):
    pd_load, pd_price, pd_wea_wind, pd_wea_G_dir, pd_wea_G_diff, pd_wea_T, pd_wea_G_hor =data_load()
    pd_load = pd_load[:n]
    pd_price=pd_price[:n]
    pd_wea_wind =pd_wea_wind[:n]
    pd_wea_G_dir =pd_wea_G_dir[:n]
    pd_wea_G_diff = pd_wea_G_diff[:n]
    pd_wea_T =pd_wea_T[:n]
    pd_wea_G_hor =pd_wea_G_hor[:n]
    return pd_load, pd_price, pd_wea_wind, pd_wea_G_dir, pd_wea_G_diff, pd_wea_T, pd_wea_G_hor

def CRF(i=0.05, n=20):
    crf = i * math.pow((1 + i), n) / (math.pow((1 + i), n) - 1)
    return crf
def x_value(R_tot,crf,C_gen,C_power,C_storage,E_max,h,):
    x  = R_tot/(crf*(C_gen+E_max*(C_power+h*C_storage)))
    # print(R_tot)
    # print((crf*(C_gen+E_max*(C_power+h*C_storage)),'cost'))
    return x
def max_R(time_range:int,n,E_max,h,eff,C_gen,C_power,C_storage):
    x_list =[]
    i = 0
    while i <= 7000:
        pd_load, pd_price, pd_wea_wind, pd_wea_G_dir, pd_wea_G_diff, pd_wea_T, pd_wea_G_hor = clip(time_range)
        x_gen = X_gen(pv_power_rate=220, time_load=time_range)
        x, y = solver(x_gen[i:n+i], pd_price[i:n+i], E_max=E_max, eff=eff, h=h,n=n)
        Revenue_Gen = Revenue_gen(x_gen[i:i+n], pd_price[i:n+i])
        R_tot = Revenue_all(Revenue_Gen, x, y, n, eff, pd_price[i:n+i])
        crf = CRF()
        X = x_value(R_tot, crf, C_gen=C_gen, C_power=C_power, C_storage=C_storage, E_max=E_max, h=h)
        i+=168
        x_list.append(X)
        # print(X)
        # print(i)

    return max(x_list)








if __name__ == '__main__':
    # time_range =490
    # pd_load, pd_price, pd_wea_wind, pd_wea_G_dir, pd_wea_G_diff, pd_wea_T, pd_wea_G_hor = clip(time_range)
    # x_gen  =X_gen(pv_power_rate=220,time_load=time_range)
    #
    # load_nor = load_nor(pd_load)
    # n = 490
    # eff = 0.9
    #
    #
    #
    # x,y=solver(x_gen[:490],pd_price,E_max=1,eff=0.9,h=1)
    # print(x,y)
    # draw_data_plt(False,x_gen,pd_price,load_nor,pd_load)
    #
    # Revenue_Gen =Revenue_gen(x_gen,pd_price)
    # R_tot= Revenue_all(Revenue_Gen,x,y,n,eff,pd_price)
    # print(R_tot,'R_tot')
    # crf = CRF()
    # X = x_value(R_tot,crf,C_gen=1000,C_power=50,C_storage=50,E_max=3,h=2)
    # x_max = max_R(time_range=8000,n=456,E_max=1,h=1,eff=0.9,C_gen=1000,C_power=100,C_storage=100)
    # print(x_max)



    C_power = [1190, 952, 590]
    C_storage = [93, 74 , 46]
    E_max_ra = np.arange(0.1, 4,0.5)
    print(E_max_ra)
    h_ra = np.arange(0.1, 4,0.25 )
    for power in C_power:
        for storage in C_storage:
            Z = []
            for i in range(len(E_max_ra)):
                Z_X = []
                print(E_max_ra[i],'E_max')
                for j in range(len(h_ra)):
                    print(h_ra[j],'h')
                    x_max = max_R(time_range=8000, n=456, E_max=i, h=j, eff=0.9, C_gen=1000, C_power=power, C_storage=storage)

                    Z_X.append(x_max)
                Z.append(Z_X)
            Z = np.array(Z)
            z = Z.tolist()

            ctf = plt.contourf(h_ra,E_max_ra,  z, 60, cmap='RdGy')


            plt.colorbar()  # 添加cbar
            plt.title('storage{}! power{}!'.format(storage,power))
            plt.xlabel(('storage time'))  # 去掉x标签
            plt.ylabel(('storage ratio'))  # 去掉y标签

            plt.savefig('25storage{}+power{}.svg'.format(storage,power),format='svg')
            plt.clf()
            print(Z)

























