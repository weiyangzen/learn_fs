# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/partitioned_counter.h

## Purpose
Declares a high-throughput counter abstraction designed for frequent increments and infrequent reads by partitioning counts per thread.

## Important APIs, Types, And Functions
The C API defines opaque `PARTITIONED_COUNTER` and functions `create_partitioned_counter`, `destroy_partitioned_counter`, `increment_partitioned_counter`, `read_partitioned_counter`, `partitioned_counters_init`, and `partitioned_counters_destroy`.

## Control Flow
This header only declares behavior. Comments describe the intended flow: increments update thread-local state without a shared lock or atomic operation; reads sum live thread-local counters and a dead-thread aggregate populated by pthread-key destructors.

## State And Persistence Behavior
Counters are in-memory, monotonic 64-bit values. No persistence is involved.

## Dependencies And Integration Points
`status.h` can allocate partitioned counters for `STATUS_PARCOUNT` rows. Locktree status counters are exposed through RocksDB lock manager status APIs.

## Risks And Edge Cases
Reads may be slightly stale by design. Overflow is caller-prohibited. Because this file only declares the API, link-time availability of the implementation is required when status rows actually allocate partitioned counters.

## Test Signals
Expected tests include increment/read correctness, thread teardown aggregation, performance comparisons, and init/destroy ordering around static objects.
