import time

import matplotlib.pyplot as plt
from docplex.mp import model
import numpy as np
from System.PV import PVSystem
import data_load.data_load

def X_gen(pv_power_rate,time_load,pd_wea_T,pd_wea_G_dir,pd_wea_G_diff,pd_wea_G_hor):
    '光伏输出功率'
    pv = PVSystem(P_PV_rated=pv_power_rate,pd_wea_T=pd_wea_T,pd_wea_G_dir=pd_wea_G_dir,
                  pd_wea_G_hor=pd_wea_G_hor,pd_wea_G_diff=pd_wea_G_diff)
    x_gen =[]
    for i in range(time_load):
        x_gen.append(pv.PVpower(i))
    return x_gen

def solver(X_gen,pd_price,E_max,eff,h,n,x_gen_cap):
    'x 是放电'

    model1 =model.Model()
    model1.parameters.parallel.set(1)
    model1.parameters.threads.set(16)

    x = model1.continuous_var_list([i for i in range(n)],name='x',lb=0 )
    y  =model1.continuous_var_list( [i for i in range(n)] , name='y',lb=0 )


    for i in range(n):
        model1.add_constraint(x[i]<=E_max*x_gen_cap)
        model1.add_constraint(y[i]<=min(X_gen[i]*eff,eff*E_max*x_gen_cap))
        model1.add_constraint(model1.sum(y[:i]) - model1.sum(x[:i]) <= h * E_max*x_gen_cap)
        model1.add_constraint(model1.sum(x[:i]) <= model1.sum(y[:i]))


    model1.add_constraint(model1.sum(y)-model1.sum(x)<=h*E_max*x_gen_cap)
    model1.add_constraint(model1.sum(y)-model1.sum(x)>=0)
    model1.add_constraint(model1.sum(y) ==model1.sum(X_gen)*eff)


    model1.maximize(model1.sum(pd_price[i]*x[i] - pd_price[i]*y[i]/eff for i in range(n)))






    solution = model1.solve()
    return solution.get_values(x),solution.get_values(y)
    # return solution


if __name__ == '__main__':
    time_start  = time.time()
    pd_load, pd_price, pd_wea_wind, pd_wea_G_dir, pd_wea_G_diff, pd_wea_T, pd_wea_G_hor = data_load.data_load.data_load()
    time_range =507
    X_gen =X_gen(pv_power_rate=1000,time_load=time_range,pd_wea_T=pd_wea_T,pd_wea_G_dir=pd_wea_G_dir,
               pd_wea_G_diff=pd_wea_G_diff,pd_wea_G_hor=pd_wea_G_hor)

    x_gen = X_gen[:time_range]

    price =pd_price[:time_range]


    x,y = solver(x_gen,price,E_max=5,eff=0.9,h=1,n=time_range,x_gen_cap=1000)

    print(x)
    print(y)
    time_end = time.time()
    print(time_end-time_start)
    #
    # x_new = list(np.round(np.array(x),2))
    # # y_new = list(np.round(np.array(y),2))
    # print(x_new)
    # print(y_new)
    r_dis = []
    r_ch  =[]
    r_gen = []
    energy = []
    for i in range(len(x)):
        r_dis.append(x[i]*price[i]/1000)
        r_ch.append(y[i]*price[i]/1000)
        r_gen.append(x_gen[i]*price[i]/1000)
        energy.append(sum(y[:i])-sum(x[:i]))

    plt.plot(list(range(len(energy))),energy,label ='energy')





    print(sum(r_dis),'放电收益')
    print(sum(r_gen),'光伏收益')
    print(sum(r_ch),'充电价格')
    plt.plot(list(range(len(x))),x,label ='X')
    print(sum(y),'总充电量')
    print(sum(x),'总放电量')
    plt.plot(list(range(len(y))),y)
    print(y)
    plt.legend()
    plt.show()

    plt.plot(list(range(len(price))),price)
    plt.show()
    print(max(price))




