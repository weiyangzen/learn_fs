# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/happiness_upload.py

## Purpose
Computes share placement for immutable uploads with "servers of happiness" goals. It uses max-flow matching to maximize unique server coverage, preserve read-only/existing allocations when useful, and distribute unmatched shares.

## Important APIs, Types, And Functions
Graph helpers: `bfs(graph, s)`, `augmenting_path_for(graph)`, and `residual_network(graph, f)` implement Edmonds-Karp max-flow machinery over adjacency-list graphs with unit capacities.

Placement helpers: `_reindex()`, `_flow_network()`, `_servermap_flow_graph()`, `_compute_maximum_graph()`, `_convert_mappings()`, `_calculate_mappings()`, `_extract_ids()`, and `_distribute_homeless_shares()`.

Public functions: `calculate_happiness(mappings)` returns the count of unique non-None peers in a share-to-peer map. `share_placement(peers, readonly_peers, shares, peers_to_shares)` returns `{share_num: peer_id}` for upload/renewal placement.

## Control Flow
`share_placement()` returns empty placement when no peers are writable/readable. It first computes mappings for read-only servers and their existing shares, preserving renewals where possible. It removes used peers/shares, builds a servermap for remaining existing allocations, computes a second max-flow mapping to preserve useful existing read-write placements, then maps remaining shares to remaining peers with a complete bipartite flow graph.

The three mapping sets are merged. Shares mapped to `None` are "homeless": `_distribute_homeless_shares()` first renews existing placements if the share already exists, then uses a priority queue to balance remaining homeless shares across read-write peers with the fewest assigned shares. Any still-None mappings are assigned by round-robin over writable peers.

`_compute_maximum_graph()` repeatedly finds augmenting paths in the residual network, updates the flow matrix, rebuilds residual graph/capacity, then derives share-to-peer assignments from residual edges.

## State And Persistence
All data structures are local and non-persistent. Inputs are sets and maps of peer/share IDs; outputs are placement decisions consumed by upload/server-selection code. Existing allocations in `peers_to_shares` are treated as renewals, not modified directly here.

## Dependencies And Integration Points
Uses `queue.PriorityQueue`. Upload/server-selection code calls `share_placement`; `encode.Encoder` later enforces happiness after remote failures with `happinessutil.servers_of_happiness`. The algorithm references `docs/specifications/servers-of-happiness.rst`.

## Risks And Edge Cases
The graph code assumes adjacency-list indices are dense and derived from `_reindex()`. `_servermap_flow_graph()` uses an `indexedShares` list built across peers without resetting inside the peer loop, which may intentionally or accidentally accumulate edges; tests should guard behavior. The final round-robin uses `peers - readonly_peers`; if that set is empty while None mappings remain, iteration would not yield. Placement uses sets, so deterministic order relies on sorted loops only in some phases.

## Test Signals
`src/allmydata/test/test_happiness.py` directly covers graph helpers, residual networks, servermap flow graphs, placement with read-only peers, existing allocations, homeless shares, and happiness calculation. Upload tests in `test_upload.py` and repair tests exercise integration with server selection and happiness failure messages.
