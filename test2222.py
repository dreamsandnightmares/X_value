import cplex
import numpy as np

# 构造矩阵 A 和向量 b
A = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
b = np.array([1, 2, 3])

# 构造目标函数系数向量 c 和变量边界下限和上限数组
c = np.array([1, -1, 2])
lb = np.array([0, 0, 0])
ub = np.array([1, 2, 3])

# 创建 cplex 对象并设置线程数为 4
problem = cplex.Cplex()
problem.parameters.threads.set(4)

# 添加变量、目标函数以及约束条件
problem.variables.add(names=["x1", "x2", "x3"], lb=lb, ub=ub)
problem.objective.set_sense(problem.objective.sense.minimize)
problem.objective.set_linear(zip(range(3), c))
problem.linear_constraints.add(rhs=b, senses="L" * len(b))
for i in range(len(b)):
    problem.linear_constraints.set_linear_components(i, zip(range(3), A[i]))

# 求解并打印结果
problem.solve()
print("Solution status: ", problem.solution.get_status())
print("Optimal value: ", problem.solution.get_objective_value())
print("Solution vector: ", problem.solution.get_values())