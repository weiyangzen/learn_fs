# sources/object-store/garage/src/rpc/layout/test.rs

Purpose: unit tests and helper routines for partition assignment quality across changing cluster topologies.

Important functions: `check_against_naive` attempts a naive token-based assignment with partition size `S + 1` and returns whether the optimized algorithm beats that baseline. `show_stat` prints `ComputationStat`. `update_layout` stages node roles and zone redundancy. `test_assignment` applies four successive layout configurations and verifies consistency and baseline quality.

Control flow: the test creates a replication factor 3 history, stages roles/capacities/zones, applies staged changes, prints stats, checks `LayoutHistory::check`, and asserts that the partition size is not worse than the naive model. It then modifies capacities, zones, and redundancy, applying several more versions to exercise rebalance and reassignment behavior.

State and persistence: all layout state is in-memory. Node IDs are deterministic fixed-byte values derived from the loop index, making results reproducible.

Dependencies and integration: directly exercises `LayoutHistory::apply_staged_changes`, `LayoutVersion` assignment computation, CRDT staging updates, zone redundancy parameters, and `ComputationStat`.

Risks and test signals: the naive check is not a proof of optimality; comments document a counterexample for the naive algorithm. The test mainly guards gross regressions in assignment validity and capacity usage. It does not test layout-manager persistence, tracker propagation, or multi-node sync behavior.
