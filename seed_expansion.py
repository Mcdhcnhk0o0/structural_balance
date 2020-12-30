import signed_utils as utils
import warnings


class SeedExpansion:

    def __init__(self, dataset: utils.Dataset, neighborhood):
        self._dataset = dataset
        self.neighborhood = neighborhood

    def seed_expansion(self, obj_function):
        """
        使用种子扩张的方式生成初始解

        :param obj_function: 目标函数类或其子类
        :return: solution: dict, partition: dict(community: set())
        """

        seeds = self.__generate_community_seeds()

        if not seeds:
            warnings.warn('No seeds are found, using standard initialization instead.')
            return utils.standard_initialize(self._dataset.vnum)
        else:
            print(len(seeds), 'seeds are found.')

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
                local_delta = obj.delta_caused_by_move(node, c, self.neighborhood[node])
                if local_delta < max_delta:
                    max_delta = local_delta
                    best_move = c

            if best_move != -1:
                obj.move(node, best_move, max_delta)

        return obj.solution, obj.partition

    def __generate_community_seeds(self):
        """
        社区种子的一种生成方法，参考文献：Detecting local community structures in complex networks
        based on local degree central nodes

        :return: 检测到的社区种子，格式为list，规模为2或3
        """

        # 结点度数 = 正度数 + 负度数
        nbr = self.neighborhood
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
