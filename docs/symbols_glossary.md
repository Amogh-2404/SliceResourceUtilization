# Symbols and Notation Glossary

Complete notation reference from "Towards Efficiently Provisioning 5G Core Network Slice Based on Resource and Topology Attributes" (Table 1).

## Physical Infrastructure (Substrate Network)

| Symbol | Description | Type |
|--------|-------------|------|
| G<sup>I</sup> | 5G core infrastructure topological graph | Graph |
| V<sup>I</sup> | Set of physical nodes | Set |
| E<sup>I</sup> | Set of physical links | Set |
| v<sup>I</sup> | A physical node | Node |
| v<sup>I</sup><sub>i</sub>, v<sup>I</sup><sub>j</sub> | Specific physical nodes | Node |
| e<sup>I</sup> | A physical link | Link |
| e<sup>I</sup><sub>ij</sub> | Physical link between nodes i and j | Link |

### Physical Node Attributes

| Symbol | Description | Type | Unit |
|--------|-------------|------|------|
| c<sub>0</sub>(v<sup>I</sup>) | Initial total CPU capacity of physical node | Real | CPU units |
| c<sub>a</sub>(v<sup>I</sup>) | Available CPU capacity of physical node | Real | CPU units |
| c<sub>u</sub>(v<sup>I</sup>) | Total CPU capacity allocated to slice nodes | Real | CPU units |
| loc(v<sup>I</sup>) | Location of physical node | Tuple | (x, y) coordinates |
| φ(v<sup>I</sup><sub>i</sub>, v<sup>I</sup><sub>j</sub>) | Euclidean distance between physical nodes | Real | Distance units |

### Physical Link Attributes

| Symbol | Description | Type | Unit |
|--------|-------------|------|------|
| b<sub>0</sub>(e<sup>I</sup>) | Initial total bandwidth of physical link | Real | Bandwidth units |
| b<sub>a</sub>(e<sup>I</sup>) | Available bandwidth of physical link | Real | Bandwidth units |
| b<sub>u</sub>(e<sup>I</sup>) | Total bandwidth allocated to slice links | Real | Bandwidth units |

### Physical Paths

| Symbol | Description | Type |
|--------|-------------|------|
| P<sup>I</sup> | Set of all loop-free physical paths | Set |
| P<sup>I</sup>(v<sup>I</sup><sub>i</sub>, v<sup>I</sup><sub>j</sub>) | Set of loop-free paths between two physical nodes | Set |
| p<sup>I</sup>(v<sup>I</sup><sub>i</sub>, v<sup>I</sup><sub>j</sub>) | A specific physical path between nodes i and j | Path |
| L(p<sup>I</sup>) | Set of links in physical path p<sup>I</sup> | Set |
| \|L(p<sup>I</sup>)\| | Hop count (number of links) in path | Integer |

---

## Slice Requests (Virtual Network)

| Symbol | Description | Type |
|--------|-------------|------|
| G<sup>S</sup> | 5G core network slice request topological graph | Graph |
| V<sup>S</sup> | Set of slice nodes | Set |
| E<sup>S</sup> | Set of slice links | Set |
| v<sup>S</sup> | A slice node | Node |
| v<sup>S</sup><sub>k</sub>, v<sup>S</sup><sub>l</sub> | Specific slice nodes | Node |
| e<sup>S</sup> | A slice link | Link |
| e<sup>S</sup><sub>kl</sub> | Slice link between slice nodes k and l | Link |

### Slice Node Attributes

| Symbol | Description | Type | Unit |
|--------|-------------|------|------|
| c(v<sup>S</sup>) | CPU capability required by slice node | Real | CPU units |
| loc(v<sup>S</sup>) | Expected deployed location of slice node | Tuple | (x, y) coordinates |
| r(v<sup>S</sup>) | Maximum deployment deviation allowed | Real | Distance units |

### Slice Link Attributes

| Symbol | Description | Type | Unit |
|--------|-------------|------|------|
| b(e<sup>S</sup>) | Bandwidth required by slice link | Real | Bandwidth units |

### Slice Request Properties

| Symbol | Description | Type | Unit |
|--------|-------------|------|------|
| SR<sub>i</sub> | The i-th slice request | Tuple | (G<sup>S</sup><sub>i</sub>, t<sup>a</sup><sub>i</sub>, t<sup>l</sup><sub>i</sub>) |
| t<sup>a</sup><sub>i</sub> | Arrival time of slice request i | Real | Time units |
| t<sup>l</sup><sub>i</sub> | Lifetime of slice request i | Real | Time units |

---

## Mapping Functions

