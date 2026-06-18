# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/testfake/FakeBlock.h

Purpose: Declares `FakeBlock`, the block handle returned by `FakeBlockStore`.

Important APIs and types: Inherits `Block`, stores `FakeBlockStore*`, `shared_ptr<cpputils::Data>`, and `_dataChanged`. Public methods are destructor, `data`, `write`, `flush`, `size`, and `resize`.

Control flow: Method bodies are in the `.cpp`; copy and assignment are disabled.

State and persistence behavior: Holds a private data buffer shared only for handle lifetime tracking and flushes dirty data back to the store.

Dependencies and integration points: Used by `FakeBlockStore` and test code through the abstract `Block` interface.

Risks: Raw store pointer lifetime must outlive blocks. Dirty state is per handle, so concurrent handles for the same ID require careful flush ordering in tests.

Test signals: See `FakeBlock.cpp` and `FakeBlockStore` tests for behavior.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/testfake/FakeBlock.h` completely for this pass (39 lines, 841 bytes).
