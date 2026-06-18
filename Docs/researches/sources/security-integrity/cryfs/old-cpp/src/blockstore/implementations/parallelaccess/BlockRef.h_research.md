# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/BlockRef.h

Purpose: Defines `BlockRef`, the resource-reference wrapper used by `ParallelAccessBlockStore` to hand out block handles coordinated by `parallelaccessstore::ParallelAccessStore`.

Important APIs and types: `BlockRef` inherits both `blockstore::Block` and `ParallelAccessStore<Block, BlockRef, BlockId>::ResourceRefBase`. It wraps a raw `Block*` `_baseBlock`.

Control flow: Constructor copies the base block ID into the `Block` base and stores the raw pointer. `data`, `write`, `size`, and `resize` simply forward to `_baseBlock`.

State and persistence behavior: `BlockRef` does not own data persistence; it references a base block managed by the parallel access store. Mutations are applied to the base block.

Dependencies and integration points: Used internally by `ParallelAccessBlockStore` and the generic `parallelaccessstore` resource manager.

Risks: Stores the block ID twice, as noted by TODO. The raw pointer must remain valid while the ref exists; lifetime is delegated to `ParallelAccessStore`. There is no additional synchronization in `BlockRef` itself.

Test signals: Parallel access tests should validate forwarded reads/writes/resizes and correct exclusive/shared lifetime behavior through the store.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/BlockRef.h` completely for this pass (45 lines, 1172 bytes).
