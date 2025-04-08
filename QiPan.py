import random
import numpy as np
from copy import deepcopy

class Qipan:
    def __init__(self, state=None, target=None):
       if target == None:
           self.target = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 0]])
       else:
           self.target = np.array(target)

       if state == None:
           self.state = self.generate_random()
       else:
           self.state = np.array(state)

       self.zero_pos = self.get_zero_pos()

    def count_inversions(self, nums):
        inversions = 0
        for i in range(len(nums)):
            if nums[i] == 0:
                continue
            for j in range(i+1, len(nums)):
                if nums[j] != 0 and nums[i] > nums[j]:
                    inversions += 1
        return inversions

    def is_solvable(self):
        """
        对于3*3的九宫格问题，当且仅当初始状态和目标状态的逆序数奇偶性相同时有解
        """
        flat_state = self.state.flatten()
        flat_target = self.target.flatten()
        row, col = self.get_zero_pos()
        state_inversions = self.count_inversions(flat_state) + row
        target_inversions = self.count_inversions(flat_target) + row
        return state_inversions % 2 == target_inversions % 2

    def generate_random(self):
        while True:
            numbers = list(range(0,9))
            random.shuffle(numbers)
            state = np.array(numbers).reshape(3, 3)

            # 直接检查生成的状态是否可解，而不是创建新的Qipan实例
            flat_state = state.flatten()
            flat_target = self.target.flatten()
            #print('此时目标棋盘为:', self.target)
            state_inversions = self.count_inversions(flat_state)
            target_inversions = self.count_inversions(flat_target)

            # 检查逆序数奇偶性是否相同
            if state_inversions % 2 == target_inversions % 2:
                return state

    def get_zero_pos(self):
        pos = np.where(self.state == 0)    # 返回值--
        return (pos[0][0], pos[1][0])

    # 判断是否满足目标状态
    def is_goal(self):
        return np.array_equal(self.state, self.target)

    # 计算欧拉距离
    def UoLa_distance(self):
        distance = 0
        for i in range(3):
            for j in range(3):
                if self.state[i][j] != 0:
                    pos = np.where(self.target == self.state[i][j])
                    goal_i, goal_j = pos[0][0], pos[1][0]
                    p1 = np.array([i, j])
                    p2 = (goal_i, goal_j)
                    distance += np.linalg.norm(p1 - p2)
        return distance

    def get_manhattan_distance(self):
        """计算当前状态到目标状态的曼哈顿距离"""
        distance = 0
        for i in range(3):
            for j in range(3):
                if self.state[i][j] != 0:  # 不计算空格
                    # 找到数字在目标状态中的位置
                    pos = np.where(self.target == self.state[i][j])
                    goal_i, goal_j = pos[0][0], pos[1][0]
                    # 计算曼哈顿距离
                    distance += abs(i - goal_i) + abs(j - goal_j)
        return distance

    def XOR_nums(self):
        count = 0
        for i in range(3):
            for j in range(3):
                if self.state[i][j] != 0 and self.state[i][j] != self.target[i][j]:
                    count += 1
        return count
    # 判断可能移动的方向
    def get_Alldir(self):
        i, j = self.zero_pos
        dirs = []

        if i > 0:
            dirs.append('U')
        if i < 2:
            dirs.append('D')
        if j > 0:
            dirs.append('L')
        if j < 2:
            dirs.append('R')

        return dirs

    # 移动空格
    def To_move(self, dir):
        i, j = self.zero_pos

        new_state = deepcopy(self.state)

        if dir == 'U' and i > 0:
            new_state[i][j] = new_state[i-1][j]
            new_state[i-1][j] = 0
            new_state = new_state.tolist()
            starget = self.target
            starget = starget.tolist()
            new_Qipan = Qipan(new_state, starget)
            # print(i, j)
            return new_Qipan

        elif dir == 'D' and i < 2:
            new_state[i][j] = new_state[i+1][j]
            new_state[i+1][j] = 0
            new_state = new_state.tolist()
            starget = self.target
            starget = starget.tolist()
            new_Qipan = Qipan(new_state, starget)
            return new_Qipan

        elif dir == 'L' and j > 0:
            new_state[i][j] = new_state[i][j-1]
            new_state[i][j-1] = 0
            new_state = new_state.tolist()
            starget = self.target
            starget = starget.tolist()
            new_Qipan = Qipan(new_state, starget)
            return new_Qipan

        elif dir == 'R' and j < 2:
            new_state[i][j] = new_state[i][j+1]
            new_state[i][j+1] = 0
            new_state = new_state.tolist()
            starget = self.target
            starget = starget.tolist()
            new_Qipan = Qipan(new_state, starget)
            return new_Qipan

        else:
            return None

    # 获得分枝数
    def get_branch(self):
        branches = []

        all_dirs = self.get_Alldir()
        # print("all_dirs", all_dirs)
        for dir in all_dirs:
            branch = self.To_move(dir)
            if branch:
                branches.append((branch, dir))
                # print("branch", branch)

        return branches





























    def __str__(self):
        """返回状态的字符串表示"""
        s = ""
        for i in range(3):
            for j in range(3):
                s += str(self.state[i][j]) + " "
            s += "\n"
        return s

    def __eq__(self, other):
        """判断两个状态是否相等"""
        return np.array_equal(self.state, other.state)

    def __hash__(self):
        """返回状态的哈希值，用于在集合中检查重复状态"""
        return hash(str(self.state))