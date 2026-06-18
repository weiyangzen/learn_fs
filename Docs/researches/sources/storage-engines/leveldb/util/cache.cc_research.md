# sources/storage-engines/leveldb/util/cache.cc

## Purpose
`cache.cc` implements the sharded LRU cache used primarily for table data blocks.

## Important APIs, Types, and Functions
It defines `LRUHandle`, `HandleTable`, `LRUCache`, `ShardedLRUCache`, and `NewLRUCache`. Public cache operations include insert, lookup, release, erase, prune, total charge, value access, and id generation.

## Control Flow
Each entry has reference counts for clients and cache residency. `Lookup` refs an entry and moves it to in-use. `Release` unrefs and moves unpinned cached entries back to LRU. `Insert` allocates a handle, inserts into the hash table, evicts duplicate keys, and evicts oldest unpinned LRU entries until usage fits capacity. `Erase` removes from hash/cache but deletion waits for external handles to release. The sharded cache hashes keys across 16 shards.

## State, Persistence, and Integration
State is in-memory only: per-shard hash table, in-use list, LRU list, capacity, usage, mutexes, and global id counter. `Table::BlockReader` uses `NewId` and block offsets as cache keys and registers release cleanup on iterators.

## Risks and Test Signals
Unreleased handles cause destructor assertions and pin memory beyond capacity. Charges must approximate memory use for eviction. Tests cover hit/miss, replacement, erase, pinning, eviction, oversized in-use sets, heavy charges, pruning, zero capacity, and id uniqueness.
