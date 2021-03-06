import numpy as np
import math
import networkx as nx
import matplotlib.pyplot as plt

MATRIX_SIZE=8
DISCOUNT = 0.9
LR = 0.9

PRICE = 9
TIME = 2
EPISODES = 10000


NODES = 8
graph = [[1,6],[2],[3],[4,6],[5,6],[0],[5],[]]

price_to_pay =[
    [0,2,0,0,0,0,2,0],
    [0,0,1,0,0,0,0,0],
    [0,0,0,5,0,0,0,0],
    [0,0,0,0,4,0,0,0],
    [0,0,0,0,0,20,0,0],
    [3,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0]]

time_to_pay =[
    [0,2,0,0,0,0,2,0],
    [0,0,1,0,0,0,0,0],
    [0,0,0,5,0,0,0,0],
    [0,0,0,0,4,0,0,0],
    [0,0,0,0,0,20,0,0],
    [3,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0]]

G = nx.DiGraph()

round_point = 0
nodes = [x for x in range(NODES)]
nodes_goodness = [5, 5, 100, 100, 100, 5, 350, 100]


T = np.matrix(np.zeros(shape=(MATRIX_SIZE, MATRIX_SIZE)))
R = np.matrix(np.ones(shape=(MATRIX_SIZE, MATRIX_SIZE))) * -1
Q = np.random.uniform(low=0, high=0, size=(MATRIX_SIZE **2 * PRICE*6 * TIME*6)).reshape(MATRIX_SIZE, PRICE*6, TIME*6, MATRIX_SIZE)

labels = {}
for x in range(len(graph)):
    labels[x] = str(nodes_goodness[x]) + "\n\n\n\n"
    if len(graph[x]) == 0:
        G.add_edges_from([(x,x)], weight=0)
    for neigh in graph[x]:
        R[x, neigh] = nodes_goodness[neigh]
        G.add_edges_from([(x, neigh)], weight=price_to_pay[x][neigh])
        T[x, neigh] = math.sin(nodes_goodness[neigh])
        if neigh is round_point:
            R[x, neigh] = 100
plt.figure(figsize=(10,7))

pos = nx.planar_layout(G)
edge_labels=dict([((u,v,),d['weight'])
                 for u,v,d in G.edges(data=True)])
nx.draw_networkx_edge_labels(G,pos,edge_labels=edge_labels)
edge_colors = ['black' for edge in G.edges()]
nx.draw(G,pos, node_size=1000, with_labels=True, labels=labels, label_color="red", node_color = "yellow", edge_color=edge_colors,edge_cmap=plt.cm.Reds, font_color="green")
nx.draw_networkx_labels(G,pos)
plt.axis('off')
plt.show()

def collect_possible_prices(state,cost):
    neighs = graph[state]
    prices = []
    for neigh in neighs:
        prices.append(price_to_pay[state][neigh])
    return [x + cost for x in prices]

def collect_possible_times(state,cost):
    neighs = graph[state]
    prices = []
    for neigh in neighs:
        prices.append(time_to_pay[state][neigh])
    return [x + cost for x in prices]

def available_actions(state):
    return np.where(R[state,] >= 0)[1]

def sample_next_action(state, actions, random=True):
    if random:
        return int(np.random.choice(actions, 1))
    else:
        best_choice = 0
        maximum = float("-inf")
        for i in actions:
            goodness = price_to_pay[state][i]/nodes_goodness[i]
            if goodness >=maximum:
                maximum = goodness
                best_choice = i
        return best_choice


def update(state, action, cost, time):
    if cost<PRICE and time<TIME:
        future_q=np.max(Q[action,collect_possible_prices(action,cost),collect_possible_times(action,cost),])
        new_q = (1-LR) * Q[state,cost,time,action] + LR * (R[state,action] + DISCOUNT * future_q)
        Q[state,cost,time,action] = new_q
        if action == round_point:
            Q[state,cost,time,action] += max(nodes_goodness)*2
        return False
    else:
        return True

for i in range(EPISODES):
    just_started = True
    state = round_point
    price_cost = 0
    time_cost = 0
    while state!=round_point or just_started:
        just_started = False
        av_actions = available_actions(state)
        action = sample_next_action(state, av_actions)
        price_cost += price_to_pay[state][action]
        time_cost += time_to_pay[state][action]
        terminate = update(state,action, price_cost,time_cost)
        if terminate:
            break
        state = action

current_state = round_point
steps = [current_state]
first = True
while current_state != round_point or first == True:
    first = False
    next_state = np.unravel_index(Q[current_state].argmax(),Q.shape)[3]
    steps.append(next_state)
    current_state = next_state

print("Most efficient path:")
print(steps)

price_used = 0
time_used = 0
for i in range(len(steps)-1):
    price_used += price_to_pay[steps[i]][steps[i+1]]
    time_used += time_to_pay[steps[i]][steps[i+1]]
print("Price used", price_used)


red_edges = []
for i in range(0,len(steps)-1):
    red_edges.append((steps[i],steps[i+1]))
edge_colors = ['black' if not edge in red_edges else 'green' for edge in G.edges()]
node_colors = ['purple' if x is round_point else 'yellow' for x in range(NODES)]
plt.figure(figsize=(10,7))
nx.draw_networkx_labels(G,pos)
nx.draw(G,pos, node_color = node_colors, edge_color=edge_colors,edge_cmap=plt.cm.Reds, title="asdasd")

plt.title(f"Most Efficient path: {steps} \n Price used: {price_used}/{PRICE} \n Time used: {time_used}/{TIME}")
plt.axis('off')

plt.show()