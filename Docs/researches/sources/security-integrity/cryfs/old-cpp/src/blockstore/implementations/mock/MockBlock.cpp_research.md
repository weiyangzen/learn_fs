# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/mock/MockBlock.cpp

Purpose: Implements mutating operations for `MockBlock`, an access-counting wrapper around a real `Block`.

Important APIs and types: Defines `MockBlock::write` and `MockBlock::resize`.

Control flow: `write` records a write for this block ID in the owning `MockBlockStore`, then delegates to the base block. `resize` records a resize and delegates.

State and persistence behavior: Persistent behavior is that writes/resizes affect the base block exactly as before; additional in-memory counters in `MockBlockStore` record access patterns.

Dependencies and integration points: Used by `MockBlockStore` in performance and behavioral tests to assert how many blocks were touched.

Risks: Counter updates happen before delegation, so a failed underlying operation may still be counted. Thread safety depends on `MockBlockStore` locking.

Test signals: Tests should inspect `writtenBlocks` and `resizedBlocks` after operations through loaded/created mock blocks.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/mock/MockBlock.cpp` completely for this pass (18 lines, 494 bytes).
