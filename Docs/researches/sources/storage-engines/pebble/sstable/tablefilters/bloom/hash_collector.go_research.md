# sources/storage-engines/pebble/sstable/tablefilters/bloom/hash_collector.go

## Purpose
Provides a pooled block-based collector for 32-bit Bloom filter hashes.

## Important APIs, Types, And Functions
`hashCollector` stores count, last hash, current block, and block slice. `hashBlockLen` is 16384. `Init`, `Add`, `NumHashes`, `Blocks`, and `Reset` manage collection and iteration. `hashBlockPool` reuses block memory.

## Control Flow
`Add` skips consecutive duplicate hashes, obtains a new block when needed, and appends the hash. `Blocks` yields all full blocks and the final partial block through an `iter.Seq`. `Reset` returns blocks to the pool and reinitializes the collector.

## State And Persistence Behavior
State is transient during filter construction. Consecutive duplicate suppression changes the generated filter only for adjacent duplicate filter keys.

## Dependencies And Integration Points
Used by normal and adaptive Bloom writers plus simulations. Depends only on Go `iter` and `sync.Pool`.

## Risks And Edge Cases
`Blocks` is documented as invalid when empty. Pool misuse or missing reset could retain memory. The collector deduplicates only adjacent equal hashes, which matches sorted table write behavior but is not global deduplication.

## Test Signals
Covered indirectly by Bloom filter construction, adaptive policy, and simulation tests.
