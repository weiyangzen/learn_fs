# sources/storage-engines/rocksdb/table/block_based/index_reader_common.cc

## Purpose
Implements common cache-aware primary index block access for block-based table index readers.

## Important APIs, Types, And Functions
`BlockBasedTable::IndexReaderCommon::ReadIndexBlock` reads the table's index block through `RetrieveBlock`. `GetOrReadIndexBlock` reuses an already held block or loads it lazily. `EraseFromCacheBeforeDestruction` evicts the cached index block when requested.

## Control Flow
`ReadIndexBlock` records `read_index_block_nanos`, asserts inputs, gets `rep->index_handle`, and retrieves a `Block_kIndex` with decompression and block-cache lookup enabled. `GetOrReadIndexBlock` returns an unowned value when the reader already has the block; otherwise it uses table cache settings. Destruction-time erasure either resets a cached entry if this reader has the last ref or asks the table to erase the index handle from cache.

## State And Persistence Behavior
No persistent state is modified. The code manages `CachableEntry<Block>` references and controls cache eviction policy for index blocks.

## Dependencies And Integration Points
Depends on `block_cache.h`, `BlockBasedTable::RetrieveBlock`, perf timers, block cache lookup context, and the table representation's index handle/decompressor/options. It is shared by hash, binary, partitioned, and other index readers.

## Risks And Edge Cases
Index-block read failures must be propagated to iterators so table reads do not silently ignore index corruption or IO failures. Cache erasure must not invalidate blocks still referenced elsewhere. Lazy loading assumes the table remains alive.

## Test Signals
Covered indirectly by table open, iterator, cache pinning, block cache, and index reader tests. Perf metrics can show read path regressions.
