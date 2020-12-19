
import random as rd
from module.objective_function import ObjectiveFunction


class LocalSearch:

    def __init__(self, obj_function: ObjectiveFunction, neighborhood):

        self.objective_function = obj_function
        self.neighborhood = neighborhood
        self.sorted_node = self.__node_sort('')

    def local_move(self):
        """
        结点逐个向邻居社区移动

        :return:
        """

        improvement = True
        ct = 0
        obj = self.objective_function
        nbr = self.neighborhood

        while improvement:

            improvement = False
            ct += 1
            # print('current iteration of local search：', ct)

            if ct >= 100:
                break
            for node in self.sorted_node:

                # if node % 10000 == 0:
                #     print('Current node:', node)

                min_delta = 0
                candidate = -1

                for nbr_community in obj.get_adjacent_community(node, nbr):

                    delta = obj.delta_caused_by_move(node, nbr_community, nbr[node])
                    if delta < min_delta:
                        min_delta = delta
                        candidate = nbr_community

                if candidate != -1:
                    obj.move(node, candidate, min_delta)
                    improvement = True

    def community_merge(self):
        """
        对当前解的社区进行合并

        :return: None
        """

        obj = self.objective_function
        community_list = list(obj.partition.keys())
        tabu_list = set()
        # rd.shuffle(community_list)
        ct = 0
        for c1 in community_list:
            ct += 1
            # print(ct, '/', len(community_list))
            # print("Merging:", c1, ' in ', community_list)
            if c1 in tabu_list:
                # 被合并过的社区无需再次考虑，放进tabu_list并跳过
                continue

            min_delta = 0
            candidate = -1
            for c2 in obj.get_adjacent_community_of_community(c1, self.neighborhood):
                delta = obj.delta_caused_by_merge(c1, c2, self.neighborhood)
                if delta < min_delta:
                    min_delta = delta
                    candidate = c2
            # 寻找最优的移动方式
            if candidate != -1:
                obj.merge(c1, candidate, min_delta)
                tabu_list.add(c1)
                tabu_list.add(candidate)

    def community_decompose(self):
        """
        社区分解

        :return:
        """
        pass

    def __node_sort(self, sort_type):
        """
        对节点的重要性进行排序，这里采用度的大小。正负边全部包括。

        :param sort_type: 社区编号
        :return: 排序之后的节点顺序
        """

        if sort_type == 'degree':

            nbr = self.neighborhood
            node_num = len(nbr)

            nbr_len = [len(nbr[i]['+']) + len(nbr[i]['-']) for i in range(node_num)]

            # 获取邻居数目的排序结果
            sorted_node = sorted(range(node_num), key=nbr_len.__getitem__, reverse=True)

        else:

            sorted_node = list(range(len(self.neighborhood)))
            # rd.shuffle(sorted_node)

        return sorted_node
