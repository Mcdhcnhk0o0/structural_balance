# encoding: utf-8


import collections
import networkx
import matplotlib.pyplot
import numpy as np


class Dataset:
    """
    # 数据集的标准格式

    vnum：结点个数，int
    enum：边的数目，int
    datasets: 网络数据，dict(dict())
    """
    def __init__(self):
        self.vnum = 0
        self.enum = 0
        self.data = []


def load_data(path: str, network_type='signed') -> Dataset:
    """
    读取数据，返回数据集

    :param path: 数据集路径
    :param network_type: 网络的类型，目前只有signed和unsigned两种
    :return: 一个Dataset，详见Dataset的描述
    """

    dataset = Dataset()
    # 使用二维字典进行数据的存储
    data = collections.defaultdict(lambda: collections.defaultdict(lambda: 0))
    print('loading datasets...')

    with open(path) as f:
        header = f.readline()
        vnum, enum = header.split()
        dataset.vnum, dataset.enum = int(vnum), int(enum)
        if network_type == 'signed':
            # 数据集格式为“结点  结点  边的属性”
            for each in f:
                n1, n2, attr = each.split()
                if attr != '1' and attr != '-1':
                    continue
                n1, n2 = int(n1), int(n2)
                data[n1][n2] = data[n2][n1] = int(attr)
        elif network_type == 'unsigned':
            # 数据集格式为“结点  结点”
            for each in f:
                n1, n2 = each.split()
                n1, n2 = int(n1), int(n2)
                data[n1][n2] = data[n2][n1] = 1
        else:
            print('no such type of network')
            raise TypeError

    dataset.data = data
    print('loading complete...')

    return dataset


def load_data_with_start_one(path: str, network_type: str) -> Dataset:
    """
    读取数据，返回数据集

    :param path: 数据集路径
    :param network_type: 网络的类型，目前只有signed和unsigned两种
    :return: 一个Dataset，详见Dataset的描述
    """
    dataset = Dataset()
    # 使用二维字典进行数据的存储
    data = collections.defaultdict(dict)
    with open(path) as f:
        header = f.readline()
        vnum, enum = header.split()
        dataset.vnum, dataset.enum = int(vnum), int(enum)
        if network_type == 'signed':
            # 数据集格式为“结点  结点  边的属性”
            for each in f:
                n1, n2, attr = each.split()
                n1, n2 = int(n1)-1, int(n2)-1
                data[n1][n2] = data[n2][n1] = int(attr)
        elif network_type == 'unsigned':
            # 数据集格式为“结点  结点”
            for each in f:
                n1, n2 = each.split()
                n1, n2 = int(n1)-1, int(n2)-1
                data[n1][n2] = data[n2][n1] = 1
        else:
            print('no such type of network')
            raise TypeError
    dataset.data = data
    print('loading datasets...')
    return dataset


def partition2solution(partition: dict, vnum: int, solution_type='dict') -> dict or np.array:
    """
    # 将集合形式的划分转化为向量形式的解

    :param solution_type: 要求返回的解的格式，默认是dict，指定为array时返回np.array
    :param partition: 以dict(community: list())形式传入
    :param vnum: int, number of vertex in the partition
    :return: {vid: cid}形式给出结点号与社区号的对应
    """

    if not partition:
        return {}
    solution = [0] * vnum
    for idx, community in partition.items():
        for node in community:
            solution[node] = idx

    if solution_type == 'array':
        return np.array(solution)
    else:
        return {i: solution[i] for i in range(vnum)}


def solution2partition(solution: dict or np.array or list) -> dict:
    """
    # 将字典形式的解转化为集合划分形式

    :param solution: dict()
    :return: dict(community: set())
    """

    if solution is None:
        return dict()
    partition = collections.defaultdict(set)

    if isinstance(solution, dict):
        for node, comm in solution.items():
            partition[comm].add(node)

    elif isinstance(solution, np.ndarray):
        for node, comm in enumerate(solution):
            if comm not in partition.keys():
                partition[comm] = {node}
            else:
                partition[comm].add(node)

    elif isinstance(solution, list):
        for node, comm in enumerate(solution):
            partition[comm].add(node)

    else:
        raise TypeError('Solution类型错误，无法转换！')

    return partition


