# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/ParallelAccessBlockStore.h

Purpose: Declares the parallel-access `BlockStore` wrapper.

Important APIs and types: `ParallelAccessBlockStore` owns `unique_ref<BlockStore> _baseBlockStore` and `ParallelAccessStore<Block, BlockRef, BlockId> _parallelAccessStore`. It implements the full `BlockStore` interface.

Control flow: Public methods are implemented in the `.cpp`; copy and assignment are disabled.

State and persistence behavior: Runtime state tracks opened blocks and delegates durable data to the base store. Removing or overwriting may update currently open block refs.

Dependencies and integration points: Consumers wrap concrete blockstores with this class when they need coordinated concurrent access. It relies on `BlockRef` and `ParallelAccessBlockStoreAdapter`.

Risks: TODO notes uncertainty about allowing parallel destruction of blocks, important because encrypted block destruction/flush may be expensive. Lifetime order between base store and parallel access store must remain valid.

Test signals: Validated by `parallelaccessstore-test` and `blockstore-test` paths using this implementation.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/parallelaccess/ParallelAccessBlockStore.h` completely for this pass (40 lines, 1620 bytes).
