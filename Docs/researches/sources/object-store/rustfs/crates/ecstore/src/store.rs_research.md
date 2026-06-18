# sources/object-store/rustfs/crates/ecstore/src/store.rs

## Purpose
Defines `ECStore`, the top-level erasure-coded object store implementing storage, bucket, object, list, multipart, heal, namespace locking, and admin traits. This file wires public trait methods to handler modules and exposes accessors for global configuration and service singletons during migration.

## Important APIs, Types, And Functions
Important types are `ECStore`, `PoolErr`, `PoolObjInfo`, `PoolAvailableSpace`, and `ServerPoolsAvailableSpace`. Helper functions include `has_xlmeta_files`, `enqueue_transition_after_write`, and `should_enqueue_transition_immediately`. Trait impls delegate to `handle_*` methods in `store/{bucket,heal,init,list,multipart,object,peer,rebalance}.rs`.

## Control Flow
S3-style operations enter through trait methods and are routed to handler methods. Successful writes, copies, and multipart completes pass through `enqueue_transition_after_write`, which schedules lifecycle transition and expiry for non-internal buckets. Admin APIs call handler methods for backend and storage info. Accessor impls return process-global config, endpoints, region, tier manager, notification system, bucket metadata system, host, port, and address.

## State And Persistence Behavior
`ECStore` owns pool routers, peer system, pool and rebalance metadata locks, decommission cancellation tokens, migrated local disk maps, tier config manager, event notifier, and a bucket monitor. This file itself mostly coordinates state; persistence occurs in handler modules and delegated pools/sets.

## Dependencies And Integration Points
It is the integration hub for bucket metadata, lifecycle queues, notification, disk endpoints, remote peers, store initialization, tiering, object metadata, S3 DTOs, locking, and storage admin traits.

## Risks
The file mixes current source-of-truth globals with new per-store fields, so migration boundaries must remain clear. `enableObjcetLockConfig` is misspelled but consistently referenced. `has_xlmeta_files` recursively scans local files and can be expensive for large buckets. Trait delegation makes behavior depend on many submodules.

## Test Signals
Tests cover storage-info helpers, local disk lookup/cache backfill, transition suppression for internal metadata buckets, and pool available-space filtering. Handler-specific behavior is tested in submodules.
