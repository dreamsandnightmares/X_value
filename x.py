from data_load.data_load import data_load
from System.PV import PVSystem
import  matplotlib.pyplot as plt
from draw_plt.plot import draw_data_plt
import math
import numpy as np
from Docplex.solver import solver
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


def CRF(i=0.05, n=25):
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
        R+=r_x_gen[i]*price[i]/1000
    '*光伏额定功率/1000  MW 转换至 kW'


    return R
def Revenue_all(Revenue_gen:float,x:list,y:list,n,eff,price):
    '储能的收益'
    '收益对于不耦合的系统有两个效率'

    Revenue_storage = 0
    for i in range(n):

        # Revenue_storage+=((x[i])*price[i])
        #
        # Revenue_storage-= (y[i]/eff*price[i])

        Revenue_storage+=((x[i])*price[i])/1000

        Revenue_storage-= (y[i]/eff*price[i])/1000
    # print(Revenue_storage,'R_storage')
    # print(Revenue_gen,'gen')
    R_tot = (Revenue_gen+Revenue_storage)
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

    x,y = solver(x_gen,pd_price,E_max=E_max,eff=eff,h=h,n=n,x_gen_cap=x_gen_cap)
    Revenue_Gen = Revenue_gen(x_gen,pd_price)
    R_tot = Revenue_all(Revenue_Gen,x,y,n,eff,pd_price)
    crf = CRF()
    X = x_value(R_tot, crf, cost_all)
    return X









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
    time_range = 8000
    x_gen_cap = 1000
    pd_load, pd_price, pd_wea_wind, pd_wea_G_dir, pd_wea_G_diff, pd_wea_T, pd_wea_G_hor = clip(time_range)

    cost_all = cost(gen_cap=x_gen_cap,gen_power_cost =1448,gen_om=16.519,E_max=1,sto_duration=2,project_time=30,
                    sto_cap_cost=600,sto_power_cost=80,sto_om_cap=0.01,sto_om_power=0.01
                    )
    crf = CRF()
    gen =X_gen(pv_power_rate=x_gen_cap,time_load=time_range,pd_wea_T=pd_wea_T,pd_wea_G_dir=pd_wea_G_dir,
               pd_wea_G_diff=pd_wea_G_diff,pd_wea_G_hor=pd_wea_G_hor)
    E_max =10
    eff = 0.9
    h =2
    #
    x, y = solver(X_gen=gen, pd_price=pd_price, E_max=E_max, eff=eff, h=h, n=time_range, x_gen_cap=x_gen_cap)


    Revenue_Gen = Revenue_gen(r_x_gen=gen,price=pd_price)
    revenue_all = Revenue_all(Revenue_Gen,x,y,n=time_range,eff=eff,price=pd_price)
    print(revenue_all,'调峰后的收益')
    x_v = x_value(revenue_all,crf,cost_all)

    print('-----------')
    print(x_v,'X_value')
    print('-----------')



    print(sum(gen),'sum gen')
    print(Revenue_gen(gen,pd_price),'gen revenue')
    print(crf,'crf')
    print(cost_all,'cost all')
    print(crf*cost_all,'crf cost')
    print(x)
    plt.plot(list(range(len(x))),x)
    plt.plot(list(range(len(y))),y)
    plt.show()