| Symbol | Description | Type |
|--------|-------------|------|
| M(V) | Slice node mapping function | Function: V<sup>S</sup> → V<sup>I</sup> |
| M(E) | Slice link mapping function | Function: E<sup>S</sup> → P<sup>I</sup> |
| M(S) | Complete slice mapping function | Function: (V<sup>S</sup>, E<sup>S</sup>) → (V<sup>I</sup>, P<sup>I</sup>) |
| M(v<sup>S</sup>) | Physical node hosting slice node v<sup>S</sup> | Node |
| M(Adj(v<sup>S</sup>)) | Set of physical nodes hosting neighbors of v<sup>S</sup> | Set |

### Mapping Variables

| Symbol | Description | Type | Values |
|--------|-------------|------|--------|
| x<sup>k</sup><sub>i</sub> | Whether slice node k maps to physical node i | Binary | {0, 1} |
| y<sup>kl</sup><sub>ij</sub> | Whether slice link kl maps to physical link ij | Binary | {0, 1} |

---

## Node Ranking Metrics

### Resource Attributes

| Symbol | Description | Type |
|--------|-------------|------|
| LR(v<sub>i</sub>) | Local resource metric of node | Real |
| GR(v<sub>i</sub>) | Global resource metric of node | Real |

### Topology Attributes

| Symbol | Description | Type |
|--------|-------------|------|
| DC(v<sub>i</sub>) | Degree centrality of node | Real ∈ [0, 1] |
| CC(v<sub>i</sub>) | Closeness centrality of node | Real ∈ [0, 1] |
| a<sub>ij</sub> | Adjacency indicator (1 if connected, 0 otherwise) | Binary |
| d(v<sub>i</sub>, v<sub>j</sub>) | Shortest path distance between nodes | Integer |

### Combined Scoring

| Symbol | Description | Type | Default |
|--------|-------------|------|---------|
| S(v<sub>i</sub>) | Combined score of node v<sub>i</sub> | Real | - |
| α | Weight for local attributes (LR × DC) | Real | 0.5 |
| β | Weight for global attributes (GR × CC) | Real | 0.5 |
| H(v<sup>I</sup><sub>i</sub>) | Cooperative provisioning coefficient | Integer | ≥ 0 |
| h(v<sup>I</sup><sub>i</sub>, v<sup>I</sup><sub>j</sub>) | Hop count in shortest path | Integer | ≥ 0 |
| ε | Small constant to prevent division by zero | Real | 10<sup>-5</sup> |

---

## Link Provisioning

### K-Shortest Path

| Symbol | Description | Type | Default |
|--------|-------------|------|---------|
| k | Number of candidate shortest paths | Integer | 3 |

### minMaxBWUtilHops Strategy

| Symbol | Description | Type |
|--------|-------------|------|
| Γ<sub>p<sup>I</sup></sub> | Path evaluation metric | Real |
| (1 - b<sub>a</sub>/b<sub>0</sub>)<sub>max</sub> | Maximum link utilization in path | Real ∈ [0, 1] |

---

## Performance Metrics

### Acceptance and Provisioning

| Symbol | Description | Type |
|--------|-------------|------|
| λ | Slice acceptance ratio | Real ∈ [0, 1] |
| S(t) | Total number of slice requests at time t | Integer |
| S<sub>m</sub>(t) | Number of successfully provisioned requests at time t | Integer |

### Revenue and Cost

| Symbol | Description | Type | Unit |
|--------|-------------|------|------|
| REV(G<sup>S</sup>, t) | Provisioning revenue of slice at time t | Real | Revenue units |
| COST(G<sup>S</sup>, t) | Provisioning cost of slice at time t | Real | Cost units |
| μ | Long-term average provisioning revenue | Real | Revenue units / time |
| η | Provisioning revenue-to-cost ratio | Real | Dimensionless |

---

## Graph Theory Notation

| Symbol | Description | Type |
|--------|-------------|------|
| \|V\| | Number of nodes in graph | Integer |
| \|E\| | Number of links in graph | Integer |
| E(v<sub>i</sub>) | Set of adjacent links of node v<sub>i</sub> | Set |
| Adj(v<sub>i</sub>) | Set of adjacent nodes of node v<sub>i</sub> | Set |

---

## Constraint Notation

### Resource Constraints

| Expression | Description |
|------------|-------------|
| ∑<sub>v<sup>S</sup><sub>k</sub></sub> x<sup>k</sup><sub>i</sub> · c(v<sup>S</sup><sub>k</sub>) ≤ c<sub>a</sub>(v<sup>I</sup><sub>i</sub>) | CPU capacity constraint (Eq. 3) |
| ∑<sub>e<sup>S</sup><sub>kl</sub></sub> y<sup>kl</sup><sub>ij</sub> · b(e<sup>S</sup><sub>kl</sub>) ≤ b<sub>a</sub>(e<sup>I</sup><sub>ij</sub>) | Bandwidth constraint (Eq. 6) |

