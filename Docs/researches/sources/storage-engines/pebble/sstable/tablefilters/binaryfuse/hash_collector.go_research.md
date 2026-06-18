# sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/hash_collector.go

## Purpose
Provides a pooled block-based collector for 64-bit key hashes used while building binary fuse table filters.

## Important APIs, Types, And Functions
`hashCollector` tracks `numHashes`, `lastHash`, current block, and a slice of pooled `hashBlock`s. `hashBlockLen` is 8192. `Init`, `Add`, `NumHashes`, `Blocks`, and `Reset` are the primary methods; `hashBlockPool` reuses block allocations.

## Control Flow
`Add` skips consecutive duplicate hashes, allocates a new pooled block when the current block fills, writes the hash, and advances counters. `Blocks` returns an `iter.Seq` over full blocks and the final partial block. `Reset` returns blocks to the pool and reinitializes inline block-slice storage.

## State And Persistence Behavior
State is transient writer memory. Consecutive duplicate suppression affects the constructed filter by avoiding redundant adjacent keys, matching sorted SSTable key insertion patterns.

## Dependencies And Integration Points
Used by the binary fuse table filter writer and `buildFilter`. Depends only on Go `iter` and `sync.Pool`.

## Risks And Edge Cases
`Blocks` must not be called on an empty collector, as documented. Reset must return all blocks exactly once to avoid leaks or aliasing. Only consecutive duplicate hashes are removed, not all duplicates.

## Test Signals
Covered indirectly by filter build/end-to-end tests. No direct unit test targets block iteration or reset.
