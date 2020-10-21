import time
import random as rd
import signed_utils as utils
from module import *

"""
分离了算法流程、邻域结构与目标函数，算法只需要关注自己本身的实现
-> 邻域操作由Neighborhood提供，静态访问
-> 目标函数单独成为一个类，提供计算方式、解的表示、邻域移动带来的变化
-> 算法主要包含自身的组件与流程，提供一个run()函数运行
"""


class RelocationHeuristic:

    def __init__(self, dataset: utils.Dataset, k):
        """
        算法执行必要的一些参数，用于初始化

        :param dataset: 数据集，由utils中读入并自定义
        :param k: cluster的数目
        """
        self.k = k
        self._dataset = dataset
        self._neighborhood = Neighborhood(dataset).neighborhood_structure
        self.obj_function = None
        self.best_solution = None
        self.best_value = 2 << 64

    def neighborhood_similarity(self, u, v):
        """
        结点u和v的相似度定义为：二者的公共正邻居与负邻居的数目

        :param u: 结点的编号
        :param v: 另一个结点的编号
        :return: 二者的相似度
        """
        return len(self._neighborhood[u]['+'] & self._neighborhood[v]['+']) + \
            len(self._neighborhood[u]['-'] & self._neighborhood[v]['-'])

    def random_select(self):
        """
        随机选出k个exemplars

        :return: set(exemplars)
        """
        # A check is made to assure that no two vertices having the exact
        # same edge set are selected

        exemplar = set(rd.sample(range(self._dataset.vnum), self.k))

        return exemplar

    def initialization(self, exemplar):
        """
        根据随机选择的初始核进行解的构造

        :param exemplar: 由random_select()返回的随机选择的初始核心
        :return: 构造的初始解向量
        """

        init_solution = dict.fromkeys(range(self._dataset.vnum), -1)
        remain = set(range(self._dataset.vnum)) - exemplar

        for idx, vertex in enumerate(exemplar):
            init_solution[vertex] = idx

        for vertex in remain:
            similarity = [self.neighborhood_similarity(vertex, u) for u in exemplar]
            idx, __ = max(enumerate(similarity), key=lambda x: x[1])
            init_solution[vertex] = idx

        return init_solution

    def relocation_heuristic(self):
        """
        算法主要流程

        :return: 一个locally optimal solution
        """
        # initialize solution
        exemplar = self.random_select()
        init_solution = self.initialization(exemplar)

        # set objective function
        self.obj_function = Frustration(dataset=self._dataset, init_solution=init_solution)
        self.obj_function.update_objective_function()
        obj = self.obj_function

        # ## start relocation heuristic ## #

        improvement = False

        while not improvement:
            improvement = True

            for v in range(self._dataset.vnum):
                h = obj.solution[v]

                # try to find the best movement
                if len(obj.partition[h]) > 1:

                    for cid in set(range(self.k)) - {h}:
                        delta = obj.delta_caused_by_move(node=v, destination=cid, node_neighborhood=self._neighborhood[v])
                        # make sure the increment is correct

                        if delta < 0:
                            obj.move(v, cid, delta=delta)
                            improvement = False

        # ## end relocation heuristic ## #

        return obj.solution, obj.obj_value

    def run(self, time_limit, is_print=True):
        """
        算法的运行函数，采用Multi-start的形式单线程运行

        :param time_limit: 时间限制或者迭代次数限制
        :param is_print: 是否打印运行过程中的信息
        :return:
        """

        print('Start Multi-start Relocation Heuristic...')
        t = 0
        start_time = time.time()
        while t < time_limit:
            if is_print:
                print('--> Current iteration: %d/%d' % (t, time_limit))
            solution, value = self.relocation_heuristic()

            if value < self.best_value:
                self.best_value = value
                self.best_solution = solution

            t += 1
            if is_print:
                print('---> Locally optimal value:', value)

        end_time = time.time()
        print('Multi-start Relocation Heuristic Complete!')
        print('Running time:', end_time - start_time)
        print('Best value:', self.best_value)

        return self.best_value


if __name__ == '__main__':

    dir_path = r'C:\Users\WQQDuan\PycharmProjects\conda\social_network\src\Slashdot'
    ds_name = r'\slashdot-undirected-size400-part0.g'
    ds = utils.load_data(dir_path + ds_name, 'signed')
    rh = RelocationHeuristic(dataset=ds, k=4)
    best_val = rh.run(20)
    print('Best frustration：', best_val)
