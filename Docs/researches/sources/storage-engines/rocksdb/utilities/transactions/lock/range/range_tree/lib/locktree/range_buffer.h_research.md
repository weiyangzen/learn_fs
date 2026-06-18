# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/range_buffer.h

## Purpose
`range_buffer.h` declares an append-only key-range buffer used to store a transaction's lock ranges cheaply and iterate them later for release, STO migration, and escalation callbacks.

## Important APIs, Types, And Functions
`range_buffer` exposes `create()`, `append()`, `is_empty()`, `total_memory_size()`, `get_num_ranges()`, and `destroy()`. Nested `iterator` exposes constructors, `current()`, and `next()`. Nested `iterator::record` exposes left/right DBT accessors, serialized `size()`, `deserialize()`, and `get_exclusive_flag()`.

## Control Flow
The header defines a record format: fixed header followed by left and optional right key payloads. Equal endpoints are point records with a single key payload; full ranges store two payloads. Iteration walks variable-length records across memarena chunks.

## State And Persistence Behavior
State is one `memarena` plus an integer range count. It is transient and destroyed as a unit, not individually freed per range.

## Dependencies
It includes integer headers, DBT helpers, and `memarena`. The implementation also uses memory macros and string copy functions.

## Integration Points
`locktree` uses this for transaction-owned lock records, STO buffer, release lists, and per-transaction escalation output. Higher RocksDB layers may receive buffers through escalation callbacks to update tracked locks.

## Risks And Edge Cases
There is no random deletion or ownership transfer; misuse requires rebuilding. Iteration records expose DBTs pointing into arena memory, so consumers must copy if they outlive iteration. The 64 KiB key size limit is a hard invariant.

## Test Signals
Tests should validate round-trip append/iterate for point and range locks, shared/exclusive flags, infinite endpoints, empty buffers, and memory-size changes used by lock memory accounting.
