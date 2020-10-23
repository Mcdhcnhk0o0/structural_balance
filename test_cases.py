from module import *
import signed_utils as utils
import time


file_dir = r'C:\Users\WQQDuan\PycharmProjects\conda\social_network\src\Slashdot'
file_name = r'\slashdot-undirected-size1000-part0.g'

dataset = utils.load_data(file_dir + file_name)
nbr = Neighborhood(dataset=dataset).neighborhood_structure


# 测试local search
def test_of_local_search():
    obj = Frustration(dataset=dataset)
    obj.update_objective_function()

    ls = LocalSearch(obj_function=obj, neighborhood=nbr)

    print('test of move')
    print(ls.objective_function.obj_value)
    ls.local_move()
    print(ls.objective_function.obj_value)
    ls.objective_function.update_objective_function()
    print(ls.objective_function.obj_value)

    print('test of merge')
    ls.community_merge()
    print(ls.objective_function.obj_value)
    ls.objective_function.update_objective_function()
    print(ls.objective_function.obj_value)


# 测试frustration的两种计算方式
def test_of_frustration_v2():
    obj = Frustration(dataset=dataset)
    t1 = time.time()
    print('v1:', obj.objective_function())
    t2 = time.time()
    print('v2:', obj.objective_function_v2(neighborhood=nbr))
    t3 = time.time()
    ls = LocalSearch(obj_function=obj, neighborhood=nbr)
    ls.local_move()
    print('v1:', obj.objective_function())
    print('v2:', obj.objective_function_v2(neighborhood=nbr))

    print('time of v1:', t2 - t1)
    print('time of v2:', t3 - t2)


if __name__ == '__main__':
    test_of_frustration_v2()
