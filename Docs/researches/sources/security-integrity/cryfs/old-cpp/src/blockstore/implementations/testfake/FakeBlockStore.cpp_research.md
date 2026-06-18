# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/testfake/FakeBlockStore.cpp

Purpose: Implements `FakeBlockStore`, a strict in-memory blockstore for unit tests that returns copies of block data and requires flush/destruction to persist modifications.

Important APIs and types: Implements `createBlockId`, `tryCreate`, `overwrite`, `load`, `_load`, `remove`, `makeFakeBlockFromData`, `updateData`, `numBlocks`, `estimateNumFreeBytes`, `blockSizeFromPhysicalBlockSize`, `forEachBlock`, and `flushBlock`.

Control flow: Blocks are stored in `_blocks` under a mutex. `tryCreate` emplaces a new ID and returns `_load`. `overwrite` inserts or replaces data and returns a loaded block. `_load` returns none on missing IDs or creates a `FakeBlock` with copied data. `remove` asserts exactly one entry was removed. `updateData` writes a copy back, inserting if absent. `flushBlock` dynamic-casts to `FakeBlock` and calls `flush`.

State and persistence behavior: Persistence is in-memory map state. Every loaded block receives a copy, and `_used_dataregions_for_blocks` keeps shared pointers to all data buffers ever issued to avoid allocator reuse hiding out-of-bounds bugs in tests. Dirty block flushes update the backing map.

Dependencies and integration points: Default base store for `MockBlockStore` and likely many blockstore/blobstore tests. Uses `BlockId::Random`, cpp-utils data helpers, assertions, memory-size utility, mutex, unordered_map, and Boost optional.

Risks: `forEachBlock` iterates `_blocks` without taking `_mutex`, unlike other methods, which is unsafe under concurrent mutation. `updateData` can reinsert a block that was removed if a stale dirty handle flushes later. `estimateNumFreeBytes` reports total system memory, not remaining fake capacity.

Test signals: Tests should validate create/load/overwrite/remove semantics, copy isolation before flush, flush persistence, numBlocks, wrong-type flush assertion, and stale-handle behavior.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/testfake/FakeBlockStore.cpp` completely for this pass (116 lines, 3380 bytes).
