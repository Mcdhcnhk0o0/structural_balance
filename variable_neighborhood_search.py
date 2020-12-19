import time
import random as rd
import signed_utils as utils
import relocation_heuristic as relocation_heuristic
from module import *


class VariableNeighborhoodSearch:

    def __init__(self, dataset: utils.Dataset, init_solution):

        self._dataset = dataset
        self._neighborhood = Neighborhood(dataset).neighborhood_structure
        self.obj_function = Frustration(dataset=dataset, init_solution=init_solution)
        self.obj_function.update_objective_function()
        self.k = len(self.obj_function.partition)
        self.best_solution = self.obj_function.solution
        self.best_value = self.obj_function.obj_value

    def perturbation(self, y_pert=0.005):

        obj = self.obj_function

        for v in range(self._dataset.vnum):

            h = obj.solution[v]

            if len(obj.partition[h]) > 1:

                # randomly move into a new cluster with probability y_pert
                if rd.random() < y_pert:

                    cid = rd.choice(list(range(h)) + list(range(h+1, self.k)))
                    delta = obj.delta_caused_by_move(node=v, destination=cid, node_neighborhood=self._neighborhood[v])
                    obj.move(v, cid, delta)

        return obj.solution

    def relocation_heuristic(self):
        """
        算法主要流程

        :return: 一个locally optimal solution
        """

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

                        if delta < 0:
                            obj.move(v, cid, delta=delta)
                            improvement = False

        # ## end relocation heuristic ## #

        return obj.solution, obj.obj_value

    def variable_neighborhood_search(self, y_pert, y_min, y_max, y_step):

        obj = self.obj_function
        self.perturbation(y_pert=y_pert)
        self.relocation_heuristic()

        if obj.obj_value < self.best_value:
            self.best_value = obj.obj_value
            self.best_solution = obj.solution
            y_pert = y_min
        else:
            y_pert += y_step
            if y_pert > y_max:
                y_pert = y_min

        return y_pert

    def run(self, time_limit, y_pert=0.005, y_min=0.005, y_max=0.2, y_step=0.005, is_print=True):

        print('Start Variable Neighborhood Search...')
        t = 0
        start_time = time.time()

        while t < time_limit:

            y_pert = self.variable_neighborhood_search(y_pert=y_pert, y_min=y_min, y_max=y_max, y_step=y_step)

            t += 1
            if is_print:
                print('Current iteration: %d/%d' % (t, time_limit))
                print('Current best value: %d' % self.best_value)

        end_time = time.time()
        print('Variable Neighborhood Search Complete!')
        print('Running time:', end_time - start_time)
        print('Best value:', self.best_value)

        return self.best_value


if __name__ == '__main__':
    dir_path = r'C:\Users\WQQDuan\PycharmProjects\conda\social_network\src\Slashdot'
    ds_name = r'\slashdot-undirected-size10000-part0.g'
    ds = utils.load_data(dir_path + ds_name, 'signed')

    rh = relocation_heuristic.RelocationHeuristic(dataset=ds, k=8)
    rh.run(time_limit=20)
    print(rh.best_solution)
    print(rh.best_value)
    vns = VariableNeighborhoodSearch(dataset=ds, init_solution=rh.best_solution)
    vns.run(time_limit=200)
    # utils.network_plot(vns.obj_function.partition, ds)
