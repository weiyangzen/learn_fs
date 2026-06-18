# sources/storage-engines/tikv/components/tikv_util/src/store/mod.rs

## Purpose
Defines the `store` utility module boundary and re-exports peer, query-stat, and region helper APIs under a single namespace.

## Important APIs, Types, and Functions
- Submodules: `peer`, `query_stats`, and `region`.
- Re-exports peer lookup/construction/removal helpers, `QueryStats` and `is_read_query`, and region range/store-membership helpers.

## Control Flow
There is no runtime control flow outside re-export wiring. Tests construct regions and peers to validate re-exported region membership helpers.

## State and Persistence Behavior
No module-level state is kept.

## Dependencies and Integration Points
Depends on submodules and `kvproto::metapb::Region` in tests. It is the import convenience layer for TiKV store-related utilities.

## Risks
API changes in submodules are exposed through this facade. Tests mostly cover region helpers, not every re-export.

## Test Signals
Tests validate `region_on_same_stores` across voter/learner/witness-like combinations and `region_on_stores` behavior with empty and non-empty target store lists.
