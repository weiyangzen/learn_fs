# sources/storage-engines/rocksdb/include/rocksdb/utilities/db_ttl.h

## Purpose
Declares `DBWithTTL`, a `StackableDB` wrapper that appends creation timestamps to values and removes expired entries during compaction.

## Important APIs, Types, And Functions
`DBWithTTL::Open` has single-CF and multi-CF overloads, accepting a default TTL or per-column-family TTL vector. `CreateColumnFamilyWithTtl`, `SetTtl`, `SetTtl(ColumnFamilyHandle*)`, and `GetTtl` manage TTL behavior.

## Control Flow, State, And Persistence
Writes through the wrapper store timestamp-suffixed values. Compaction checks timestamp plus TTL against current time and drops expired entries. Reads and iterators can still return expired entries until compaction sees them. TTL timestamps are persisted inside values, while TTL configuration is runtime wrapper state.

## Dependencies And Integration Points
Depends on `DB` and `StackableDB`. It integrates with column-family creation, compaction filters, read-only opens, and normal DB read/write paths.

## Risks And Edge Cases
Opening a TTL-created DB through plain `DB::Open` exposes timestamp-suffixed values and disables expiration. Non-positive TTL behaves as infinity. Small TTL values can make most or all data eligible for deletion after compaction. Read-only mode does not remove expired entries.

## Test Signals
Cover compaction-driven expiry, reads before compaction, multi-CF TTLs, runtime TTL changes, non-positive TTLs, read-only opens, and plain DB reopen incompatibility.
