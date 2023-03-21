import time

import matplotlib.pyplot as plt
from docplex.mp import model
import numpy as np
from System.PV import PVSystem
import data_load.data_load
import pandas as pd

def X_gen(pv_power_rate,time_load,pd_wea_T,pd_wea_G_dir,pd_wea_G_diff,pd_wea_G_hor):
    '光伏输出功率'
    pv = PVSystem(P_PV_rated=pv_power_rate,pd_wea_T=pd_wea_T,pd_wea_G_dir=pd_wea_G_dir,
                  pd_wea_G_hor=pd_wea_G_hor,pd_wea_G_diff=pd_wea_G_diff)
    x_gen =[]
    for i in range(time_load):
        x_gen.append(pv.PVpower(i))
    return x_gen

def solver(X_gen,pd_price,E_max,eff,h,n,):
    'x 是放电'

    model1 =model.Model()
    model1.parameters.parallel.set(1)
    model1.parameters.threads.set(16)

    x = model1.continuous_var_list([i for i in range(n)],name='x',lb=0 )
    y  =model1.continuous_var_list( [i for i in range(n)] , name='y',lb=0 )


    for i in range(n):
        model1.add_constraint(x[i]<=E_max)
        model1.add_constraint(y[i]<=min(X_gen[i]*eff,eff*E_max))
        model1.add_constraint(model1.sum(y[:i]) - model1.sum(x[:i]) <= h * E_max)
        model1.add_constraint(model1.sum(x[:i]) <= model1.sum(y[:i]))


    model1.add_constraint(model1.sum(y)-model1.sum(x)<=h*E_max)
    model1.add_constraint(model1.sum(y)-model1.sum(x)>=0)
    # model1.add_constraint(model1.sum(y) ==model1.sum(gen)*eff)




    model1.maximize(model1.sum(pd_price[i]*x[i] - pd_price[i]*y[i]/eff for i in range(n)))



    solution = model1.solve()
    return solution.get_values(x),solution.get_values(y),solution.objective_value
    # return solution

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


    return x,y
if __name__ == '__main__':
    pd_load, pd_price, pd_wea_wind, pd_wea_G_dir, pd_wea_G_diff, pd_wea_T, pd_wea_G_hor = data_load.data_load.data_load()
    timeload= 507
    gen,price = readdata()
    gen  =gen[:timeload]
    price = price[:timeload]
    # print(gen)
    # print(price)

    print(gen[:timeload],'gen')
    print(sum(gen[:timeload]),'光伏总放电')
    x,y,s  =solver(gen,price,E_max=1,eff=0.9,h=4,n=timeload)
    print(sum(x),'储能系统总放电')
    print(sum(y),'储能系统总充电')
    print(s)
    aaa = 0
    for i in range(len(x)):
        aaa+=x[i]*price[i] - y[i]*price[i]/0.9
    print(aaa)

    plt.plot(list(range(len(x))),x,label ='dis')
    plt.plot(list(range(len(y))),y,label ='ch')

    plt.plot(list(range(len(gen))),gen,label ='gen')
    plt.legend()
    plt.show()
    plt.plot(list(range(len(pd_price[:72]))),price[:72],label ='price')
    plt.legend()
    plt.show()




