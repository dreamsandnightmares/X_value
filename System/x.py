import scipy
from scipy import optimize
import numpy
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
n =500
x =[]
x_gen = X_gen(pv_power_rate=220, time_load=8760)
for i in  range(n):
    if i%2 ==0:
        x.append(1)
    else:
        x.append(float(-1/0.9))

bounds =[]
for i in range(n):
    if i%2 ==0:
        bounds.append([0,1])
    else:
        bounds.append([0,x_gen[int(i/2)]])

a = []
for i in  range(n):
    if i%2 ==0:
        a.append(-1)
    else:
        a.append(1)

b =[]
for i in  range(n):
    if i%2 ==0:
        b.append(1)
    else:
        b.append(-1)


c = numpy.array(x) #最值等式未知数系数矩阵

A_ub = numpy.array([a,b]) #<=不等式左侧未知数系数矩阵
B_ub = numpy.array([1,0]) #<=不等式右侧常数矩阵
#A_eq = numpy.array() 等式左侧未知数系数矩阵
#B_eq = numpy.array() 等式右侧常数矩阵
x = (None,1) #未知数取值范围
y = (None,None) #未知数取值范围
res = scipy.optimize.linprog(-c,A_ub,B_ub,bounds = bounds) #默认求解最小值，求解最大值使用-c并取结果相反数
# print(res)
v =0
for i in range(len(res.x)):
    if i%2 ==0:
        v -=res.x[i]
    else:
        v +=res.x[i]
print(v,'V')
d= 0



for i in range(len(res.x)):
    if i >=0:
        pass
    else:
        d+=i
    if i%2 ==0:
        if res.x[i]<=1:
            pass
        else:
            d+=i
    else:
        if res.x[i] <= x_gen[int(i/2)]:
            pass
        else:
            d+=i
print(d)


