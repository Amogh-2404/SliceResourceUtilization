# Mathematical Formulations

This document contains all mathematical formulations from the paper "Towards Efficiently Provisioning 5G Core Network Slice Based on Resource and Topology Attributes" by Li et al. (2019).

## Table of Contents

1. [Node Ranking Attributes](#node-ranking-attributes)
2. [Combined Scoring Functions](#combined-scoring-functions)
3. [Provisioning Constraints](#provisioning-constraints)
4. [Performance Metrics](#performance-metrics)
5. [Link Provisioning Strategy](#link-provisioning-strategy)

---

## Node Ranking Attributes

### 1. Local Resource (LR)

**Equation 12:**

```
LR(vᵢ) = c(vᵢ) × ∑ b(e)
                e∈E(vᵢ)
```

**Description**: The local resource metric of a node is obtained by multiplying the CPU capacity of the node by the sum of bandwidths of all its adjacent links.

**Variables**:
- `c(vᵢ)`: CPU capacity of node vᵢ
- `b(e)`: Bandwidth of link e
- `E(vᵢ)`: Set of all adjacent links of node vᵢ

**Rationale**: The larger LR(vᵢ) is, the more slice nodes can be hosted by the physical node.

**Implementation**:
```python
def local_resource(node, graph):
    cpu = graph.get_node_cpu(node)
    adjacent_links = graph.get_adjacent_links(node)
    bandwidth_sum = sum(graph.get_link_bandwidth(link) for link in adjacent_links)
    return cpu * bandwidth_sum
```

---

### 2. Global Resource (GR)

**Equation 13:**

```
               ∑ [b(p(vᵢ, vⱼ)) + c(p(vᵢ, vⱼ))]
              i≠j
GR(vᵢ) = ───────────────────────────────────────
                      |V| - 1
```

**Description**: The global resource metric considers the minimum bandwidth of the links in the shortest path of the node to all other nodes and the minimum computing capacity of the nodes along the shortest path.

**Variables**:
- `b(p(vᵢ, vⱼ))`: Minimum bandwidth of the links in the shortest path between vᵢ and vⱼ
- `c(p(vᵢ, vⱼ))`: Minimum CPU of the nodes in the shortest path between vᵢ and vⱼ
- `|V|`: Total number of nodes in the graph

**Rationale**: Considering only local resources can cause load imbalance and resource fragmentation. Global resource attributes ensure better resource distribution.

**Implementation**:
```python
def global_resource(node, graph):
    total = 0
    nodes = graph.get_all_nodes()
    for target in nodes:
        if target != node:
            path = graph.shortest_path(node, target)
            min_bw = min(graph.get_link_bandwidth(link) for link in path.links)
            min_cpu = min(graph.get_node_cpu(n) for n in path.nodes)
            total += (min_bw + min_cpu)
    return total / (len(nodes) - 1)
```

---

### 3. Degree Centrality (DC)

**Equation 14:**

```
           ∑ aᵢⱼ
           vⱼ
DC(vᵢ) = ─────────
          |V| - 1
```

**Description**: The normalized degree centrality indicates the ratio of the number of adjacent links to the total number of links in the graph.

**Variables**:
- `aᵢⱼ`: 1 if node vᵢ and node vⱼ are connected by a link; otherwise, 0
- `|V|`: Total number of nodes

**Rationale**: Degree centrality measures the local topological importance of the node. The greater it is, the more connected the node is and the more likely it is to be selected.

**Implementation**:
```python
def degree_centrality(node, graph):
    adjacency_matrix = graph.adjacency_matrix()
    degree = sum(adjacency_matrix[node])
    num_nodes = len(graph.get_all_nodes())
    return degree / (num_nodes - 1)
```

---

### 4. Closeness Centrality (CC)

**Equation 15:**

```
            |V| - 1
CC(vᵢ) = ───────────────
          ∑ d(vᵢ, vⱼ)
         i≠j
```

**Description**: Closeness centrality is a method of measuring the importance of a node from a global topological perspective. It is obtained by calculating the sum of the shortest paths from the node to all other nodes and taking the reciprocal.

**Variables**:
- `d(vᵢ, vⱼ)`: Length (hop count) of the shortest path between node vᵢ and node vⱼ
- `|V|`: Total number of nodes

**Rationale**: Nodes near the geometric center of the graph have higher closeness centrality and are better positioned for efficient slice provisioning.

**Implementation**:
```python
def closeness_centrality(node, graph):
    distances = graph.distance_matrix()[node]
    distance_sum = sum(d for d in distances if d > 0)
    num_nodes = len(graph.get_all_nodes())
    return (num_nodes - 1) / distance_sum if distance_sum > 0 else 0
```

---

## Combined Scoring Functions

### 5. Node Ranking Strategy

**Equation 16:**

```
S(vᵢ) = α × LR(vᵢ) × DC(vᵢ) + β × GR(vᵢ) × CC(vᵢ)
```

**Description**: Combined scoring function that integrates local resources, global resources, local topology attributes, and global topology attributes.

**Variables**:
- `α, β`: Weighting parameters for relative importance of local vs. global attributes
- Typically set to `α = β = 0.5` for balanced consideration

**Rationale**: This strategy systematically evaluates nodes by combining all four attributes to comprehensively assess node importance.

---

### 6. Slice Node Scoring

**Equation 17:**

```
S(vᵢˢ) = α × LR(vᵢˢ) × DC(vᵢˢ) + β × GR(vᵢˢ) × CC(vᵢˢ)
```

**Description**: Scoring function applied to slice nodes in the slice request to rank them for provisioning order.

**Usage**: Slice nodes are provisioned in descending order of their scores. Higher-scoring nodes are provisioned first.

---

### 7. Cooperative Provisioning Coefficient

**Equation 18:**

```
H(vᵢᴵ) = ∑ h(vᵢᴵ, vⱼᴵ)
         vⱼᴵ∈M(Adj(vˢ))
```

**Description**: The cooperative provisioning coefficient calculates the sum of hop counts of the shortest paths between a candidate physical node and all physical nodes already hosting neighbor slice nodes.

**Variables**:
- `h(vᵢᴵ, vⱼᴵ)`: Hop count of the shortest path between physical nodes vᵢᴵ and vⱼᴵ
- `M(Adj(vˢ))`: Set of physical nodes hosting all neighbor slice nodes of the current slice node vˢ

**Rationale**: This coefficient helps select physical nodes that are closer to already-mapped neighbors, resulting in shorter physical paths for slice links and better resource utilization.

---

### 8. Physical Node Scoring with Cooperative Provisioning

**Equation 19:**

```
             α × LR(vᵢᴵ) × DC(vᵢᴵ) + β × GR(vᵢᴵ) × CC(vᵢᴵ)
S(vᵢᴵ) = ─────────────────────────────────────────────────────
                         H(vᵢᴵ) + ε
```

**Description**: Scoring function for ranking candidate physical nodes, incorporating the cooperative provisioning coefficient in the denominator.

**Variables**:
- `ε`: Small constant (10⁻⁵) to prevent division by zero when H(vᵢᴵ) = 0

**Rationale**: Candidate physical nodes with smaller H values (closer to mapped neighbors) receive higher scores, improving link provisioning success.

**Implementation**:
```python
def score_physical_node(node, mapped_neighbors, graph, alpha=0.5, beta=0.5, epsilon=1e-5):
    lr = local_resource(node, graph)
    dc = degree_centrality(node, graph)
    gr = global_resource(node, graph)
    cc = closeness_centrality(node, graph)
    h = cooperative_provisioning_coefficient(node, mapped_neighbors, graph)

    numerator = alpha * lr * dc + beta * gr * cc
    denominator = h + epsilon
    return numerator / denominator
```

---

## Provisioning Constraints

### 9. Slice Node Mapping Constraint

**Equation 1:**

```
∑ xᵢᵏ = 1,    ∀vₖˢ ∈ Vˢ
vᵢᴵ
```

**Description**: Each slice node must be mapped to exactly one physical node.

**Variables**:
- `xᵢᵏ`: Binary variable indicating whether slice node vₖˢ is mapped to physical node vᵢᴵ

---

### 10. One-to-One Node Mapping Constraint

**Equation 2:**

```
∑ xᵢᵏ ≤ 1,    ∀vᵢᴵ ∈ Vᴵ
vₖˢ
```

**Description**: Each physical node can host at most one slice node from the same slice request (no co-hosting).

---

### 11. CPU Capacity Constraint

**Equation 3:**

```
∑ xᵢᵏ · c(vₖˢ) ≤ cₐ(vᵢᴵ),    ∀vᵢᴵ ∈ Vᴵ
vₖˢ
```

**Description**: The total CPU capacity allocated to slice nodes at a physical node cannot exceed its available CPU capacity.

**Variables**:
- `c(vₖˢ)`: CPU demand of slice node vₖˢ
- `cₐ(vᵢᴵ)`: Available CPU capacity of physical node vᵢᴵ

---

### 12. Location Constraint

**Equation 4:**

```
xᵢᵏ · dis(vₖˢ, vᵢᴵ) ≤ r(vˢ)
```

**Description**: The distance between the mapped location of a slice node and its expected deployment location cannot exceed the maximum allowed deviation.

**Variables**:
- `r(vˢ)`: Maximum deployment deviation allowed by slice node vˢ

---

### 13. Euclidean Distance Formula

**Equation 5:**

```
dis(vₖˢ, vᵢᴵ) = √[(x(vₖˢ) - x(vᵢᴵ))² + (y(vₖˢ) - y(vᵢᴵ))²]
```

**Description**: Euclidean distance between the expected location of a slice node and the actual location of a candidate physical node.

**Variables**:
- `x(v), y(v)`: Cartesian coordinates of node v

**Implementation**:
```python
def euclidean_distance(loc1, loc2):
    return math.sqrt((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2)
```

---

### 14. Bandwidth Constraint

**Equation 6:**

```
∑ yᵢⱼᵏˡ · b(eₖₗˢ) ≤ bₐ(eᵢⱼᴵ),    ∀eᵢⱼᴵ ∈ Eᴵ
eₖₗˢ
```

**Description**: The sum of bandwidth allocated to all slice links mapped to one physical link cannot exceed its available bandwidth.

**Variables**:
- `yᵢⱼᵏˡ`: Binary variable (1 if physical link eᵢⱼᴵ hosts slice link eₖₗˢ, 0 otherwise)
- `b(eₖₗˢ)`: Bandwidth demand of slice link eₖₗˢ
- `bₐ(eᵢⱼᴵ)`: Available bandwidth of physical link eᵢⱼᴵ

---

## Performance Metrics

### 15. Slice Acceptance Ratio (λ)

**Equation 7:**

```
           T
          ∑ Sₘ(t)
         t=0
λ = lim  ──────────
    T→∞    T
          ∑ S(t)
         t=0
```

**Description**: The ratio of the number of slices successfully provisioned to the total number of slice requests that arrive over a period of time.

**Variables**:
- `S(t)`: Total number of slice requests at time t
- `Sₘ(t)`: Number of slice requests provisioned successfully at time t
- `T`: Simulation time horizon

---

### 16. Provisioning Revenue

**Equation 8:**

```
REV(Gˢ, t) = ∑ c(vˢ) + ∑ b(eˢ)
             vˢ∈Vˢ    eˢ∈Eˢ
```

**Description**: The provisioning revenue of a slice request is the sum of CPU capacities of its nodes and bandwidths of its links.

**Note**: Assumes unit price of 1 for both CPU and bandwidth.

---

### 17. Long-term Average Provisioning Revenue (μ)

**Equation 9:**

```
          T
         ∑   ∑  REV(Gˢ, t)
        t=0 Gˢ∈Sₘ(t)
μ = lim ────────────────────
    T→∞         T
```

**Description**: The average revenue earned over time from successfully provisioned slices.

---

### 18. Provisioning Cost

**Equation 10:**

```
COST(Gˢ, t) = ∑ c(vˢ) + ∑ |L(pᴵ(eˢ))| · b(eˢ)
             vˢ∈Vˢ    eˢ∈Eˢ
```

**Description**: The provisioning cost includes node CPU costs and link bandwidth costs multiplied by hop counts.

**Variables**:
- `pᴵ(eˢ)`: Physical path hosting slice link eˢ
- `L(pᴵ(eˢ))`: Set of physical links in path pᴵ(eˢ)
- `|L(pᴵ(eˢ))|`: Hop count (number of physical links) in the path

**Rationale**: Longer physical paths consume more bandwidth resources across multiple links.

---

### 19. Provisioning Revenue-to-Cost Ratio (η)

**Equation 11:**

```
    REV           T
η = ──── = lim   ∑   ∑  REV(Gˢ, t)
    COST   T→∞  t=0 Gˢ∈Sₘ(t)
              ─────────────────────────
                T
               ∑   ∑  COST(Gˢ, t)
              t=0 Gˢ∈Sₘ(t)
```

**Description**: The ratio of total provisioning revenue to total provisioning cost, measuring resource utilization efficiency.

**Interpretation**: Higher η indicates more efficient use of physical network resources.

---

## Link Provisioning Strategy

### 20. minMaxBWUtilHops Strategy

**Equation 20:**

```
          (      bₐ(eᴵ) )
Γₚᴵ = max ( 1 - ────── ) × |L(pᴵ)|
          (      b₀(eᴵ) )
          eᴵ∈L(pᴵ)
```

**Description**: The strategy selects the physical path which has the minimum product of the maximum link bandwidth utilization and its hop count.

**Variables**:
- `bₐ(eᴵ)`: Available bandwidth of physical link eᴵ
- `b₀(eᴵ)`: Initial (total) bandwidth of physical link eᴵ
- `|L(pᴵ)|`: Hop count of physical path pᴵ
- `(1 - bₐ(eᴵ)/b₀(eᴵ))`: Bandwidth utilization of link eᴵ

**Rationale**:
1. Minimizes the maximum link utilization to avoid creating bottlenecks
2. Prefers paths with fewer hops to reduce bandwidth cost
3. Balances between path quality and path length

**Implementation**:
```python
def minmax_bw_util_hops(paths, physical_network):
    best_path = None
    min_gamma = float('inf')

    for path in paths:
        max_util = 0
        for link in path.links:
            available_bw = physical_network.get_available_bandwidth(link)
            initial_bw = physical_network.get_initial_bandwidth(link)
            utilization = 1 - available_bw / initial_bw
            max_util = max(max_util, utilization)

        hop_count = len(path.links)
        gamma = max_util * hop_count

        if gamma < min_gamma:
            min_gamma = gamma
            best_path = path

    return best_path
```

---

## Summary of Key Parameters

| Parameter | Symbol | Default Value | Description |
|-----------|--------|---------------|-------------|
| Local weight | α | 0.5 | Weight for local attributes (LR, DC) |
| Global weight | β | 0.5 | Weight for global attributes (GR, CC) |
| Division safety | ε | 10⁻⁵ | Prevents division by zero |
| K-shortest paths | k | 3 | Number of candidate paths |
| Unit price | - | 1 | Price per unit CPU/bandwidth |

---

## Algorithm Time Complexity

### Node Provisioning
**Complexity**: O(|Vᴵ||Eᴵ| + |Vᴵ|²)

- Closeness centrality calculation: O(|Vᴵ||Eᴵ| + |Vᴵ|²) [Dijkstra from each node]
- Other metrics: O(|Vᴵ| + |Eᴵ|)

### Link Provisioning
**Complexity**: O(k|Vᴵ|(|Eᴵ| + |Vᴵ|log|Vᴵ|))

- K-shortest paths (Yen's algorithm): O(k|Vᴵ|(|Eᴵ| + |Vᴵ|log|Vᴵ|))

### Overall Algorithm
**Complexity**: O(|Vᴵ||Eᴵ| + |Vᴵ|²) + O(k|Vᴵ|(|Eᴵ| + |Vᴵ|log|Vᴵ|))

**Result**: Polynomial time complexity ✓

---

## References

Li, X., Guo, C., Xu, J., Gupta, L., & Jain, R. (2019). Towards Efficiently Provisioning 5G Core Network Slice Based on Resource and Topology Attributes. *Applied Sciences, 9*(20), 4361.
