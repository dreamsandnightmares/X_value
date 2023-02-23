from docplex.mp import model
import numpy as np
from System.PV import PVSystem
import data_load.data_load

def X_gen(pv_power_rate, time_load):
    pv = PVSystem(P_PV_rated=pv_power_rate)
    x_gen = []
    for i in range(time_load):
        x_gen.append(pv.PVpower(i) / pv_power_rate)
    return x_gen

def solver(X_gen,pd_price,E_max,eff,h,n):

    model1 =model.Model()

    x = model1.continuous_var_list([i for i in range(n)],name='x',lb=0 )
    y  =model1.continuous_var_list( [i for i in range(n)] , name='y',lb=0 )

    model1.maximize(model1.sum(pd_price[i]*x[i] - pd_price[i]*y[i]/eff for i in range(n)))

    model1.add_constraint(model1.sum(y)-model1.sum(x)<=h*E_max)
    model1.add_constraint(model1.sum(y)-model1.sum(x)>=0)


    for i in range(n):
        model1.add_constraint(x[i]<=E_max)
        model1.add_constraint(y[i]<=min(X_gen[i]*eff,eff*E_max))
        model1.add_constraint(model1.sum(y[:i]) - model1.sum(x[:i]) <= h * E_max)
        model1.add_constraint(model1.sum(x[:i]) <= model1.sum(y[:i]))

    solution = model1.solve()
    return solution.get_values(x),solution.get_values(y)


if __name__ == '__main__':
    pd_load, pd_price, pd_wea_wind, pd_wea_G_dir, pd_wea_G_diff, pd_wea_T, pd_wea_G_hor = data_load.data_load.data_load()
    X_gen = X_gen(pv_power_rate=220, time_load=8760)
    print(len(X_gen))
    print(len(pd_price))

    x_gen = X_gen[:507]
    price =pd_price[:507]


    x,y = solver(x_gen,price,E_max=1,eff=0.9,h=1,n=507)

    x_new = list(np.round(np.array(x),2))
    y_new = list(np.round(np.array(y),2))
    print(x_new)
    print(y_new)



