import warnings
import collections
import random as rd
import signed_utils as utils


class Initialization:
    """
    提供了三种生成初始解的方法：
    1. standard initialization，每个结点单独成社区；
    2. seed_initialization，先生成社区种子，然后将其余点归结至种子所在社区；
    3. lpa_initialization，基于几趟标签传播的初始解生成方式；

    其中1和3与目标函数无关，2则需要传入相应的目标函数才能有对应的结果。
    """

    def __init__(self, dataset: utils.Dataset):
        self._dataset = dataset
        pass

    def standard_initialization(self):
        """
        将每个结点看作一个社区进行初始化。

        :return: solution: dict, partition: dict(community: set())
        """

        partition = dict()
        solution = dict(enumerate(list(range(self._dataset.vnum))))
        for i in range(self._dataset.vnum):
            partition[i] = {i}
        return solution, partition

    def seed_initialization(self, neighborhood, obj_function):
        """
        使用种子扩张的方式生成初始解

        :param neighborhood: 邻域结构
        :param obj_function: 目标函数类或其子类
        :return: solution: dict, partition: dict(community: set())
        """

        seeds = self.__generate_community_seeds(neighborhood=neighborhood)

        if not seeds:
            warnings.warn('No seeds are found, using standard initialization instead.')
            return self.standard_initialization()
        else:
            print(len(seeds), 'seeds are found.')

        # 引入目标函数类，实例化好之后传进来
        obj = obj_function

        # 创建初始解
        init_solution = obj.solution
        for seed in seeds:
            cid = init_solution[seed[0]]
            for other in seed[1:]:
                init_solution[other] = cid

        obj.set_solution(solution=init_solution)
        obj.update_objective_function()
        seeds_flatten = [i for j in seeds for i in j]
        cluster_candidate = set([init_solution[i] for i in seeds_flatten])

        # 种子扩张
        for node in set(range(self._dataset.vnum)) - set(seeds_flatten):

            max_delta = 2 << 63
            best_move = -1
            for c in cluster_candidate:
                local_delta = obj.delta_caused_by_move(node, c, neighborhood[node])
                if local_delta < max_delta:
                    max_delta = local_delta
                    best_move = c

            if best_move != -1:
                obj.move(node, best_move, max_delta)

        return obj.solution, obj.partition

    def lpa_initialization(self, neighborhood, max_iter=5):
        """
        基于标签传播的初始解生成方式。

        :param max_iter: 最大迭代次数
        :param neighborhood: 邻域结构
        :return: solution: dict, partition: dict(community: set())
        """

        solution, __ = self.standard_initialization()
        changed = True
        ct = 0

        random_v = list(range(self._dataset.vnum))
        rd.shuffle(random_v)

        while changed and ct < max_iter:
            ct += 1
            changed = False

            for node in random_v:
                # print(solution)
                mcc = self.__most_common_community_label(node, current_solution=solution, node_neighborhood=neighborhood[node])
                # print('from', solution[node], 'to ', mcc)
                if changed is False and mcc != solution[node]:
                    changed = True
                solution[node] = mcc

        # 整理一下解
        partition = utils.solution2partition(solution)
        partition = utils.reform_partition(partition)
        solution = utils.partition2solution(partition, self._dataset.vnum)
        print(len(partition))

        return solution, partition

    def __generate_community_seeds(self, neighborhood):
        """
        社区种子的一种生成方法，参考文献：Detecting local community structures in complex networks
        based on local degree central nodes

        :return: 检测到的社区种子，格式为list，规模为2或3
        """

        # 结点度数 = 正度数 + 负度数
        nbr = neighborhood
        relative_degree = {i: len(nbr[i]['+']) + len(nbr[i]['-']) for i in range(self._dataset.vnum)}

        candidate = []

        for idx, degree in relative_degree.items():
            # 收集邻域的度数情况
            try:
                nbr_degree = [(i, relative_degree[i]) for i in nbr[idx]['+']]
                max_nbr_id, max_nbr_degree = max(nbr_degree, key=lambda x: x[1])
            except ValueError:
                continue
            if degree > max_nbr_degree:
                # 若当前点的度数高于任何一个正邻居的度数，则认为它是一个局部度中心结点
                # 同时，找到它的最大度正邻居，绑定在一起
                third_nbr = nbr[idx]['+'] & nbr[max_nbr_id]['+']
                # 如果有二者的公共正邻居仍不为空，找最大的正邻居加入他们
                if third_nbr:
                    third_nbr_degree = [(i, relative_degree[i]) for i in third_nbr]
                    third_chosen, __ = max(third_nbr_degree, key=lambda x: x[1])
                    candidate.append([idx, max_nbr_id, third_chosen])
                else:
                    candidate.append([idx, max_nbr_id])

        return candidate

    @ staticmethod
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


if __name__ == '__main__':

    file_path = r'C:\Users\WQQDuan\PycharmProjects\conda\social_network\src\Slashdot\slashdot-undirected-size600-part0.g'

    ds = utils.load_data(file_path, 'signed')

    from module.neighborhood import Neighborhood
    from module.frustration import Frustration

    # 调用示范
    obj_func = Frustration(ds)
    # so, pa = Initialization(ds).seed_initialization(Neighborhood(ds).neighborhood_structure, obj_func)
    so, pa = Initialization(ds).lpa_initialization(Neighborhood(ds).neighborhood_structure, max_iter=20)

    # utils.network_plot(pa, dataset=ds)
