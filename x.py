from data_load.data_load import data_load
from System.PV import PVSystem
import  matplotlib.pyplot as plt
from draw_plt.plot import draw_data_plt
import math
import numpy as np
from Docplex.solver import solver
import pandas as pd
import time
import  os


def cost(gen_cap,gen_power_cost,gen_om,sto_cap_cost,sto_power_cost,sto_om_cap,
         sto_om_power,E_max,sto_duration,project_time):
    gen_om_all = 0
    sto_om_cap_all =0
    sto_om_power_all =0
    gen_cost =gen_cap*gen_power_cost
    sto_power_cost_all =gen_cap*E_max*sto_power_cost
    sto_cap_cost_all =gen_cap*E_max*sto_duration*sto_cap_cost
    print(gen_cost,'gen_cost')

    for i  in range(project_time):
        gen_om_all +=gen_om*gen_cap
        sto_om_power_all =sto_om_power*sto_power_cost_all
        sto_om_cap_all = sto_cap_cost_all*sto_om_cap

    OM_all = gen_om_all+sto_om_cap_all+sto_om_power_all
    print(OM_all,'OPEX')
    print(gen_om_all,'gen_om_all')
    print(gen_om_all+gen_cost,'gen_all')
    print(sto_power_cost_all,'sto_power_cost')
    print(sto_cap_cost_all,'sto_cap_cost_all')

    cost_all = OM_all+gen_cost+sto_power_cost_all+sto_cap_cost_all


    return cost_all


def CRF(i=0.05, n=30):
    '计算年化投资成本'
    crf = i * math.pow((1 + i), n) / (math.pow((1 + i), n) - 1)
    return crf

def X_gen(pv_power_rate,time_load,pd_wea_T,pd_wea_G_dir,pd_wea_G_diff,pd_wea_G_hor):
    '光伏输出功率'
    pv = PVSystem(P_PV_rated=pv_power_rate,pd_wea_T=pd_wea_T,pd_wea_G_dir=pd_wea_G_dir,
                  pd_wea_G_hor=pd_wea_G_hor,pd_wea_G_diff=pd_wea_G_diff)
    x_gen =[]
    for i in range(time_load):
        x_gen.append(pv.PVpower(i))
    return x_gen

def clip(n:int):
    '截取一段数据'
    pd_load, pd_price, pd_wea_wind, pd_wea_G_dir, pd_wea_G_diff, pd_wea_T, pd_wea_G_hor =data_load()
    pd_load = pd_load[:n]
    pd_price=pd_price[:n]
    pd_wea_wind =pd_wea_wind[:n]
    pd_wea_G_dir =pd_wea_G_dir[:n]
    pd_wea_G_diff = pd_wea_G_diff[:n]
    pd_wea_T =pd_wea_T[:n]
    pd_wea_G_hor =pd_wea_G_hor[:n]
    return pd_load, pd_price, pd_wea_wind, pd_wea_G_dir, pd_wea_G_diff, pd_wea_T, pd_wea_G_hor



def Revenue_gen(r_x_gen:list,price):
    "光伏的收益"
    R = 0
    # print(len(r_x_gen))
    # print(len(price))
    for i in range(len(r_x_gen)):
        R+=(r_x_gen[i]*price[i])
    '*光伏额定功率/1000  MW 转换至 kW'


    return R
def Revenue_all(Revenue_gen:float,obj):
    '储能的收益'
    '收益对于不耦合的系统有两个效率'

    # Revenue_storage = 0
    # for i in range(n):
    #
    #     # Revenue_storage+=((x[i])*price[i])
    #     #
    #     # Revenue_storage-= (y[i]/eff*price[i])
    #
    #     Revenue_storage+=((x[i])*price[i])
    #
    #     Revenue_storage-= (y[i]/eff*price[i])
    #
    # print(Revenue_storage,'R_storage')
    # # print(Revenue_gen,'gen')
    R_tot = (Revenue_gen+obj)
    # return R_tot/2.2
    return  R_tot


def x_value(R_tot, crf,cost_all, ):
    '计算x值'
    x = R_tot / (cost_all*crf)
    # print(R_tot)
    # print((crf*(C_gen+E_max*(C_power+h*C_storage)),'cost'))
    return x


def max_R(n,E_max,h,eff,cost_all,x_gen,pd_price,x_gen_cap):

    '取maxR  感觉这里有问题'

    x,y = solver(x_gen,pd_price,E_max=E_max,eff=eff,h=h,n=n)
    Revenue_Gen = Revenue_gen(x_gen,pd_price)
    R_tot = Revenue_all(Revenue_Gen,x)
    crf = CRF()
    X = x_value(R_tot, crf, cost_all)
    return X

