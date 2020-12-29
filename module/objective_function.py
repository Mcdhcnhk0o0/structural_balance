import signed_utils as utils


class ObjectiveFunction:

    def __init__(self, dataset: utils.Dataset, init_solution=None):
        """
        初始化流程

        :param dataset: 读入的数据集，格式在utils中给出
        :param init_solution: 可选参数，初始解
        """

        self._dataset = dataset
        self.obj_value = - 2 << 32

        if init_solution is None:
            self.solution, self.partition = utils.standard_initialize(self._dataset.vnum)
        else:
            self.solution = init_solution
            self.partition = utils.solution2partition(init_solution)

    def set_solution(self, solution):
        """
        更改当前解

        :param solution: 想要修改成的解
        :return: None
        """
        self.solution = solution
        self.partition = utils.solution2partition(solution)

    def update_objective_function(self):
        """
        更新目标函数值

        :return:
        """
        self.obj_value = self.objective_function()
        return self.obj_value

    def objective_function(self):
        return self.obj_value

    def objective_function_v2(self, neighborhood, partition=None):
        return self.obj_value

    def move(self, node, destination, delta):
        pass

    def delta_caused_by_move(self, node, destination, neighborhood):
        pass

    def merge(self, c1, c2, delta):
        pass

    def delta_caused_by_merge(self, c1, c2, neighborhood):
        pass

    def get_adjacent_community(self, node, neighborhood) -> set:
        """
        # 找到结点node的邻接社区

        :param neighborhood: 数据集的邻域结构
        :param node: 结点序号
        :return: 其邻接社区
        """
        nbr = neighborhood[node]['+'] | neighborhood[node]['-']
        nbr_community = set([self.solution[i] for i in nbr])
        # when the element doesn't exist, discard would not raise KeyError
        nbr_community.discard(self.solution[node])

        return nbr_community

    def get_adjacent_community_of_community(self, cid, neighborhood):
        """
        # 找到社区cid的邻接社区

        :param cid: 社区编号
        :param neighborhood: 邻域结构
        :return: 编号为vid的社区的所有邻接社区
        """

        adjacent_node = set()
        # bug here
        # TODO the algorithm about adjacent community needs to be optimized
        # the algorithm to find neighbor communities is inefficient

        for node in self.partition[cid]:
            adjacent_node = adjacent_node | neighborhood[node]['+'] | neighborhood[node]['-']

        adjacent_community = set([self.solution[i] for i in adjacent_node])
        adjacent_community.discard(cid)

        return adjacent_community
