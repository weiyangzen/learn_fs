# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/ParallelAccessBlockStore.cpp

Purpose: Implements a `BlockStore` decorator that coordinates concurrent access to block handles through `parallelaccessstore::ParallelAccessStore`.

Important APIs and types: Implements `createBlockId`, `tryCreate`, `load`, `overwrite`, both `remove` overloads, `numBlocks`, `estimateNumFreeBytes`, `blockSizeFromPhysicalBlockSize`, `forEachBlock`, and `flushBlock`. It uses `ParallelAccessBlockStoreAdapter`, `BlockRef`, `unique_ref`, and Boost optional.

Control flow: Construction owns the base store and creates an adapter for the parallel access store. `tryCreate` refuses creation if the ID is already opened, delegates base creation, then registers the new block with the parallel access store. `load` delegates to `_parallelAccessStore.load`. `overwrite` uses `loadOrAdd`: if a block is already open, resize/write into it; otherwise create/overwrite in the base store. `remove(unique_ref<Block>)` unwraps a `BlockRef` and removes it through the parallel access store; `remove(id)` removes by ID. Read-only metadata methods delegate to base store. `flushBlock` unwraps `BlockRef` and flushes the base block.

State and persistence behavior: The wrapper's runtime state is the base blockstore plus the parallel-access manager's open-resource registry. Persistence remains the base store's responsibility, but overwrite/remove behavior is coordinated with currently open refs.

Dependencies and integration points: Sits between higher blockstore users and any concrete base store to prevent unsafe simultaneous access. It integrates with the separate `parallelaccessstore` library.

Risks: `tryCreate` first checks `isOpened`, but base creation can still fail if the ID exists closed in the base store. The overwrite lambda captures `data` by reference and writes into an already-open block before returning it. Correctness depends on `ParallelAccessStore` enforcing the intended locking/lifetime semantics. Wrong block type in `remove`/`flushBlock` asserts.

Test signals: Parallel access tests should cover duplicate open/create refusal, load sharing/exclusion, overwrite of opened and unopened blocks, removal by ID/ref, base metadata delegation, and flush forwarding.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/ParallelAccessBlockStore.cpp` completely for this pass (96 lines, 3226 bytes).
