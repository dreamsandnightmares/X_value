import scipy
from scipy.optimize import minimize
import numpy as np
from System.PV import PVSystem
import data_load.data_load
def func(x):
    return x[0]*0.1+x[1]*0.1+x[2]*0.2+x[2]*0.2

def cons(args):
    a,b = args
    return ({'type':'ineq', 'fun':lambda x: x[0]-a},{'type':'ineq', 'fun':lambda x: b-x[0]},{'type':'ineq', 'fun':lambda x: x[2]-a},{'type':'ineq', 'fun':lambda x:b-x[2]},)

def cons1(args):
    a,b =args
    return ({'type':'ineq', 'fun':lambda x:x[1]-a},{'type':'ineq', 'fun':lambda x:b-x[1]},{'type':'ineq', 'fun':lambda x:x[3]-a},{'type':'ineq', 'fun':lambda x:b-x[3]},)
def cons2():
    return ({'type':'ineq', 'fun':lambda x:x[1]+x[3]-x[0]-x[2]},)

args =0,1
args1 =0,0.5
cons1 =cons1(args)+cons1(args1)+cons2()

