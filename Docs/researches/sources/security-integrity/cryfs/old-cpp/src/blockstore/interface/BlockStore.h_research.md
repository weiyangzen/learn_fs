# sources/security-integrity/cryfs/old-cpp/src/blockstore/interface/BlockStore.h

Purpose: Defines the abstract blockstore interface for creating, loading, overwriting, removing, enumerating, sizing, and flushing blocks.

Important APIs and types: `BlockStore` declares `createBlockId`, `tryCreate`, `load`, `overwrite`, `remove(id)`, `numBlocks`, `estimateNumFreeBytes`, `blockSizeFromPhysicalBlockSize`, `forEachBlock`, `flushBlock`, and provides default `remove(unique_ref<Block>)` and `create(data)`.

Control flow: `create(data)` loops generating IDs and calling `tryCreate` until an unused ID succeeds, copying data for each attempt. Default `remove(unique_ref<Block>)` captures the block ID, destroys the handle with `cpputils::destruct`, then removes by ID. Concrete stores implement all persistence behavior and optional load/create failures.

State and persistence behavior: Interface itself has no state. Implementations decide whether blocks are durable, cached, copied, flushed on destruction, or immediately written. `flushBlock` is the explicit hook for wrappers/caches to persist an open block.

Dependencies and integration points: Uses `Block`, `BlockId`, `boost::optional`, cpp-utils `unique_ref`, and `cpputils::Data`. It is the central contract implemented by fake, mock, parallel access, caching, rustbridge, and real stores.

Risks: `load` TODO says it should use optional semantics, but it already does; comments still mention nullptr. The infinite create loop assumes random ID collisions eventually stop and `tryCreate` failures only indicate existing IDs. Passing `Data` by value can copy unless callers move. Remove-by-handle destroys the block before removing by ID, which matters for implementations whose destructor flushes stale data.

Test signals: Concrete blockstore suites should test ID collision handling, create/load/overwrite/remove semantics, enumeration, free-byte estimates, physical/logical block sizing, and flush behavior.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/interface/BlockStore.h` completely for this pass (57 lines, 2001 bytes).
