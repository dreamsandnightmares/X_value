import matplotlib.pyplot as plt



def draw_data_plt(if_ture:bool,x_gen,pd_price,load_nor,pd_load,number=1000000):
    if if_ture:
        fig, (axs1, axs2, axs3, axs4) = plt.subplots(4, 1)

        dist_x_gen = list(range(len(x_gen)))
        axs1.plot(dist_x_gen[:number], x_gen[:number])

        dist_price = list(range(len(pd_price)))
        axs2.plot(dist_price[:number], pd_price[:number])
        axs2.set_ylabel('price')

        dist_x_load = list(range(len(pd_load)))

        nor_load = load_nor
        axs4.plot(dist_x_load[:number], nor_load[:number])

        plt.show()




