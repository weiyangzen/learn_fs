# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/mock/MockBlockStore.h

Purpose: Implements a `BlockStore` wrapper that counts block operations for tests, especially performance tests that assert a feature only loads/writes/removes a small number of blocks.

Important APIs and types: `MockBlockStore` wraps another `BlockStore`, defaulting to `testfake::FakeBlockStore`. It overrides the full `BlockStore` interface and exposes `resetCounters`, `createdBlocks`, `loadedBlocks`, `removedBlocks`, `resizedBlocks`, `writtenBlocks`, and `distinctWrittenBlocks`.

Control flow: Creation increments created count, delegates to base `tryCreate`, and wraps successful blocks in `MockBlock`. Loading increments loaded count and wraps. `overwrite` increments written count and delegates directly. `remove(id)` increments removed count and delegates. `remove(unique_ref<Block>)` requires a `MockBlock`, unwraps its base block, and delegates. `flushBlock` requires a `MockBlock` and flushes the underlying base block.

State and persistence behavior: Operation counters are protected by a mutex and persist in memory until reset. Actual block data and persistence behavior belong to the base store.

Dependencies and integration points: Uses `FakeBlockStore`, `MockBlock`, cpp-utils `unique_ref`, dynamic pointer moves, assertions, and Boost optional. It is a test double for blockstore users.

Risks: `overwrite` returns the base store's block directly rather than wrapping it, so subsequent writes/resizes through that returned block will not be counted as `MockBlock` operations. Counter increments can occur even if the delegated operation returns none or fails. `distinctWrittenBlocks` sorts by raw block ID bytes and assumes binary length.

Test signals: Tests should verify operation vectors/counts, reset behavior, distinct written block calculation, unwrap/remove paths, and wrong-store assertions in `remove`/`flushBlock`.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/mock/MockBlockStore.h` completely for this pass (163 lines, 6397 bytes).
