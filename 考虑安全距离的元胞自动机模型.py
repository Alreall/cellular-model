import random
import matplotlib.pyplot as plt
import numpy as np
import xlwt
import csv

# 元胞尺寸0.5m
# 定义人工驾驶车辆
class Car:
    def _init_(self, length, width):
        self.length = length                # 车长
        self.width = width                  # 车宽

    length = 15
    width = 1.6
    # 静态参数
    an = 6                                  # 最大加速度
    bn = 5                                  # 舒适减速
    B = 7                                   # 最大减速度
    T = 1.5                                 # 安全车头时距
    ty = 0                                  # 车辆类型
    v_max = 75                              # 最大速度
    front = None                            # 前车
    back = None                             # 后车
    v = 0                                   # 车辆速度
    x = 0                                   # 车头位置
    p = 0.3                                 # 随机慢化概率

    # 更新车间距
    def updateD(self):
        if self.x > self.front.x:
            return self.front.x + Road.length - self.x - self.front.length
        else:
            return self.front.x - self.x - self.front.length

    # 定义安全距离
    def update_Gapsafe(self):
        return self.v * self.T + (self.v ** 2) / (2 * self.B)-(self.front.v**2) / (2*self.B)

    # 定义安全速度
    def update_vsafe(self):
        dn = self.updateD()
        return (max((self.bn*self.T)**2+self.bn*(2*dn-self.T*self.v+(self.front.v**2) / self.bn), 0)) ** 0.5-self.bn * self.T

    # 更新车速
    def _update_v(self):
        Gap_safe = self.update_Gapsafe()
        vsafe = self.update_vsafe()
        gap = max(self.updateD(), 0)
        # 加速行驶
        if gap > Gap_safe:
            self.v = min(self.v + self.an, self.v_max, vsafe, gap)
        # 匀速行驶
        elif gap == Gap_safe:
            self.v = min(self.v, gap)
        # 减速行驶
        else:
            if self.front.v == 0:
                self.v = max(min(vsafe, gap - 1), 0)
            else:
                self.v = max(min(vsafe, gap), 0)
        # 随机慢化过程
        if np.random.random() <= self.p:
            self.v = max(self.v - self.bn, 0)

    # 更新位置
    def update_x(self):
        self._update_v()
        self.x = (self.x+self.v) % Road.length

# 定义智能网联车辆
class CAV:
    def _init_(self, length, width):
        self.length = length            # 车长
        self.width = width              # 车宽

    length = 15
    width = 1.6
    # 静态参数
    an = 6                              # 最大加速度
    bn = 5                              # 舒适减速度
    B = 7                               # 最大减速度
    T = 0                               # 安全车头时距
    v_max = 75                          # 最大速度
    ty = 1                              # 车辆类型
    front = None                        # 前车
    back = None                         # 后车
    v = 0                               # 车辆速度
    x = 0                               # 车头位置

    # 更新车间距
    def updateD(self):
        if self.x > self.front.x:
            return self.front.x + Road.length - self.x - self.front.length
        else:
            return self.front.x - self.x - self.front.length

    # 定义安全距离
    def update_Gapsafe(self):
        return self.v * self.T + (self.v ** 2) / (2 * self.B) - (self.front.v ** 2) / (2 * self.B)

    # 定义安全速度
    def update_vsafe(self):
        dn = self.updateD()
        return (max((self.bn*self.T)**2+self.bn*(2*dn-self.T * self.v+self.front.v**2 / self.bn), 0))**0.5-self.bn*self.T

    # 更新车速
    def _update_v(self):
        if self.front.ty == 1:
            self.T = 0.6
            Gap_safe = self.update_Gapsafe()
            vsafe = self.update_vsafe()
            gap = self.updateD()
            # 加速行驶
            if gap > Gap_safe:
                self.v = min(self.v + self.an, self.v_max, vsafe, gap)
            # 匀速行驶
            elif gap == Gap_safe:
                self.v = min(self.v, gap)
            # 减速行驶
            else:
                if self.front.v == 0:
                    self.v = max(min(vsafe, gap - 1), 0)
                else:
                    self.v = max(min(vsafe, gap), 0)
        else:
            self.T = 1.1
            Gap_safe = self.update_Gapsafe()
            vsafe = self.update_vsafe()
            gap = self.updateD()
            # 加速行驶
            if gap > Gap_safe:
                self.v = min(self.v + self.an, self.v_max, vsafe, gap)
            # 匀速行驶
            elif gap == Gap_safe:
                self.v = min(self.v, gap)
            # 减速行驶
            else:
                if self.front.v == 0:
                    self.v = max(min(vsafe, gap - 1), 0)
                else:
                    self.v = max(min(vsafe, gap), 0)

    # 更新位置
    def update_x(self):
        self._update_v()
        self.x = (self.x + self.v) % Road.length

