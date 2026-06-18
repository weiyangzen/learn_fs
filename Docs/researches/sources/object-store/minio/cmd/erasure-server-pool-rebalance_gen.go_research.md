# sources/object-store/minio/cmd/erasure-server-pool-rebalance_gen.go

## Purpose
This generated file supplies tinylib/msgp serialization code for rebalance state, metric enum values, and per-pool stats. It is the binary body used by `rebalanceMeta.save` and `rebalanceMeta.load` after the `rebalance.bin` header.

## Important APIs, Types, and Functions
Generated methods cover `rebalSaveOpts`, `rebalStatus`, `rebalanceInfo`, `rebalanceMeta`, `rebalanceMetric`, `rebalanceMetrics`, `rebalanceStats`, and `rstats`. Each type gets `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize`.

Enum-like types serialize as uint8 values. `rebalanceInfo` uses keys `startTs`, `stopTs`, and `status`. `rebalanceMeta` uses `stopTs`, `id`, `pf`, and `rss`. `rebalanceStats` uses `ifs`, `ic`, `bus`, `rbs`, `bu`, `ob`, `no`, `nv`, `bs`, `par`, and `inf`.

## Control Flow
Streaming decoders read headers and switch by map key, allocating slices as needed and preserving capacity when possible. Pointer slices such as `PoolStats` and `rstats` support nil elements and lazily allocate `rebalanceStats` values on decode.

Marshalers write deterministic maps or arrays into caller-provided buffers grown with `msgp.Require`. Unknown fields are skipped in both streaming and byte-slice decode paths.

## State and Persistence Behavior
The file defines how operation IDs, stopped time, percent-free goals, bucket queues, completed buckets, counters, participation flags, and pool status are persisted. Missing fields default to zero values, and unknown fields are skipped, allowing additive changes but not semantic migrations.

Nil pointer support in `rebalanceMeta.PoolStats` matters because callers must handle possible nil stats entries defensively. Most handwritten code assumes initialized entries after `initRebalanceMeta` or `updateRebalanceStats`.

## Dependencies, Risks, and Test Signals
The only direct dependency is `github.com/tinylib/msgp/msgp`. It integrates with `rebalanceMeta.loadWithOpts`, `rebalanceMeta.saveWithOpts`, and `erasure-server-pool-rebalance_gen_test.go`.

Manual edits would be overwritten. Any change to msg tags or field types can break compatibility with existing `rebalance.bin` files unless migration logic is added. Generated tests use zero values, so populated arrays, nil pointer entries, non-empty bucket queues, and status transitions are not asserted directly.
