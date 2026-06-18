# sources/object-store/garage/src/model/helper/locked.rs

## Purpose
This file implements serialized helper operations for mutating bucket aliases, key-local aliases, key permissions, and key deletion. It is the coordination layer that updates both sides of denormalized relationships in bucket, key, and alias tables.

## Important APIs, types, and functions
`LockedHelper` holds `&Garage` and an optional `tokio::sync::MutexGuard`. It exposes `bucket()` and `key()` helper accessors; global alias methods `set_global_bucket_alias`, `unset_global_bucket_alias`, `purge_global_bucket_alias`; local alias methods `set_local_bucket_alias`, `unset_local_bucket_alias`, `purge_local_bucket_alias`; `set_bucket_key_permissions`; `delete_key`; and `repair_aliases`.

## Control flow
Alias setters validate bucket names, fetch relevant bucket/key/alias rows, reject collisions, compute an alias timestamp via `increment_logical_clock_2`, then write both authoritative and reverse-map records with the same timestamp. Unset operations refuse to leave a bucket with no aliases and remove both sides. Purge operations are tolerant cleanup paths for deletion/repair. Permission updates fetch both bucket and key, advance timestamps against both current permission maps, and write matching permission CRDT entries to both tables. `delete_key` purges local aliases, removes bucket permissions, then marks the key deleted. `repair_aliases` runs a DB transaction that scans buckets, alias table, and key table, removes aliases pointing to deleted buckets, reconstructs reverse maps, and queues table updates.

## State and persistence behavior
All public mutation methods write replicated metadata tables. The mutex is local to one Garage process and does not serialize concurrent API nodes. Timestamps are used as causality barriers so CRDT merges converge across paired table updates. `repair_aliases` writes directly through table queue-insert APIs inside a DB transaction and logs each repaired inconsistency.

## Dependencies and integration points
It depends on bucket alias validation/table, bucket/key helpers, bucket/key tables, permission CRDTs, Garage DB transactions, table utilities, and logical clocks. Admin bucket/key APIs should acquire `Garage::locked_helper` before calling these methods.

## Risks and edge cases
The file explicitly documents unresolved cross-node races for bucket/alias mutations. Partial failures between paired inserts can leave reverse maps stale until repair. Unalias operations reject removing the last alias but races can invalidate that check. `delete_key` iterates existing aliases/permissions and performs nested async mutations, so failures can leave a partially cleaned key. `repair_aliases` trusts local DB state and should be run carefully on inconsistent clusters.

## Test signals
No direct tests in this subset. High-value tests should cover global/local alias collision, last-alias rejection, timestamp monotonicity, deleted bucket/key permission denial, partial repair scenarios, and concurrent same-alias operations.