# 设置道路
class Road:
    def _init_(self, motorPercent, length, width):
        self.motorPercent = motorPercent                        # 道路占有率
        self.length = length                                    # 车道长度
        self.width = width                                      # 车道宽度


    motorPercent = 0.9
    length = 10000
    width = 3.5


    # 初始化道路车辆
    def initCars(self):
        # 计算车辆数量
        self.num0fcar = int(self.length / 15 * self.motorPercent)
        # 生成车辆
        self.ls = []
        gas = self.length/self.num0fcar
        for i in range(self.num0fcar):
            random_num = random.random()
            if random_num < 1:
                c = Car()
                # 等间距放置车辆
                c.x = i * gas
                c.v = 0
                c.index = i
            else:
                c = CAV()
                # 等间距放置车辆
                c.x = i * gas
                c.v = 0
                c.index = i
            self.ls.append(c)
            # 新增车辆为上一辆车的前车
            if i > 0:
                c.back = self.ls[self.ls.index(c)-1]
                c.back.front = c
        # 头车的前车是尾车
        self.ls[len(self.ls)-1].front = self.ls[0]
        self.ls[0].back = self.ls[len(self.ls)-1]

    # 运行
    def run(self, time_max):
        # 初始化道路
        self.initCars()
        # 开始仿真
        for time in range(time_max):
            # 车辆位置更新
            for c in self.ls:
                c.update_x()

# 获取输入道路的平均车速
def get_vMean(r, timeMax):
    # 初始化道路
    r.initCars()
    # 开始仿真
    ls = []
    vSum = 0
    for time in range(timeMax):
        # 车辆位置更新
        for c in r.ls:
            c.update_x()
            vSum = vSum + c.v
        # 计算当前时间步平均车速
        ls.append(vSum / r.num0fcar)
        vSum = 0
    return sum(ls) / len(ls)

# 获取密度-速度
def get_K_V():
    V_ls = np.zeros((1, 20))
    K_ls = np.zeros((1, 20))
    timeMax = 500
    j = 0
    for i in np.arange(0.05, 1, 0.05):
        r = Road()
        r.motorPercent = i
        V_ls[0, j] = get_vMean(r, timeMax)*1.8
        K_ls[0, j] = r.num0fcar / r.length * 2000
        j = j + 1
    return K_ls, V_ls

# 绘制速度-密度图
def plot_K_V(K_V):
    # 输入元组第0个元素为密度，第1个元素为平均速度
    ls_K = []
    ls_V = []
    for i in range(19):
        ls_K.append(K_V[0][0, i])
        ls_V.append(K_V[1][0, i])
    plt.plot(ls_K, ls_V)
    plt.title('密度-速度图', fontsize=35)
    plt.xlabel('密度', fontsize=30)
    plt.ylabel('速度', fontsize=30)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.show()

# 绘制流量-密度图
def plot_K_Q(K_V):
    # 输入元组第0个元素为密度，第1个元素为平均速度
    ls_K = []
    ls_Q = []
    for i in range(19):
        ls_K.append(K_V[0][0, i])
        ls_Q.append(K_V[1][0, i] * K_V[0][0, i])
    plt.plot(ls_K, ls_Q)
    plt.title('密度-流量图', fontsize=35)
    plt.xlabel('密度', fontsize=30)
    plt.ylabel('流量', fontsize=30)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.show()

# 绘制流量-速度图
def plot_V_Q(K_V):
    # 输入元组第0个元素为密度，第1个元素为平均速度
    ls_V = []
    ls_Q = []
    for i in range(19):
        ls_V.append(K_V[1][0, i])
        ls_Q.append(K_V[1][0, i] * K_V[0][0, i])
    plt.plot(ls_Q, ls_V)
    plt.title('速度-流量图', fontsize=35)
    plt.xlabel('流量', fontsize=30)
    plt.ylabel('速度', fontsize=30)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.show()

# 写入数据

def xlsWrite(K_V):
    # 创建文件对象
    f = open('p=10.csv','w',encoding='utf-8',newline="")
    # 基于文件对象构建csv写入对象
    csv_write = csv.writer(f)
    # 构建列表头
    csv_write.writerow(['密度', '速度', '流量'])
    # 写入csv文件
    for i in range(19):
        csv_write.writerow([K_V[0][0, i],K_V[1][0, i],K_V[0][0, i] * K_V[1][0, i]])
    f.close()

#################### main
# 创建道路
r = Road()
# 展示动画
################### 动画展示
r.motorPercent = 0.3
timeMax = 100
# r.show(timeMax)
################### 三参数图
# 获取占有率-速度
K_V = get_K_V()
# 汇出密度-速度图
# plot_K_V(K_V)
# 汇出密度-流量图
plot_K_Q(K_V)
# 汇出速度-流量图
################### 导出数据
# plot_V_Q(K_V)
# 写入excel文件
# xlsWrite(K_V)
################### v_max变化
# for i in range(1,7):
#     Car.v_max = 5*i
#     K_V = get_K_V()
#     plot_K_Q(K_V)
#     #plot_V_Q(K_V)
#     #plot_K_V(K_V)
# plt.legend(labels=['5','10','15','20','25','30'],fontsize = 20)
################### S变化
# for i in np.arange(1.4,2,0.1):
#     Car.S = i
#     K_V = get_K_V()
#     #plot_K_Q(K_V)
#     #plot_V_Q(K_V)
#     plot_K_V(K_V)
# plt.legend(labels=['1','2','3','4','5'],fontsize = 20)
################### T变化
# for i in np.arange(1.4,2,0.1):
#     Car.T = i
#     K_V = get_K_V()
#     #plot_K_Q(K_V)
#     #plot_V_Q(K_V)
#     plot_K_V(K_V)
# plt.legend(labels=['1','2','3','4','5'],fontsize = 20)
################### par变化
# for i in range(1,6):
#     Car.par = i*0.2
#     K_V = get_K_V()
#     plot_K_Q(K_V)
#     #plot_V_Q(K_V)
#     #plot_K_V(K_V)
# plt.legend(labels=['0.2','0.4','0.6','0.8','1'],fontsize = 20)

