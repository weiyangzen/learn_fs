# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/testfake/FakeBlockStore.h

Purpose: Declares the strict in-memory fake blockstore used for tests.

Important APIs and types: `FakeBlockStore` implements `BlockStore` and stores `_blocks: unordered_map<BlockId, Data>`, `_used_dataregions_for_blocks`, and `_mutex`. It exposes `updateData` and `flushBlock` in addition to the abstract interface.

Control flow: Public behavior is implemented in the `.cpp`; helper methods create fake block handles and load optional blocks. Copy and assignment are disabled.

State and persistence behavior: In-memory map acts as backing persistence for fake blocks. The extra vector intentionally keeps old data regions alive to make tests less forgiving of memory misuse.

Dependencies and integration points: Used directly in tests and as the default base for `MockBlockStore`.

Risks: Because fake blocks copy data, behavior differs from a real memory-mapped or direct in-memory store. Tests relying on immediate visibility without flush should fail, by design. Concurrency safety depends on all map access taking `_mutex`; header exposes no guard for callbacks.

Test signals: Blockstore tests should use this to catch missing flushes and out-of-bounds writes.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/testfake/FakeBlockStore.h` completely for this pass (69 lines, 3113 bytes).
