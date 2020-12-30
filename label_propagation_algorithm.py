import signed_utils as utils
import random as rd
import collections


class LabelPropagation:

    def __init__(self, dataset: utils.Dataset, neighborhood):
        """
        标签传播算法

        :param dataset: 数据集
        :param neighborhood: 邻域结构
        """
        self._dataset = dataset
        self.neighborhood = neighborhood

    def label_propagation(self, max_iter=5, print_info=False):
        """
        基于标签传播的初始解生成方式。

        :param print_info: 输出信息开关
        :param max_iter: 最大迭代次数
        :return: solution: dict, partition: dict(community: set())
        """

        solution, __ = utils.standard_initialize(self._dataset.vnum)
        changed = True
        ct = 0

        random_v = list(range(self._dataset.vnum))
        rd.shuffle(random_v)

        while changed and ct < max_iter:
            ct += 1
            changed = False

            for node in random_v:

                mcc = self.__most_common_community_label(node, current_solution=solution, node_neighborhood=self.neighborhood[node])
                if changed is False and mcc != solution[node]:
                    changed = True
                solution[node] = mcc

        # reform the solution and partition
        partition = utils.solution2partition(solution)
        partition = utils.reform_partition(partition)
        solution = utils.partition2solution(partition, self._dataset.vnum)

        if print_info:
            print('Solution:', solution)
            print('Partition:', partition)
            print('Number of clusters:', len(partition))

        return solution, partition

    @staticmethod
    def __most_common_community_label(node, current_solution, node_neighborhood):
        """
        找到最公共的社区标签

        :param node: 节点序号
        :return: 正邻居为其社区+1，负邻居为其社区-1.由此得到的最大值
        """
        pos_nbr, neg_nbr = node_neighborhood['+'], node_neighborhood['-']

        label_num = collections.defaultdict(int)

        for elem in pos_nbr:
            label_num[current_solution[elem]] += 1
        for elem in neg_nbr:
            label_num[current_solution[elem]] -= 1

        if label_num:
            return max(label_num, key=label_num.get)
        else:
            return current_solution[node]