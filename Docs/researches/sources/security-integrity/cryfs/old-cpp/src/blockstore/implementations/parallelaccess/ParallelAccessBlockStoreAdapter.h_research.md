# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/ParallelAccessBlockStoreAdapter.h

Purpose: Adapts the `BlockStore` interface to the generic `ParallelAccessBaseStore<Block, BlockId>` interface expected by `parallelaccessstore`.

Important APIs and types: `ParallelAccessBlockStoreAdapter` stores a raw `BlockStore*` and implements `loadFromBaseStore`, `removeFromBaseStore(unique_ref<Block>)`, and `removeFromBaseStore(BlockId)`.

Control flow: Each method forwards directly to the underlying base blockstore.

State and persistence behavior: Holds no ownership and no independent persistence. All state changes occur in the base blockstore.

Dependencies and integration points: Constructed by `ParallelAccessBlockStore` with `_baseBlockStore.get()` and used internally by `ParallelAccessStore`.

Risks: The raw pointer must remain valid for the adapter lifetime. There is no null check or synchronization here; the owning wrapper must provide lifetime and concurrency context.

Test signals: Indirect signals are successful parallel access load/remove behavior and base-store side effects.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/ParallelAccessBlockStoreAdapter.h` completely for this pass (39 lines, 1117 bytes).
