# sources/object-store/garage/src/model/k2v/rpc.rs

## Purpose
This file implements K2V-specific RPCs for routing writes and long-poll reads to the storage nodes responsible for each K2V partition. It keeps vector clocks small by generating write timestamps on a responsible storage node rather than at arbitrary API ingress nodes.

## Important APIs, types, and functions
`K2VRpc` includes insert, batch insert, poll item, poll range, and response variants. `InsertedItem` carries partition/sort/context/value. `K2VRpcHandler` owns `System`, item table, a mutex-protected local timestamp tree, endpoint, and subscription manager. Public methods are `new`, `insert`, `insert_batch`, `poll_item`, and `poll_range`. Internal methods handle insert/batch, `local_insert`, item/range polling, and range scans.

## Control flow
`insert` computes storage nodes for the partition hash and sends `InsertItem` to all candidates with quorum 1. `insert_batch` groups items by identical responsible node set and sends batch RPCs concurrently. Insert handling serializes local timestamp updates with a mutex, calls `update_entry_with`, advances the local timestamp stored under `b"timestamp"`, and propagates changed items through the item table. `poll_item` sends to all responsible nodes with read quorum and merges returned items until timeout. `poll_range` decodes/restricts the seen marker, sends individual calls to all nodes, waits for quorum plus a short extra delay or timeout, merges returned items, updates the seen marker, and returns `None` only when a previous marker existed and no new items were found.

## State and persistence behavior
The local timestamp tree `k2v_local_timestamp` persists each node's K2V logical time. Item updates persist through `k2v_item`. Poll subscriptions are transient in memory and wake local RPC handlers when table updates arrive. Range seen markers are client-provided/returned strings and not persisted server-side.

## Dependencies and integration points
This module depends on Garage RPC endpoints, request strategies, table replication, table local stores, DB transactions, K2V causality/seen/sub/item modules, and helper errors. It integrates with `GarageK2V` initialization and K2V API request handlers.

## Risks and edge cases
Insert quorum 1 means writes are accepted after one responsible node timestamps them, relying on table replication afterward. If the chosen node fails before propagation, availability/consistency depends on table durability. `poll_range_read_range` breaks on the first item outside `range.matches`; this is correct for end bounds but can prematurely stop for a prefix filter if the start point is not prefix-aligned. Long polls use local subscriptions and can miss events only if subscription timing and initial scan are wrong; the code subscribes before scanning when a seen marker exists. Invalid seen markers map to bad-request helper errors.

## Test signals
No direct tests here, but previous Garage K2V integration tests likely exercise batch, item, range, and poll flows. Focused tests should cover quorum error thresholds, range prefix scanning, timeout behavior, seen-marker shrinking, local timestamp monotonicity, and batch grouping.
