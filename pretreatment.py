from module import *
import signed_utils as utils


file_dir = r'C:\Users\WQQDuan\PycharmProjects\conda\social_network\src\Slashdot'
file_name = r'\slashdot-undirected-size2000-part0.g'

dataset = utils.load_data(file_dir + file_name)
nbr = Neighborhood(dataset).neighborhood_structure

alone, isolated = utils.detect_isolated_nodes(dataset.vnum, nbr)
isolated = {str(i) for i in isolated}

new_file_name = file_name[:-2] + '-treated.g'

with open(file_dir + file_name) as f:
    with open(file_dir + new_file_name, 'w') as g:
        head = f.readline()
        g.write(head)
        for line in f:
            n1, n2, attr = line.strip().split()
            if n1 in isolated or n2 in isolated:
                continue
            g.write(line)

print('Pretreatment complete!')
