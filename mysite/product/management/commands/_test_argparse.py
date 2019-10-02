import os
import sys
from anytree import Node, RenderTree
from anytree.search import find_by_attr as node_find
Category = ['2851.9.62.72.75', '11187.69.3666.184', '2851.9.62.63', '2.1', '2851.10', '16', '12.34382.80',
            '8.4485.119', '16.178.199', '16.182.196', '8.4489.207', '16.81.82', '12218.170.42010.172',
            '2.1.35', '2851.7', '2.1.26', '136.137.142', '3003.19', '12218.170.42010.173', '8.4203.91.94',
            '2851.3.171', '16.178', '16.81.43239.185.191', '45722.20', '2851.9.62.63.67','12218.170.42010.167',
            '8.20324.132', '2851.21', '12218.170.42010.174', '16.178.198','2851.18', '12', '12218.170', '2851.3',
            '12218.170.42010.176', '2', '8.4203.97', '2851.7.169','16.81.43239.185', '2.1.50', '2851.11',
            '16.81.43239.185.190', '8.4485.98', '12218.170.42010.177', '16.81.43239.185.188']


def get_category_tree():
    tree = Node('root')
    for row in Category:
        path = row.split('.')
        point = tree
        for node in path:
            print(f'{path} --> {node}',end='\t')
            point = add_node(node, point)
    return tree


def add_node(node_name, point: Node):
    node_exist = node_find(point, node_name)
    if node_exist:
        print('EXIST')
        return node_exist
    else:
        print('add')
        return Node(node_name, parent=point)


if __name__ == "__main__":
    a = get_category_tree()
    print(RenderTree(a))
    s = '1.1.1.1.1.1.2.3'
    print(s.split('.')[-2])
    print(os.getcwd())
    print(sys.getsizeof(a.descendants))
