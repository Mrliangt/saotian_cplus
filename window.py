import time
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QButtonGroup
from jedi.inference.utils import to_list

from QipanUI import Ui_Dialog
from QiPan import *
from PyQt5.QtCore import Qt, QTimer
from A_algrithm import QipanSolver

class MainWindow(QMainWindow, Ui_Dialog):
    def __init__(self, parent=None, is_editable=True):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.editable = is_editable
        # 初始左棋盘显示--图形
        self.current_state_Qipan = [[self.State_pos1, self.State_pos2, self.State_pos3],
                                    [self.State_pos4, self.State_pos5, self.State_pos6],
                                    [self.State_pos7, self.State_pos8, self.State_pos9]]
        # 目标右棋盘显示--图形
        self.target_state_Qipan = [[self.Target_pos1, self.Target_pos2, self.Target_pos3],
                                    [self.Target_pos4, self.Target_pos5, self.Target_pos6],
                                    [self.Target_pos7, self.Target_pos8, self.Target_pos9]]

        self.initial_state_qipan = Qipan(state=[[1, 2, 3], [4, 5, 6], [7, 8, 0]])  # 未设置时初始状态棋盘
        self.initial_goal_qipan = Qipan([[1, 2, 3], [4, 5, 6], [7, 8, 0]])   # 用户未手动设置目标状态棋盘

        # 左边棋盘--值
        self.state_qipan = Qipan(state=[[1, 2, 3], [4, 5, 6], [7, 8, 0]])   # 当前初始状态棋盘
        # 右边棋盘--值
        self.target_qipan = Qipan(target=[[1, 2, 3], [4, 5, 6], [7, 8, 0]]) # 当前目标状态棋盘

        self.resetbutton.clicked.connect(self.reset_Qipan)                  # 重置按钮
        self.random_button.clicked.connect(self.generate_random_Qipan)      # 随机生成初始状态的棋盘

        self.set_targetbutton.clicked.connect(self.set_targetState)         # 设置目标状态按钮

        self.Back_lastState.clicked.connect(self.BackToLast_state)           # 回退上一步
        self.Back_lastTarget.clicked.connect(self.BackToLast_target)       # 回退上一步


        self.solveit = QipanSolver()                                            # 解决方案创建
        self.animation_timer = QTimer()                                     # 动画定时器
        self.animation_timer.timeout.connect(self.animate_solution)
        self.solution_steps = []
        self.current_step = 0                                               # 有效路径步数记录

        self.M_Button.setChecked(True)
        ### 启发式函数选择


        self.Solve_button.clicked.connect(self.solve_Qipan)  # 求解按钮
        # 将棋盘上的按钮关联函数
        for m in range(3):
            for n in range(3):
                self.current_state_Qipan[m][n].clicked.connect(lambda checked, i=m, j=n: self.curNums_clicked(i, j))
        for m in range(3):
            for n in range(3):
                self.target_state_Qipan[m][n].clicked.connect(lambda checked, i=m, j=n:self.tarNums_clicked(i, j))

        self.step_i = 0

    def reset_Qipan(self):
        #self.initial_qipan = Qipan()
        #self.goal_qipan = Qipan([[1, 2, 3], [4, 5, 6], [7, 8, 0]])

        # 重置初始状态和目标状态为[[1，2，3],[4,5,6],[7,8,0]]
        self.set_curQipan(self.initial_state_qipan)
        self.set_targetQipan(self.initial_goal_qipan)

        # 重置求解状态
        # self.solution_steps = []
        # self.current_step = 0
        # #self.step_btn.setEnabled(False)
        # self.animation_timer.stop()

    def generate_random_Qipan(self):
        target_nums = self.target_qipan.state
        target_nums = target_nums.tolist()
        self.initial_qipan = Qipan(target=target_nums)
        #print('此时目标棋盘为:',target_nums)
        self.set_curQipan(self.initial_qipan)


        # 重置求解状态
        self.solution_steps = []
        self.current_step = 0
        # self.step_btn.setEnabled(False)
        self.animation_timer.stop()

    def solve_Qipan(self):
        # 获取初始状态棋盘的当前状态
        self.step_i = 0
        current_state = self.get_curstate()
        current_state = current_state.tolist()
        # 获取目标状态棋盘的当前状态
        target_nums = self.get_tarstate()
        target_nums = target_nums.tolist()

        self.last_state = current_state
        self.last_target = target_nums

        self.h_func = self.buttonGroup.checkedButton().text()
        if self.buttonGroup.checkedButton().text() == '曼哈顿距离':
            self.h_func = 'M'
        elif self.buttonGroup.checkedButton().text() == '欧式距离':
            self.h_func = 'O'
        else:
            self.h_func = 'Y'
        print(self.h_func)
        # 将当前左右两棋盘的数值传给左侧棋盘
        self.state_qipan = Qipan(current_state, target_nums)

        if  not self.state_qipan.is_solvable():
            print("无解")
            return
        #print('初始状态:',self.state_qipan.state)
        #print('目标状态:',self.state_qipan.target)
        start_time = time.time()
        self.solution_steps = self.solveit.solve(self.state_qipan, h_type=self.h_func)
        end_time = time.time()
        if self.h_func == 'M':
            self.SET_M_TIME.setText(str(end_time - start_time))
        elif self.h_func == 'O':
            self.SET_O_TIME.setText(str(end_time - start_time))
        else:
            self.SET_Y_TIME.setText(str(end_time - start_time))
        self.ans_path = [step for state, step in self.solution_steps]
        print(self.ans_path)

        # 如果找到解，开始动画
        if self.solution_steps:
            self.current_step = 0
            #self.step_btn.setEnabled(True)
            self.start_animation()
        else:
            print("无解")
            #self.status_label.setText("无法找到解!")


    def BackToLast_state(self):
        self.state_qipan = Qipan(self.last_state, self.last_target)
        self.update_curQipan()
    def BackToLast_target(self):
        self.target_qipan = Qipan(self.last_target, self.last_target)
        self.update_tarQipan()

    def set_targetState(self):
        current_state = self.get_tarstate()
        current_state = current_state.tolist()
        # 更新目标状态
        print('test success')
        self.target_qipan = Qipan(target=current_state)
        self.state_qipan.target = np.array(current_state)


    # 设置当前九宫格状态及更新函数
    def set_curQipan(self, qipan):
        self.state_qipan = qipan
        self.update_curQipan()

    def update_curQipan(self):
        if self.state_qipan is not None:
            for i in range(3):
                for j in range(3):
                    if self.state_qipan.state[i][j] == 0:
                        self.current_state_Qipan[i][j].setText(' ')
                    else:
                        self.current_state_Qipan[i][j].setText(str(self.state_qipan.state[i][j]))
    # 设置目标九宫格状态及更新函数
    def set_targetQipan(self, qipan):
        self.target_qipan = qipan
        self.update_tarQipan()

    def update_tarQipan(self):
        if self.target_qipan is not None:
            for i in range(3):
                for j in range(3):
                    if self.target_qipan.state[i][j] == 0:
                        self.target_state_Qipan[i][j].setText(' ')
                    else:
                        self.target_state_Qipan[i][j].setText(str(self.target_qipan.state[i][j]))

    def curNums_clicked(self, row, col):
        if not self.editable:
            return
        Zero_pos_row, Zero_pos_col =self.state_qipan.zero_pos

        if (row == Zero_pos_row and abs(col - Zero_pos_col) == 1) or\
                (col == Zero_pos_col and abs(row - Zero_pos_row) == 1):
            t = self.state_qipan.state[row][col]
            self.state_qipan.state[row][col] = 0
            self.state_qipan.state[Zero_pos_row][Zero_pos_col] = t

            self.state_qipan.zero_pos = [row, col]
            self.update_curQipan()

    def tarNums_clicked(self, row, col):
        if not self.editable:
            return
        Zero_pos_row, Zero_pos_col =self.target_qipan.zero_pos

        if (row == Zero_pos_row and abs(col - Zero_pos_col) == 1) or\
                (col == Zero_pos_col and abs(row - Zero_pos_row) == 1):
            t = self.target_qipan.state[row][col]
            self.target_qipan.state[row][col] = 0
            self.target_qipan.state[Zero_pos_row][Zero_pos_col] = t

            self.target_qipan.zero_pos = [row, col]
            self.update_tarQipan()

    def get_curstate(self):
        state = []
        for i in range(3):
            row = []
            for j in range(3):
                if self.current_state_Qipan[i][j].text() == ' ':
                    row.append(0)
                else:
                    row.append(int(self.current_state_Qipan[i][j].text()))
            state.append(row)
        return np.array(state)

    def get_tarstate(self):
        state = []
        for i in range(3):
            row = []
            for j in range(3):
                if self.target_state_Qipan[i][j].text() == ' ':
                    row.append(0)
                else:
                    row.append(int(self.target_state_Qipan[i][j].text()))
            state.append(row)

        return np.array(state)
    def start_animation(self):
        """开始动画"""
        # 设置动画间隔（毫秒）
        interval = 1000 // 2
        self.animation_timer.start(interval)

    def animate_solution(self):
        """动画展示解决方案"""

        if self.step_i < len(self.ans_path):
            if self.ans_path[self.step_i] == None:
                self.step_i += 1
                pass
            else:
                self.state_qipan=self.state_qipan.To_move(self.ans_path[self.step_i])
                self.step_i += 1
                self.set_curQipan(self.state_qipan)
