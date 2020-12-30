import signed_utils as utils
from module.local_search import LocalSearch


class Initialization:
    """
    提供了多种生成初始解的方法：
    1. standard initialization，每个结点单独成社区；
    2. greedy_initialization，贪心策略，本质上是一趟的局部搜索；
    3. seed_initialization，先生成社区种子，然后将其余点归结至种子所在社区；
    4. lpa_initialization，基于几趟标签传播的初始解生成方式；
    5. grasp_initialization，贪心随机自适应算法生成。

    """

    def __init__(self, dataset: utils.Dataset, neighborhood):
        self._dataset = dataset
        self.neighborhood = neighborhood

    def standard_initialization(self):
        """
        将每个结点看作一个社区进行初始化。

        :return: solution: dict, partition: dict(community: set())
        """

        return utils.standard_initialize(self._dataset.vnum)

    def greedy_initialization(self, obj_function):
        """
        思想源于Louvain算法：局部结点移动，与local_search中的local_move策略相同

        :param obj_function: 目标函数
        :return:
        """

        method = LocalSearch(obj_function, self.neighborhood)
        method.local_move()
        return method.objective_function.solution, method.objective_function.partition

    def seed_initialization(self, obj_function):
        """
        使用种子扩张的方式生成初始解

        :param obj_function: 目标函数类或其子类
        :return: solution: dict, partition: dict(community: set())
        """

        import seed_expansion as sea
        seed_init = sea.SeedExpansion(self._dataset, self.neighborhood)
        return seed_init.seed_expansion(obj_function)

    def lpa_initialization(self, max_iter=5):
        """
        基于标签传播的初始解生成方式。

        :param max_iter: 最大迭代次数
        :return: solution: dict, partition: dict(community: set())
        """

        import label_propagation_algorithm as lpa
        lpa_init = lpa.LabelPropagation(self._dataset, self.neighborhood)
        return lpa_init.label_propagation(max_iter=max_iter, print_info=False)

    def grasp_initialization(self):
        pass


if __name__ == '__main__':

    file_path = r'C:\Users\WQQDuan\PycharmProjects\conda\social_network\src\Slashdot\slashdot-undirected-size600-part0.g'

    ds = utils.load_data(file_path, 'signed')

    from module.neighborhood import Neighborhood
    from module.frustration import Frustration

    # 调用示范
    obj_func = Frustration(ds)
    print(obj_func.solution)
    # greedy
    so, pa = Initialization(ds, neighborhood=Neighborhood(ds).neighborhood_structure).greedy_initialization(obj_func)
    # seed
    # so, pa = Initialization(ds, neighborhood=Neighborhood(ds).neighborhood_structure).seed_initialization(obj_func)
    # lpa
    # so, pa = Initialization(ds, neighborhood=Neighborhood(ds).neighborhood_structure).lpa_initialization(max_iter=20)
    print(so)
    print(pa)
    obj_func.set_solution(solution=so)
    obj_func.update_objective_function()
    print(obj_func.obj_value)
    # utils.network_plot(pa, dataset=ds)
