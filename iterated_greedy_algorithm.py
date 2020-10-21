from module.neighborhood import Neighborhood
from module.frustration import Frustration
from module.initialization import Initialization
from module.local_search import LocalSearch
import signed_utils as utils
import random as rd


"""
迭代贪心算法的一般流程：
    1. s_z <- generate an initial solution;
    2. s_* <- apply local search to s_z;
    3. while termination condition is not satisfied do:
        s_p <- apply destruction to s_*
        s_' <- apply construction to s_p
        s_' <- apply local search to s_'
        if acceptance criterion is satisfied then
            s_* <- s_'
        end
    4. return s_*
"""


class IteratedGreedy:

    def __init__(self, dataset):
        self._dataset = dataset
        self.objective_function = Frustration(dataset)
        self.neighborhood = Neighborhood(dataset).neighborhood_structure
        self.best_solution_set = []
        self.best_value = 2 << 31

    def initialization(self):
        init = Initialization(self._dataset)
        solution, partition = init.lpa_initialization(neighborhood=self.neighborhood)
        self.objective_function.set_solution(solution)
        self.objective_function.update_objective_function()

    def local_search(self):
        ls = LocalSearch(self.objective_function, self.neighborhood)
        return ls

    def destruction_and_reconstruction(self, beta):
        destruction_nodes = self.__destruction(beta)
        self.__reconstruction(destruction_nodes, p_type='all')

    def run(self, max_iter=200):
        self.initialization()
        ct = 0
        ls = self.local_search()

        while ct < max_iter:
            # print(self.objective_function.solution)
            # print(self.objective_function.partition)

            ls.local_move()
            ls.community_merge()

            if self.objective_function.obj_value < self.best_value:
                self.best_value = self.objective_function.obj_value
                self.best_solution_set = [self.objective_function.solution, self.objective_function.partition]

            print('%d/%d: best value --> %d' % (ct, max_iter, self.best_value))

            self.destruction_and_reconstruction(0.3)
            ls.local_move()
            ls.community_merge()
            ct += 1

        print('IG Complete!')
        print('=' * 40)
        print('Best Value:', self.best_value)
        print('Number of Community:', len(self.best_solution_set[1]))

    def __destruction(self, beta):

        node_num = len(self.neighborhood)
        candidate_node = rd.sample(range(node_num), int(node_num * beta))
        return candidate_node

    def __reconstruction(self, destruction_nodes, p_type):

        obj = self.objective_function

        if p_type == 'all':
            # 将结点往所有的社区进行移动
            candidate_community = set(obj.partition.keys())
            for node in destruction_nodes:
                try:
                    obj.solution[node] = rd.choice(list(candidate_community - {obj.solution[node]}))
                except IndexError:
                    continue

        elif p_type == 'neighbor':
            # 将结点往邻居社区进行移动
            for node in destruction_nodes:
                try:
                    obj.solution[node] = rd.choice(list(obj.get_adjacent_community(node, self.neighborhood)))
                except IndexError:
                    continue

        obj.partition = utils.solution2partition(obj.solution)
        obj.update_objective_function()


if __name__ == '__main__':

    file_dir = r'C:\Users\WQQDuan\PycharmProjects\conda\social_network\src\Slashdot'
    file_name = r'\slashdot-undirected-size1000-part0.g'

    ds = utils.load_data(file_dir + file_name)

    ig = IteratedGreedy(ds)
    ig.run()
