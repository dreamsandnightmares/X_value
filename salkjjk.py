import xlwt
import random
import numpy as np
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
import xlrd
import scipy
from data_load.data_load import data_load
pd_load,pd_price,pd_wea_wind,pd_wea_G_dir,pd_wea_G_diff,pd_wea_T ,pd_wea_G_hor= data_load()
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
x_data = []
y_data = []

x_data1 = []
y_data1 = []

data1 = pd_price[:465]

# table = data.sheets()[0]
#
# data1 = xlrd.open_workbook('train_reward_2.xls')
# table1 = data1.sheets()[0]
#
# cap = table.col_values(1)  # 读取第二列数据
# cap1 = table.col_values(0)  # 读取第一列数据
# print(cap)  #打印出来检验是否正确读取

# cap2 = table1.col_values(1)  # 读取第二列数据
# cap3 = table1.col_values(0)  # 读取第一列数据
# print(cap)  #打印出来检验是否正确读取

# for i in range(1, 9999):
#     y_data.append(cap[i])
#     # x_data.append(cap1[i]*50) #对第一列数据扩大50倍
#     x_data.append(cap1[i])  # 对第一列数据扩大50倍
#
# for i in range(1, 2321):
#     y_data1.append(cap2[i])
#     # x_data.append(cap1[i]*50) #对第一列数据扩大50倍
#     x_data1.append(cap3[i])  # 对第一列数据扩大50倍

# ?平滑处理：
x_data = list(range(len(data1)))
# plt.plot(x_data,data1)
# plt.show()
tmp_smooth1 = scipy.signal.savgol_filter(data1, 25, 3)
# tmp_smooth2 = scipy.signal.savgol_filter(y_data,63,4)
plt.semilogx(x_data, data1, label="pd_price", alpha=0.2)  # //增加透明度
plt.semilogx(x_data, tmp_smooth1, label='price-smooth', color='red')
# plt.semilogx(x_data,tmp_smooth2,label = 'mic'+str(1)+'拟合曲线-53',color = 'green')

# tmp_smooth3 = scipy.signal.savgol_filter(y_data1, 25, 3)
# # %  window_length的值越小，曲线越贴近真实曲线；window_length值越大，平滑效果越厉害
# # ! k值推荐3-5k值越大，曲线越贴近真实曲线；k值越小，曲线平滑越厉害。另外，当k值较大时，受窗口长度限制，拟合会出现问题，高频曲线会变成直线
# # tmp_smooth2 = scipy.signal.savgol_filter(y_data,63,4)
# plt.semilogx(x_data1, y_data1, label="DDPG", alpha=0.3)  # //增加透明度
# plt.semilogx(x_data1, tmp_smooth3, label='DDPG-smooth', color='blue')

# plt.plot(x_data, y_data,color="#006bac")
plt.title('Savitzky-Golay 滤波器25/3')
plt.legend()  # 标签

plt.xlabel('episodes')
plt.ylabel('Average reward')
plt.show()