def standard_initialize(vnum: int) -> (dict, dict):
    """
    将每个结点看作一个社区进行初始化。

    :param vnum: 网络的节点数目
    :return: solution:list, partition:dict(community: list())
    """

    partition = dict()
    solution = dict(enumerate(list(range(vnum))))
    for i in range(vnum):
        partition[i] = {i}
    return solution, partition


def reform_partition(partition: dict) -> dict:
    """
    :param partition: dict(community: list())
    :return: community: range(len(partition))
    """
    # 重新调整划分的表示方式，让社区号从0开始并逐一递增
    re_partition = dict()
    idx = 0
    for cluster in partition.values():
        re_partition[idx] = cluster
        idx += 1
    return re_partition


def dataset2g(dataset, file_name='generated_dataset.g'):
    """
    可以把生成的数据集写成一个.g文件，便于多次使用

    :param file_name:
    :param dataset: 一个Dataset类
    :return: 将对应的.g文件写入当前目录
    """

    with open(file_name, 'w') as f:

        f.write(str(dataset.vnum) + '\t' + str(dataset.enum) + '\n')
        for node in dataset.data:
            for nbr, attr in dataset.data[node].items():
                f.write(str(node) + '\t' + str(nbr) + '\t' + str(attr) + '\n')

    print('-> 数据集存储完毕，命名为：' + file_name)


def network_plot(partition: dict, dataset: Dataset):
    """
    :param partition: dict(community: set())
    :param dataset: 一个Dataset, 由load_data产生
    :return: None, 仅用于作图
    """
    # 给出数据集和划分，进行绘图，仅适用于小型网络
    g = networkx.Graph()
    # 给定几种可选颜色
    color_set = ['red', 'yellow', 'blue', 'green', 'orange', 'black', 'brown', 'gold', 'olive', 'pink', 'lime', 'darksage']
    if len(partition) > len(color_set):
        print('too many communities(', len(partition), '), need more kind of colors->', len(color_set))
        raise KeyError
    # 设置节点颜色与边的颜色
    node_color = []
    edge_color = []
    # 从数据集中读取边和结点
    for idx, comm in enumerate(partition.keys()):
        for each in partition[comm]:
            g.add_node(each)
            node_color.append(color_set[idx % len(color_set)])
    for node in dataset.data:
        for nbr, attr in dataset.data[node].items():
            g.add_edge(node, nbr)
            if attr == 1:
                edge_color.append('black')
            else:
                edge_color.append('red')
    # 作图
    networkx.draw_networkx(g, with_labels=True, node_size=120, font_size=6, node_color=node_color, edge_color=edge_color)
    matplotlib.pyplot.show()


def collect_degree_info(dataset: Dataset, neighborhood) -> dict:
    """
    收集度的信息。

    :return: 一个字典，{节点编号：度的信息}
    """
    degree = dict()
    for i in range(dataset.vnum):
        pos_degree = len(neighborhood[i]['+'])
        neg_degree = len(neighborhood[i]['-'])
        i_degree = {
            '+': pos_degree,
            '-': neg_degree
        }
        degree[i] = i_degree

    return degree


def detect_isolated_nodes(vnum, neighborhood):
    """

    :param vnum:
    :param neighborhood:
    :return:
    """
    alone = set()
    isolated = set()

    for i in range(vnum):
        if not neighborhood[i]['+']:
            if not neighborhood[i]['-']:
                alone.add(i)
            else:
                isolated.add(i)

    print('alone(no neighbors, total', len(alone), '):', alone)
    print('isolated(no pos neighbors, total', len(isolated), '):', isolated)

    return alone, isolated
