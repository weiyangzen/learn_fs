# sources/storage-engines/tikv/components/pd_client/src/lib.rs

## Purpose
`pd_client/src/lib.rs` is the public surface for the PD client crate. It re-exports client implementations and defines shared types, bucket statistics helpers, the main `PdClient` trait, constants, and small utility functions.

## Important APIs, Types, and Functions
- Re-exports include `RpcClient`, v2 `RpcClient`/`PdClient`, `Config`, `Error`, `FeatureGate`, `PdConnector`, and bucket stat utilities.
- `RegionStat` aggregates region heartbeat data, including peer state, traffic, approximate size/keys, query stats, CPU stats, and coprocessor details.
- `RegionInfo` pairs a `metapb::Region` with optional leader and derefs to `Region`.
- `BucketMeta` tracks bucket boundaries, sizes, region id/version/epoch and supports split/left-merge/total size plus heap sizing.
- `BucketStat` holds `Arc<BucketMeta>`, current protobuf stats, creation time, and methods to reset, merge, add flows, update write stats, ingest SST, split, merge, and clean a bucket.
- The public `PdClient` trait defines cluster bootstrap, store and region lookup, heartbeat streams, split/scatter/report operations, TSO, safe points, feature gate, min resolved ts, bucket reports, RU metrics, and config/meta operations.
- `take_peer_address` selects `peer_address` over `address`.
- `check_update_service_safe_point_resp` rejects unsafe service safe point requests when PD returns a higher minimal safe point.
- `RegionWriteCfCopDetail` tracks write-CF coprocessor iteration amplification.

## Control Flow
Most trait methods default to `unimplemented!`, defining an interface implemented by `client.rs`. `get_tso` delegates to `batch_get_tso(1)`. Bucket methods maintain parallel vectors in `BucketMeta` and protobuf stats, preserving split/merge alignment. Service safe point checking is a simple ttl/min-safe-point guard.

## State and Persistence Behavior
The file defines data structures used to report or modify PD's persistent cluster state, but local state is ordinary Rust structs. Bucket stats mutate in memory between reports. `BucketMeta` ordering compares epoch version first, then bucket version, which controls freshness decisions.

## Dependencies and Integration Points
The crate surface integrates with `kvproto` PD/meta/replication/resource-manager protobufs, futures boxed futures, TiKV heap sizing, time utilities, and transaction timestamps. It is consumed by raftstore, scheduling, resource control, GC, split/checker, and metadata paths.

## Risks
The trait is very broad, so mock clients must implement many methods or rely on panicking defaults. Bucket split/merge methods assert `idx != 0` and assume all stats vectors are aligned with metadata keys/sizes. `RegionWriteCfCopDetail::sub` can underflow if called with larger counters. Safe point checks only reject when ttl is nonzero and returned min exceeds requested point.

## Test Signals
Inline test `test_processed_key_0` validates MVCC amplification does not divide by zero. Other behavior is exercised by concrete client tests and downstream PD client users.
