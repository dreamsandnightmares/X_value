import scipy
from scipy.optimize import minimize
import numpy as np
from System.PV import PVSystem
import data_load.data_load

def X_gen(pv_power_rate, time_load):
    pv = PVSystem(P_PV_rated=pv_power_rate)
    x_gen = []
    for i in range(time_load):
        x_gen.append(pv.PVpower(i) / pv_power_rate)
    return x_gen


def bounds(number:list,x_gen,eff,E_max):
    bounds = []
    for i in range(len(number)):
        if i%2==0:
            bounds.append([0, E_max])
        else:
            bounds.append([0, min(eff * x_gen[int(i / 2)], eff * E_max)])
    return bounds

def bounds_storage(number:list,h,E_max):
    bounds_up =[]
    bounds_down = []
    for i in range(len(number)):
        if i %2==0:
            bounds_up.append(-1)
            bounds_down.append(1)
        else:
            bounds_up.append(1)
            bounds_down.append(-1)
    return [bounds_up]+[bounds_down]




def func(number:list,eff,price):
    para = []
    for i in  range(len(number)):
        if i%2 !=0:
            para.append(-1/eff*price[int(i/2)])
        else:
            para.append(1*price[i])
    return para
def check_st(res:list,E_max,x_gen,eff,h):
    storage = 0
    for i in range(len(res)):
        if i%2==0:
            storage-=res[i]
            if  0<= res[i] <= E_max:
                pass
            else:
                print('X_dis error',i)
                print(res[i] ,E_max)
                print('-----------')
        else:
            storage += res[i]
            if  0<= res[i] <=min(eff*x_gen[int(i/2)],eff*E_max):
                pass
            else:
                print('X_ch error',i)
                print(res[i],min(eff*x_gen[int(i/2)],eff*E_max))
                print('-----------')

    if 0<= storage <=h*E_max:
        pass
    else:
        print('storage error',storage)



def X_value(func_para,bounds_au,bounds_bu,bounds):
    res = scipy.optimize.linprog(-func_para, bounds_au, bounds_bu, bounds=bounds)
    return res

def number_list(n:int):
    number =[]
    number_dis = []
    number_ch = []
    for i in  range(n):
        number.append(i)
        if i%2 ==0:
            number_dis.append(i)
        else:
            number_ch.append(i)


    return number,number_dis,number_ch
def zeros(number: list):
    x = []
    for i in range(len(number)):
        x.append(0)
    return x
if __name__ == '__main__':
    # n =4
    # pd_load, pd_price, pd_wea_wind, pd_wea_G_dir, pd_wea_G_diff, pd_wea_T, pd_wea_G_hor =data_load.data_load.data_load()
    # number, number_dis, number_ch = number_list(n)
    #
    # x0 = zeros(number)
    # pice = [0.1,0.3,0.2,0.4]
    # x_gen = [0.1,0.2,0.3,0.4]
    #
    # func_para =np.array(func(number=number,eff=0.9,price=pice))
    #
    # bounds_au =np.array(bounds_storage(number=number,h=1,E_max=1))
    # bounds_bu = np.array([1,0])
    # bounds =bounds(number,x_gen,eff=0.9,E_max=1)
    # res = scipy.optimize.linprog(-func_para,bounds_au,bounds_bu,bounds=bounds)
    # print(res)
    # check_st(res.x,E_max=1,x_gen=x_gen,eff=0.9,h=1)
    e = [0.1,0.2,0.3]
    h = [0.1,0.2,0.3]
    z = [1,2,3]
    a = []
    c = []
    for i in range(len((e))):
        a = []
        a.append(e[i])
        a.append(h[i])
        a.append(z[i])
        c.append(a)
    print(c)
    a = np.load('c.txt.npy')
    print(a )


















