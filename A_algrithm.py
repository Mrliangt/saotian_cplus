import time
from collections import deque
import sys
from PyQt5.QtWidgets import QApplication


import time


class QipanNode:
    """九宫格拼图的节点，记录每一步的状态"""

    def __init__(self, qipan, h_type, parent=None, action=None, cost=0):
        # 当前拼图状态
        self.qipan = qipan
        # 父节点（上一个状态）
        self.parent = parent
        # 到达当前状态的操作（例如：'上移'，'下移'等）
        self.action = action
        # 从起点到当前节点的步数
        self.cost = cost
        # 启发式估值
        if h_type == 'M':
            self.heuristic = qipan.get_manhattan_distance()
        elif h_type == 'O':
            self.heuristic = qipan.UoLa_distance()
        else:
            self.heuristic = qipan.XOR_nums()
        # 总估值（步数 + 启发式值）
        self.total_value = cost + self.heuristic

    def get_path(self):
        """获取从起点到当前节点的路径"""
        path = []
        current_node = self
        # 通过不断找父节点回溯路径
        while current_node is not None:
            path.append((current_node.qipan, current_node.action))
            current_node = current_node.parent
        # 反转路径，让起点在前
        path.reverse()
        return path


class QipanSolver:
    """拼图问题求解器"""

    def __init__(self):
        # 记录搜索过的节点数量
        self.searched_nodes = 0
        # 记录队列的最大长度
        self.max_queue_size = 0
        # 存储找到的解决方案路径
        self.solution = None
        # 记录搜索过程
        self.search_history = []
        # 是否找到解的标记
        self.found_solution = False
        # 记录求解耗时
        self.time_used = 0

    def solve(self, start_qipan, h_type='M'):
        """开始求解拼图问题"""
        start_time = time.time()

        # 初始化起点节点
        start_node = QipanNode(start_qipan, h_type)

        # 如果初始状态就是目标状态
        if start_qipan.is_goal():
            self.solution = [(start_qipan, None)]
            self.found_solution = True
            self.time_used = time.time() - start_time
            return self.solution

        # 准备两个列表：
        open_list = [start_node]  # 待探索节点列表
        closed_list = []  # 已探索节点列表

        # 开始搜索循环
        while len(open_list) > 0:
            # 记录队列最大长度
            if len(open_list) > self.max_queue_size:
                self.max_queue_size = len(open_list)

            # 找出open_list中估值最小的节点
            min_value = float('inf')  # 初始设为无穷大
            current_node = None
            # 遍历所有待探索节点找最小值
            for node in open_list:
                if node.total_value < min_value:
                    min_value = node.total_value
                    current_node = node
            #print('minVlaue:',min_value)

            # 从open_list移除当前节点
            open_list.remove(current_node)

            # 添加到已探索列表
            closed_list.append(current_node)

            # 增加搜索计数
            self.searched_nodes += 1
            #print(current_node.qipan)
            # 记录搜索过程
            self.search_history.append(current_node.qipan)

            # 检查是否找到目标
            if current_node.qipan.is_goal():
                self.solution = current_node.get_path()
                self.found_solution = True
                self.time_used = time.time() - start_time
                return self.solution

            # 生成所有可能的下一步状态
            next_states = current_node.qipan.get_branch()
            #print('next_states',next_states)

            # 处理每个可能的下一步
            for new_qipan, move in next_states:
                # 创建新节点
                new_node = QipanNode(
                    qipan=new_qipan,
                    h_type=h_type,
                    parent=current_node,
                    action=move,
                    cost=current_node.cost + 1
                )
                #print('新节点:',new_node.qipan.state)
                #print("h:", h_type)
                # print(new_node.qipan.state)
                # 检查新状态是否已经探索过
                already_explored = False
                # 遍历已关闭列表
                for closed_node in closed_list:
                    judge = True
                    #print('已探索节点为:',closed_node.qipan.state)
                    for i in range(3):
                        for j in range(3):
                            judge = judge & (closed_node.qipan.state[i][j] == new_node.qipan.state[i][j])
                    if judge:
                        already_explored = True
                        #print('该节点已经被探索过')
                        break
                    #print('test seccess!!!')
                if already_explored:
                    continue

                # 检查是否在待探索列表中
                in_open_list = False
                for open_node in open_list:
                    judge = True
                    for i in range(3):
                        for j in range(3):
                            judge = judge and (open_node.qipan.state[i][j] == new_node.qipan.state[i][j])
                    if judge:
                        in_open_list = True
                        break
                if not in_open_list:
                    open_list.append(new_node)
            if new_node.cost == 60:
                print("无法找到合适解")
                return None

        # 如果循环结束还没找到解
        self.time_used = time.time() - start_time
        return None

    # def get_stats(self):
    #     """获取求解统计信息"""
    #     return {
    #         "已探索节点": self.searched_nodes,
    #         "最大队列长度": self.max_queue_size,
    #         "解路径长度": len(self.solution) - 1 if self.solution else 0,
    #         "耗时": round(self.time_used, 4),
    #         "是否找到解": self.found_solution
    #     }