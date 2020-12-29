from module import *
from unittest import TestCase
import signed_utils as utils
import unittest


file_dir = r'C:\Users\WQQDuan\PycharmProjects\conda\social_network\src\Slashdot'
file_name = r'\slashdot-undirected-size1000-part0.g'

dataset = utils.load_data(file_dir + file_name)
nbr = Neighborhood(dataset=dataset).neighborhood_structure


class TestInitialization(TestCase):

    init = Initialization(dataset=dataset, neighborhood=nbr)

    def test_greedy(self):
        obj_function = Frustration(dataset=dataset)
        solution, partition = self.init.greedy_initialization(obj_function)
        self.assertIsInstance(partition, dict)

    def test_seed(self):
        obj_function = Frustration(dataset=dataset)
        solution, partition = self.init.seed_initialization(obj_function)
        self.assertIsInstance(partition, dict)

    def test_lpa(self):
        solution, partition = self.init.lpa_initialization()
        self.assertIsInstance(partition, dict)


class TestFrustration(TestCase):

    objective_function = Frustration(dataset=dataset)

    def test_frustration(self):
        f1 = self.objective_function.objective_function()
        f2 = self.objective_function.objective_function_v2(nbr)
        self.assertEqual(f1, f2)


class TestLocalSearch(TestCase):

    objective_function = Frustration(dataset=dataset)
    ls = LocalSearch(obj_function=objective_function, neighborhood=nbr)

    def test_move(self):
        self.objective_function.update_objective_function()
        self.ls.local_move()
        value_after_move = self.objective_function.obj_value
        self.objective_function.update_objective_function()
        value_after_update = self.objective_function.obj_value
        self.assertEqual(value_after_update, value_after_move)

    def test_merge(self):
        self.objective_function.update_objective_function()
        self.ls.community_merge()
        value_after_merge = self.objective_function.obj_value
        self.objective_function.update_objective_function()
        value_after_update = self.objective_function.obj_value
        self.assertEqual(value_after_update, value_after_merge)


if __name__ == '__main__':
    unittest.main()
