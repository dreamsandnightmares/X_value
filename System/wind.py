from data_load.data_load import data_load
import math
import matplotlib.pyplot as plt

def windpower(windspeed,power_rated):
    V_wind =[]
    h_WT =30
    h_ref =10
    a = 0.14
    V_wind_ci = 3
    V_wind_co =25
    V_wind_wr = 13
    wind_power = []



    for i in range(len(windspeed)):
        V_wind.append(windspeed[i]*math.pow(h_WT/h_ref,a))

    for i in range(len(V_wind)):
        if V_wind[i] <= V_wind_ci:
            wind_power.append(0)
        elif V_wind_ci<=V_wind[i] <= V_wind_wr:

            ref =( math.pow(V_wind[i],3) - math.pow(V_wind_ci,3))/( math.pow(V_wind_wr,3) - math.pow(V_wind_ci,3))
            wind_power.append(power_rated*ref)
        elif V_wind_wr<V_wind[i]<V_wind_co:
            wind_power.append(power_rated)
        else:
            wind_power.append(0)
    return wind_power

if __name__ == '__main__':
    pd_load, pd_price, pd_wea_wind, pd_wea_G_dir, pd_wea_G_diff, pd_wea_T, pd_wea_G_hor = data_load()
    print(pd_wea_wind)
    wind_power =windpower(pd_wea_wind,power_rated=200)
    dist = list(range(len(wind_power)))
    plt.plot(dist,wind_power)
    plt.xlabel("time")
    plt.ylabel('power')
    plt.title("wind power")
    plt.show()
