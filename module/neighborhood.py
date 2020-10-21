# encoding: utf-8


import signed_utils as utils


class Neighborhood:

    def __init__(self, dataset: utils.Dataset):
        self._dataset = dataset
        self.neighborhood_structure = self.__collect_neighbor_info()

    def __collect_neighbor_info(self) -> dict:
        """
        收集邻域信息。因为符号网络的邻居涉及到正负，实时找的代价稍高，故存起来。

        :return: 一个字典，{节点编号：节点的邻居}，其中 节点的邻居={'正'：(正邻居集合), '负'：(负邻居集合)}
        """
        neighbors = dict()
        for i in range(self._dataset.vnum):
            neighbors[i] = self.__get_neighbors(i)

        return neighbors

    def __get_neighbors(self, node) -> dict:
        """
        找到结点node的所有邻居，并且把正负邻居分开。

        :param node: 结点编号
        :return: 一个字典，{'正'：(正邻居集合), '负'：(负邻居集合)}
        """

        # 做一个判断，先算出正负边的数目，可能加快找邻居的速度
        nbr = self._dataset.data[node].keys()
        nbr_values = self._dataset.data[node].values()
        neg_num = (len(nbr_values) - sum(nbr_values)) / 2
        pos_num = len(nbr_values) - neg_num

        # 依据边的数目找邻居，最差情况也就是遍历整个邻居集合
        neg_nbr, pos_nbr = [], []

        if pos_num > neg_num:
            # 先找负的邻居
            for nid, attr in self._dataset.data[node].items():
                if neg_num == 0:
                    break
                if attr == -1:
                    neg_nbr.append(nid)
                    neg_num -= 1
            pos_nbr = set(nbr) - set(neg_nbr)
            nbr_structure = {
                '+': set(pos_nbr),
                '-': set(neg_nbr)
            }

        else:
            # 先找正的邻居
            for nid, attr in self._dataset.data[node].items():
                if pos_num == 0:
                    break
                if attr == 1:
                    pos_nbr.append(nid)
                    pos_num -= 1
            neg_nbr = set(nbr) - set(pos_nbr)
            nbr_structure = {
                '+': set(pos_nbr),
                '-': set(neg_nbr)
            }

        return nbr_structure
