import heapq

def find_safe_route(graph, start, end, blocked_nodes):
    n = len(graph)
    blocked = set(blocked_nodes)
    # Can't find route if start or end is blocked
    if start in blocked or end in blocked:
        return ([], -1)
    # dist[i] = shortest known time to reach node i
    dist = [float('inf')] * n
    dist[start] = 0
    # prev[i] = which node we came from to reach i
    prev = [-1] * n
    # Min-heap: (cost, node)
    heap = [(0, start)]

    while heap:
        current_dist, u = heapq.heappop(heap)
        if current_dist > dist[u]:
            continue
        #  exit if we've reached the destination
        if u == end:
            break
        # Explore neighbours
        for v in range(n):
            if graph[u][v] == 0:  
                continue
            if v in blocked:
                continue

            new_dist = dist[u] + graph[u][v]
            if new_dist < dist[v]:
                dist[v] = new_dist
                prev[v] = u
                heapq.heappush(heap, (new_dist, v))
    # No path found
    if dist[end] == float('inf'):
        return ([], -1)

    path = []
    node = end
    while node != -1:
        path.append(node)
        node = prev[node]
    path.reverse()

    return (path, dist[end])

# put your input here

graph = [
    [0, 5, 0, 8, 0],
    [5, 0, 3, 0, 0],
    [0, 3, 0, 2, 7],
    [8, 0, 2, 0, 4],
    [0, 0, 7, 4, 0]
]

start_node = 0
end_node = 4
blocked = [3]

print(find_safe_route(graph, start_node, end_node, blocked))  
print(find_safe_route(graph, start_node, end_node, []))
print(find_safe_route(graph, start_node, end_node, [2,3]))