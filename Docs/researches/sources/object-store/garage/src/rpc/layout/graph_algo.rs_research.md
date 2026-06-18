# sources/object-store/garage/src/rpc/layout/graph_algo.rs

Purpose: graph primitives and algorithms used by layout computation to assign partitions to nodes under replication, capacity, zone, and rebalance constraints.

Important APIs and types: `Vertex` models source/sink, partition upper/lower vertices, partition-zone vertices, and node vertices. `FlowEdge` and `WeightedEdge` back `Graph<FlowEdge>` and `Graph<WeightedEdge>`. `CostFunction` maps directed vertex pairs to costs. Public flow APIs include `add_edge`, `get_positive_flow_from`, `get_outflow`, `flow_upper_bound`, `compute_maximal_flow`, and `optimize_flow_with_cost`.

Control flow: `compute_maximal_flow` implements Dinic's algorithm over adjacency lists, first shuffling edges with deterministic seeded randomness to distribute assignments consistently across runs. It builds BFS levels, then iterative DFS paths, updating forward/reverse residual flows. `optimize_flow_with_cost` converts residual capacity into a weighted graph, finds negative cycles with bounded Bellman-Ford, and pushes one unit around each cycle until no improving cycle remains. `cycles_of_1_forest` extracts cycles from predecessor links.

State and persistence: graphs are in-memory only. Deterministic shuffle is important state behavior because `garage layout show` and actual application must agree.

Dependencies and integration: used from `layout/version.rs` for optimal partition size, candidate assignment, and rebalance minimization. Depends only on standard collections and `rand` seeded RNG.

Risks and test signals: correctness is algorithmic and error-prone: reverse-edge indices must stay valid after shuffling, capacities are `u64` but flows are `i64`, and bounded negative-cycle search assumes layout graph structure. Coverage comes through layout assignment tests rather than unit tests of graph internals.
