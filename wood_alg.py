def min_str(str_graph, visited):
    mn_value_ind = [24, 0]
    for i in range(len(str_graph)):
        if str_graph[i] != 0 and str_graph[i] < mn_value_ind[0] and i not in visited:
            mn_value_ind[0] = str_graph[i]
            mn_value_ind[1] = i
    return mn_value_ind


def ost_tree(G):
    visited = [0]
    res_graph = [[0, 0, 0, 0] for i in range(len(G))]

    for i in range(len(G) - 1):
        edge_min = [0, 0, 12345678]

        for ind_vis in visited:
            min_in_str = min_str(G[ind_vis], visited)

            if edge_min[2] > min_in_str[0]:
                edge_min[0] = ind_vis
                edge_min[1] = min_in_str[1]
                edge_min[2] = min_in_str[0]

        res_graph[edge_min[0]][edge_min[1]] = edge_min[2]
        res_graph[edge_min[1]][edge_min[0]] = edge_min[2]

        visited.append(edge_min[1])

    return res_graph


def DFS(ostov_tree, start, end):
    res_way = [start]
    n = len(ostov_tree)
    used = [False] * n
    Stack = [start]
    used[start] = True
    while Stack:
        v = Stack[-1]
        moved_deeper = False
        for i in range(n):
            if ostov_tree[v][i] != 0 and ostov_tree[v][i] != end and not used[i]:
                moved_deeper = True
                Stack.append(i)
                used[i] = True
                res_way.append(i)
                break
        if not moved_deeper:
            Stack.pop()
    if start == end:
        res_way.append(end)
    return res_way


def way_wood_alg(start, end, graph):
    tree = ost_tree(graph)
    way = DFS(tree, start, end)
    return way