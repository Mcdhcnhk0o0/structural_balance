
import signed_utils as utils
from module.objective_function import ObjectiveFunction


class Frustration(ObjectiveFunction):

    def objective_function(self):
        """
        使用solution和dataset计算网络的line index of structural balance，时间复杂度O(m)

        :return: 当前划分下的不平衡指数
        """

        data = self._dataset.data
        sl = self.solution
        frustration = 0

        # 由于这里要频繁访问当前solution，所以最好使用dict来存储解(list查找效率很低)
        for node in data:
            cid = sl[node]
            for nbr, attr in data[node].items():
                # cluster内的负边
                if sl[nbr] == cid and attr == -1:
                    frustration += 1
                # cluster间的正边
                elif sl[nbr] != cid and attr == 1:
                    frustration += 1

        assert frustration % 2 == 0
        return frustration // 2

    def objective_function_v2(self, neighborhood):
        """
        使用partition和neighborhood计算line index of imbalance

        :param neighborhood:
        :return:
        """

        frustrations = {}

        for cid, community in self.partition.items():

            pos_out, neg_in = 0, 0

            # 计算单个社区的frustration
            for node in community:

                node_nbr = neighborhood[node]
                pos_out += len(node_nbr['+'] - community)  # 社区外正边
                neg_in += len(community & node_nbr['-'])  # 社区内负边

            frustrations[cid] = pos_out + neg_in

        return sum(frustrations.values()) // 2

    def delta_caused_by_move(self, node, destination, node_neighborhood):
        """
        将一个结点从当前的cluster移动至目标destination后，引起的变化

        :param node: 结点编号
        :param node_neighborhood: 结点node的邻域
        :param destination: 目标cluster的编号
        :return: move前 - move后，值为负则意味着line index变得更优
        """

        delta = 0
        current_cluster = self.solution[node]

        if current_cluster == destination:
            return 0

        for v in node_neighborhood['+']:

            cid = self.solution[v]
            # imbalance要求正边在cluster之间
            if cid != current_cluster and cid == destination:
                # 若正边从cluster间移动至cluster内，则imbalance减少
                delta -= 1
            elif cid == current_cluster and cid != destination:
                delta += 1

        for v in node_neighborhood['-']:

            cid = self.solution[v]
            # imbalance要求负边在cluster之内
            if cid != current_cluster and cid == destination:
                # 若负边从cluster外移动至cluster内，则imbalance增加
                delta += 1
            elif cid == current_cluster and cid != destination:
                # 反之，imbalance减少
                delta -= 1

        return delta

    def move(self, node, destination, delta):
        """
        将成员变量solution与partition进行结点移动式的调整

        :param node: 欲移动的结点
        :param destination: 目标cluster
        :param delta: 移动引起的frustration的变化，必须给出
        :return: 无
        """

        pre_cid = self.solution[node]

        self.solution[node] = destination
        self.partition[pre_cid].remove(node)
        if not self.partition[pre_cid]:
            del self.partition[pre_cid]
        self.partition[destination].add(node)

        self.obj_value += delta

    def delta_caused_by_merge(self, c1, c2, neighborhood):
        """
        将两个社区合并引起的变化

        :param c1: 社区1的编号
        :param c2: 社区2的编号
        :param neighborhood: 邻域结构
        :return: merge前-merge后，结果为负则意味着划分更优
        """

        c1_community, c2_community = self.partition[c1], self.partition[c2]
        data = self._dataset.data
        delta = 0

        for node in c1_community:
            intersection = (neighborhood[node]['+'] | neighborhood[node]['-']) & c2_community

            for another_node in intersection:
                if data[node][another_node] == 1:
                    delta -= 1
                elif data[node][another_node] == -1:
                    delta += 1

        return delta

    def merge(self, c1, c2, delta):
        """
        将成员变量solution与partition进行社区合并，将c2合并至c1

        :param c1: 欲合并的社区1
        :param c2: 欲合并的社区2
        :param delta: 合并带来的目标函数值变化
        :return: 无
        """

        for node in self.partition[c2]:
            self.solution[node] = c1

        self.partition[c1] = self.partition[c1] | self.partition[c2]
        del self.partition[c2]

        self.obj_value += delta


if __name__ == "__main__":

    file_path = r'C:\Users\WQQDuan\PycharmProjects\conda\social_network\src\Slashdot\slashdot-undirected-size200-part0.g'

    ds = utils.load_data(file_path, 'signed')

    fru = Frustration(dataset=ds)
    print(fru.obj_value)

    print(ds.vnum, ds.enum)

    # test cases
    # import structure_balance.neighborhood as test_neighborhood
    # nbr = test_neighborhood.Neighborhood(ds)
    # positive_edges = sum([len(v['+']) for k, v in nbr.neighborhood_structure.items()])
    # negative_edges = sum([len(v['-']) for k, v in nbr.neighborhood_structure.items()])
    # print('positive:', positive_edges)
    # print('negative:', negative_edges)
    # print('total edges:', positive_edges + negative_edges)

    # print(nbr.neighborhood_structure[0])
    # d = fru.delta_caused_by_move(0, 5, nbr.neighborhood_structure[0])
    # fru.move(0, 5, d)
    # print(fru.frustration)
    # print(fru.line_index())
