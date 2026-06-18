# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/range_buffer.cc

## Purpose
`range_buffer.cc` implements a compact arena-backed serialization format for transaction-owned key ranges, including exclusive/shared flag storage and point-range compaction.

## Important APIs, Types, And Functions
It implements `record_header` infinity helpers and initialization, iterator record accessors/deserialization, iterator traversal, `create()`, `append()`, `is_empty()`, `total_memory_size()`, `get_num_ranges()`, `destroy()`, `append_range()`, and `append_point()`.

## Control Flow
`append()` stores one copy if endpoints are equal, otherwise stores left and right payloads after a header. `record_header::init()` records infinity flags and key sizes. Iteration uses `memarena::chunk_iterator`; `current()` deserializes the record at the current chunk offset, and `next()` advances by the last record size, moving chunks as needed.

## State And Persistence Behavior
The buffer owns all serialized range bytes in a `memarena` and resets wholesale on `destroy()`. DBT records returned by an iterator point into the current serialized record and are valid only while that record object remains in scope.

## Dependencies
It depends on DBT helpers, memory/assert macros, `memarena`, and fixed-width integer types. It assumes key payload sizes fit in 16-bit header fields.

## Integration Points
Transactions and STO mode use range buffers as lock ownership lists. `locktree::release_locks()` iterates them to release locks, and escalation callbacks receive per-transaction buffers describing replacement ranges.

## Risks And Edge Cases
`MAX_KEY_SIZE` is enforced with invariants, not recoverable errors. Header layout is implicitly serialized in memory and has a commented-out size assertion. Infinite point ranges and right-key-size-zero point records require careful deserialization.

## Test Signals
Range acquisition/release, STO migration, dump/status, and escalation all consume range buffers. Focused tests should cover finite range, finite point, infinite endpoints, chunk transitions, exclusive flag preservation, and maximum key size.
