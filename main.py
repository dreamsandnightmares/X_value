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
    R_tot = (Revenue_gen+Revenue_storage)
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
    time_range =507
    pd_load, pd_price, pd_wea_wind, pd_wea_G_dir, pd_wea_G_diff, pd_wea_T, pd_wea_G_hor = clip(time_range)
    x_gen  =X_gen(pv_power_rate=220,time_load=time_range)

    load_nor = load_nor(pd_load)
    n = 507
    eff = 0.9



    x,y=solver(x_gen[:time_range],pd_price,E_max=1,eff=0.9,h=1,n=n)
    # print(x,y)
    draw_data_plt(False,x_gen,pd_price,load_nor,pd_load)

    Revenue_Gen =Revenue_gen(x_gen,pd_price)
    R_tot= Revenue_all(Revenue_Gen,x,y,n,eff,pd_price)
    # print(R_tot,'R_tot')
    crf = CRF()
    # X = x_value(R_tot,crf,C_gen=1000,C_power=50,C_storage=50,E_max=3,h=2)
    # x_max = max_R(time_range=8000,n=456,E_max=1,h=1,eff=0.9,C_gen=1000,C_power=100,C_storage=100)
    # print(x_max)
    # dist_x_gen  =list(range(len(x_gen)))
    #
    #
    # #
    # x_gen_new = []
    #
    # for i in range(len(x_gen)):
    #     x_gen_new.append(x_gen[i]+x[i]-y[i])
    #
    # dist_x_gen_new =list(range(len(x_gen_new)))
    # fig, (axs1, axs2,axs3) = plt.subplots(3, 1,sharex=True)
    # axs1.plot(dist_x_gen_new, x_gen_new)
    # axs1.set_xlabel('Time')
    # axs1.set_ylabel('X_gen_new ')
    # axs1.set_title('X_gen_new ')
    #
    # axs2.plot(dist_x_gen, x_gen)
    # axs2.set_xlabel('Time')
    # axs2.set_ylabel('X_gen ')
    # axs2.set_title('X_gen ')
    #
    # axs3.plot(dist_x_gen_new, pd_price)
    # axs3.set_xlabel('Time')
    # axs3.set_ylabel('price ')
    # axs3.set_title('price')
    # fig.subplots_adjust(wspace=0.5, hspace=0.5)
    # plt.savefig('X_gen switch.svg', format='svg')
    #
    # plt.show()








    C_power = [1190, 952, 590]
    C_storage = [93, 74 , 46]
    E_max_ra = np.arange(0.001, 4,0.5)
    print(E_max_ra)
    h_ra = np.arange(0.001, 4,0.25 )
    for power in C_power:
        for storage in C_storage:
            Z = []
            for i in range(len(E_max_ra)):
                Z_X = []
                print(E_max_ra[i],'E_max')
                for j in range(len(h_ra)):
                    print(h_ra[j],'h')
                    x_max = max_R(time_range=8000, n=507, E_max=i, h=j, eff=0.6, C_gen=6965, C_power=power, C_storage=storage)

                    Z_X.append(x_max)
                Z.append(Z_X)
            Z = np.array(Z)
            z = Z.tolist()

            ctf = plt.contourf(h_ra, E_max_ra, z,1000,cmap=plt.cm.coolwarm)


            plt.colorbar()  # 添加cbar
            cs = plt.contour(h_ra, E_max_ra, z, levels=[1], colors='k')  # 绘制一条等高线，颜色为黑色，等高线值为1
            plt.clabel(cs, inline=True, fontsize=1000)  # 在等高线上添加标签
            plt.title('storage{}! power{}!'.format(storage,power))
            plt.xlabel(('storage time'))  # 去掉x标签
            plt.ylabel(('storage ratio'))  # 去掉y标签

            plt.savefig('6965H2storage{}+power{}.svg'.format(storage,power),format='svg')
            plt.clf()
            print(Z)

    C_power = [870, 1390, 1743]
    C_storage = [1190, 952, 590]
    E_max_ra = np.arange(0.001, 4,0.5)
    print(E_max_ra)
    h_ra = np.arange(0.001, 4,0.25 )
    for power in C_power:
        for storage in C_storage:
            Z = []
            for i in range(len(E_max_ra)):
                Z_X = []
                print(E_max_ra[i],'E_max')
                for j in range(len(h_ra)):
                    print(h_ra[j],'h')
                    x_max = max_R(time_range=8000, n=504, E_max=i, h=j, eff=0.9, C_gen=6965, C_power=power, C_storage=storage)

                    Z_X.append(x_max)
                Z.append(Z_X)
            Z = np.array(Z)
            z = Z.tolist()

            ctf = plt.contourf(h_ra, E_max_ra, z,1000,cmap=plt.cm.coolwarm)


            plt.colorbar()  # 添加cbar
            cs = plt.contour(h_ra, E_max_ra, z, levels=[1], colors='k')  # 绘制一条等高线，颜色为黑色，等高线值为1
            plt.clabel(cs, inline=True, fontsize=1000)  # 在等高线上添加标签
            plt.title('storage{}! power{}!'.format(storage,power))
            plt.xlabel(('storage time'))  # 去掉x标签
            plt.ylabel(('storage ratio'))  # 去掉y标签

            plt.savefig('6965Listorage{}+power{}.svg'.format(storage,power),format='svg')
            plt.clf()
            print(Z)
























