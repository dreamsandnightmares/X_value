from data_load.data_load import data_load
from System.PV import PVSystem
import  matplotlib.pyplot as plt
from draw_plt.plot import draw_data_plt
import math
import numpy as np
from Docplex.solver import solver
import time
import  os
import pandas as pd

'更新  之前的jcpl数据有问题'



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
def readdata():
    path = r"/home/wch/Downloads/data/ERCOT/XIHE_Solar_Power_Data_1679302964.csv"
    x = pd.read_csv(path)
    x = x['输出功率(MW)'].tolist()

    path = r"/home/wch/Downloads/data/ERCOT/ERCOT.xlsx"
    y = pd.read_excel(path)
    y = y['Unnamed: 8'].tolist()
    path = r"/home/wch/Downloads/data/PJM/PJM.xlsx"
    for i  in range(len(y)):
        if y[i] >1500:
            y[i] =1500
        else:
            y[i] =y[i]
    Z = pd.read_excel(path)
    z = Z['JCPL'].tolist()


    return x,y,z








if __name__ == '__main__':
    a,b,c = readdata()
    print(sum(a)/8760)
    time_range =8000
    pd_load, pd_price, pd_wea_wind, pd_wea_G_dir, pd_wea_G_diff, pd_wea_T, pd_wea_G_hor = clip(time_range)

    x_gen_cap = 1000
    E_max = 1
    h =4
    crf = CRF()

    cost_all = cost(gen_cap=x_gen_cap, gen_power_cost=1000, gen_om=16.519, E_max=E_max, sto_duration=h, project_time=30,
                    sto_cap_cost=0, sto_power_cost=0, sto_om_cap=0.01, sto_om_power=0.01
                    )
    r_pv = []
    prcie_diff =[]
    for i in range(len(pd_price)):
        r_pv.append(a[i]*b[i])
        prcie_diff.append(pd_price[i] - c[i])



    print(b)
    print(max(b))
    print(max(c))


    print(sum(a)*1000,'光伏发电')
    print(sum(r_pv),'光伏收益')
    print(sum(r_pv)/(crf*cost_all),'x')







    # plt.show()