def data():
    path = r"/home/wch/Downloads/data/ERCOT/XIHE_Solar_Power_Data_1679302964.csv"
    '1MW 光伏输出功率 (MW)'

    x = pd.read_csv(path)
    x = x['输出功率(MW)'].tolist()

    path = r"/home/wch/Downloads/data/ERCOT/ERCOT.xlsx"
    y = pd.read_excel(path)
    y = y['Unnamed: 8'].tolist()

    for i in range(len(y)):
        if y[i] >= 1500:
                y[i] = 1500

    return x, y








    # while i <= 7000:
    #     pd_load, pd_price, pd_wea_wind, pd_wea_G_dir, pd_wea_G_diff, pd_wea_T, pd_wea_G_hor = clip(time_range)
    #     x_gen = X_gen(pv_power_rate=1000,time_load=time_range,pd_wea_T=pd_wea_T,pd_wea_G_dir=pd_wea_G_dir,
    #            pd_wea_G_diff=pd_wea_G_diff,pd_wea_G_hor=pd_wea_G_hor)
    #
    #     x, y = solver(x_gen[i:n+i], pd_price[i:n+i], E_max=E_max, eff=eff, h=h,n=n)
    #     Revenue_Gen = Revenue_gen(x_gen[i:i+n], pd_price[i:n+i])
    #     R_tot = Revenue_all(Revenue_Gen, x, y, n, eff, pd_price[i:n+i])
    #     crf = CRF()
    #     X = x_value(R_tot, crf,cost_all)
    #     i+=168
    #     x_list.append(X)








if __name__ == '__main__':
    time_range = 8760
    x_gen_cap = 1000
    pd_load, pd_price, pd_wea_wind, pd_wea_G_dir, pd_wea_G_diff, pd_wea_T, pd_wea_G_hor = clip(time_range)
    E_max = 1
    h =4
    cost_all = cost(gen_cap=x_gen_cap,gen_power_cost =1448,gen_om=16.519,E_max=E_max,sto_duration=h,project_time=30,
                    sto_cap_cost=100 ,sto_power_cost=80,sto_om_cap=0.01,sto_om_power=0.01
                    )
    crf = CRF()
    gen,price = data()
    # Revenue_Gen = Revenue_gen(r_x_gen=gen[:time_range],price=price[:time_range])
    # print(Revenue_Gen)
    #
    # x1 = x_value(R_tot=Revenue_gen(gen,price=price),cost_all=cost_all,crf=crf)
    # print(x1,'PV')
    # eff = 0.9
    #
    # x, y,s = solver(X_gen=gen[:time_range], pd_price=price[:time_range], E_max=E_max, eff=eff, h=h, n=time_range)
    # revenue_all = Revenue_all(Revenue_Gen,obj=s,)
    # print(revenue_all)
    # x_v = x_value(revenue_all,crf,cost_all)
    # print(x_v)
    eff = 0.9
    C_power = [150,100,50 ]
    C_sto = [150,100,50]
    E_max_ra = np.arange(0.001, 4, 0.5)
    h_ra = np.arange(0.001, 4, 0.25)
    for power in C_power:
        for storage in C_sto:
            Z = []
            z_list = []
            for i in range(len(E_max_ra)):
                Z_X = []
                print(E_max_ra[i], 'E_max')
                for j in range(len(h_ra)):
                    he_list =[]


                    cost_all = cost(gen_cap=x_gen_cap, gen_power_cost=1448, gen_om=16.519, E_max=i, sto_duration=j,
                                    project_time=30,
                                    sto_cap_cost=storage, sto_power_cost=power, sto_om_cap=0.01, sto_om_power=0.01
                                    )
                    print(h_ra[j],'h')
                    x, y, s = solver(X_gen=gen[:time_range], pd_price=price, E_max=E_max, eff=eff, h=h, n=time_range)
                    Revenue_Gen = Revenue_gen(r_x_gen=gen[:time_range], price=price[:time_range])
                    revenue_all = Revenue_all(Revenue_Gen, obj=s, )
                    x_v = x_value(revenue_all,crf,cost_all)
                    print(x_v,'X')
                    Z_X.append(x_v)
                    he_list.append(j)
                    he_list.append(i)
                    he_list.append(x_v)
                    z_list.append(he_list)
                Z.append(Z_X)
            Z = np.array(Z)
            z = Z.tolist()
            ctf = plt.contourf(h_ra, E_max_ra, z, 1000, cmap=plt.cm.coolwarm)


            plt.colorbar()  # 添加cbar
            cs = plt.contour(h_ra, E_max_ra, z, levels=[1], colors='k')  # 绘制一条等高线，颜色为黑色，等高线值为1
            plt.clabel(cs, inline=True, fontsize=1000)  # 在等高线上添加标签
            plt.title('storage{}! power{}!'.format(storage, power))
            plt.xlabel(('storage time'))  # 去掉x标签
            plt.ylabel(('storage ratio'))  # 去掉y标签

            plt.savefig('storage{}+power{}.svg'.format(storage, power), format='svg')
            plt.clf()
            print(Z)
            np.save('x_value{}+{}'.format(storage, power),z_list)








