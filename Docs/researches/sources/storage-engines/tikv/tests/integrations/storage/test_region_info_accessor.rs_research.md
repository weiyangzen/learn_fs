# sources/storage-engines/tikv/tests/integrations/storage/test_region_info_accessor.rs

## Purpose
This file tests raftstore's `RegionInfoAccessor` and `RegionInfoProvider` query behavior over a cluster whose keyspace is split into known contiguous regions.

## Important APIs, Types, and Functions
`prepare_cluster` writes keys, splits at `k1`, `k3`, `k5`, `k7`, and `k9`, and returns the expected region list. Tests create accessors through `post_create_coprocessor_host` and call `seek_region`, `get_regions_in_range`, `get_top_regions`, `find_region_by_key`, scheduler `RegionInfoQuery::RaftStoreEvent`, and `RegionActivity`.

## Control Flow
Each test starts a three-node cluster, captures one accessor per node from the coprocessor host creation hook, prepares the split layout, then queries every node's accessor. Seek tests verify traversal from empty, boundary, interior, and high keys. Range tests cover unbounded and bounded ranges. Top-region tests inject coprocessor write stats for each region and validate leader-side top-region population. Find-by-key tests check boundary and tail lookup.

## State, Persistence, and Dependencies
State is the accessor's in-memory region collection, raftstore leader tracking, and injected region activity metrics. It depends on PD/client region stat types, coprocessor hooks, and `HandyRwLock` for checking leader sets.

## Integration Points, Risks, and Test Signals
The tests integrate region metadata updates from raftstore with query APIs used by GC, scheduling, and diagnostics. Signals are exact region vector equality for deterministic ranges and non-empty top regions on leaders. Risk is the fixed sleep used to wait for raftstore updates after splits.