### Mapping Constraints

| Expression | Description |
|------------|-------------|
| ∑<sub>v<sup>I</sup><sub>i</sub></sub> x<sup>k</sup><sub>i</sub> = 1 | Each slice node maps to one physical node (Eq. 1) |
| ∑<sub>v<sup>S</sup><sub>k</sub></sub> x<sup>k</sup><sub>i</sub> ≤ 1 | One-to-one mapping (Eq. 2) |
| x<sup>k</sup><sub>i</sub> · dis(v<sup>S</sup><sub>k</sub>, v<sup>I</sup><sub>i</sub>) ≤ r(v<sup>S</sup>) | Location constraint (Eq. 4) |

---

## Distance and Location

| Symbol | Description | Formula |
|--------|-------------|---------|
| dis(v<sup>S</sup>, v<sup>I</sup>) | Euclidean distance between slice and physical node | √[(x(v<sup>S</sup>) - x(v<sup>I</sup>))² + (y(v<sup>S</sup>) - y(v<sup>I</sup>))²] |
| x(v), y(v) | Cartesian coordinates of node v | Real numbers |

---

## Time and Simulation

| Symbol | Description | Type | Unit |
|--------|-------------|------|------|
| t | Current simulation time | Real | Time units |
| T | Total simulation time / time horizon | Real | Time units |
| lim<sub>T→∞</sub> | Limit as time approaches infinity | Operator | - |

---

## Sets and Cardinality

| Notation | Description |
|----------|-------------|
| ∈ | Element of (membership) |
| ⊆ | Subset of |
| ∑ | Summation |
| Π | Product |
| \| \| | Cardinality (size of set) |
| ∀ | For all (universal quantifier) |

---

## Special Notation

### Superscripts
- <sup>I</sup> : Infrastructure / Physical network
- <sup>S</sup> : Slice / Virtual network
- <sup>a</sup> : Available
- <sup>u</sup> : Used / Allocated
- <sup>l</sup> : Lifetime

### Subscripts
- <sub>0</sub> : Initial value
- <sub>a</sub> : Available
- <sub>u</sub> : Used
- <sub>i</sub>, <sub>j</sub> : Physical node indices
- <sub>k</sub>, <sub>l</sub> : Slice node indices
- <sub>m</sub> : Mapped / Accepted

---

## Quick Reference Table

| Category | Key Symbols |
|----------|-------------|
| **Graphs** | G<sup>I</sup>, G<sup>S</sup>, V<sup>I</sup>, V<sup>S</sup>, E<sup>I</sup>, E<sup>S</sup> |
| **Resources** | c (CPU), b (bandwidth), loc (location) |
| **Subscripts** | <sub>0</sub> (initial), <sub>a</sub> (available), <sub>u</sub> (used) |
| **Metrics** | LR, GR, DC, CC, S (score) |
| **Parameters** | α, β, k, ε |
| **Performance** | λ, μ, η, REV, COST |
| **Mapping** | M, x<sup>k</sup><sub>i</sub>, y<sup>kl</sup><sub>ij</sub> |

---

## Usage Examples

### Physical Node CPU Constraint
```
Current: ca(viᴵ) = c0(viᴵ) - cu(viᴵ)
After allocation: cu(viᴵ) = cu(viᴵ) + c(vkˢ)
```

### Physical Link Bandwidth Constraint
```
Current: ba(eijᴵ) = b0(eijᴵ) - bu(eijᴵ)
After allocation: bu(eijᴵ) = bu(eijᴵ) + b(eklˢ) × |L(pᴵ)|
```

### Node Scoring Example
```
S(vi) = 0.5 × LR(vi) × DC(vi) + 0.5 × GR(vi) × CC(vi)
```

---

## Conventions

1. **Uppercase letters**: Sets and graphs (V, E, G, P)
2. **Lowercase letters**: Individual elements (v, e, c, b)
3. **Greek letters**: Parameters (α, β, λ, μ, η, ε, φ)
4. **Superscripts I/S**: Infrastructure/Slice distinction
5. **Subscripts i,j**: Physical node indices
6. **Subscripts k,l**: Slice node indices
7. **Parentheses ( )**: Function application
8. **Square brackets [ ]**: Set membership
9. **Angle brackets ⟨ ⟩**: Ordered tuple

---

*For detailed mathematical formulations, see [mathematical_formulations.md](mathematical_formulations.md)*
