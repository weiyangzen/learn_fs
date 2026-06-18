# sources/object-store/garage/src/model/k2v/item_table.rs

## Purpose
This file defines the K2V item CRDT table. Each item stores dotted version-vector state per storage node, supports concurrent values and deletes, notifies poll subscribers, and maintains K2V index counters.

## Important APIs, types, and functions
Constants `ENTRIES`, `CONFLICTS`, `VALUES`, and `BYTES` name metrics. `K2VItem` stores `K2VItemPartition`, sort key, and a map of `K2VNodeId` to `DvvsEntry`. `DvvsEntry` has `t_discard` and timestamped `DvvsValue` list. `DvvsValue` is `Value(Vec<u8>)` or `Deleted`. `K2VItem::update`, `causal_context`, `values`, `with_raw_items`, `DvvsEntry::from_raw`, and CRDT merge implementations are central. `K2VItemTable` hooks counters and subscriptions. `ItemFilter` supports tombstone exclusion and conflicts-only queries.

## Control flow
Writes apply an optional causal context by raising each node's discard timestamp, discard obsolete values, choose a new local timestamp above both previous local time and provided node timestamp, and append the new value/delete. Merge combines node entries, merges timestamp-ordered value lists without duplicates, takes max discard time, and discards obsolete values. Table updates first adjust the index counter, then notify subscribers of new entries.

## State and persistence behavior
The initial table format stores DVVS state in replicated sharded metadata table `k2v_item`. A tombstone is an item whose visible values are all `Deleted`. Counters aggregate live entries, conflicts, value count, and byte totals by bucket and partition key. Partition hashing uses Blake2b over bucket UUID and partition key.

## Dependencies and integration points
It depends on Garage DB, table CRDTs, index counters, K2V causality and subscriptions. `GarageK2V` creates this table and its counters; `K2VRpcHandler` performs writes and polls; API handlers use filters for listing conflicts/data.

## Risks and edge cases
Visible values are deduplicated by value equality, so identical concurrent values collapse for clients while clocks still retain provenance. The merge assumes `values` are timestamp-sorted; malformed persisted state could violate it. Counter failures are logged but ignored. A delete is just another value unless its causal context discards earlier values, so clients must supply correct tokens to overwrite.

## Test signals
`test_dvvsentry_merge_simple` covers a basic discard/merge case. More tests should cover concurrent values, deletes with/without causal context, tombstone filtering, counter counts, partition hash stability, and subscriber notifications.
