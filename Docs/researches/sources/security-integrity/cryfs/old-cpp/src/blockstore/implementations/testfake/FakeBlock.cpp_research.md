# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/testfake/FakeBlock.cpp

Purpose: Implements `FakeBlock`, a strict in-memory test block that works on a private copy and flushes changes back to `FakeBlockStore` only when dirty.

Important APIs and types: Defines constructor, destructor, `data`, `write`, `size`, `resize`, and `flush`. It uses `cpputils::Data`, `DataUtils::resize`, assertions, and `std::memcpy`.

Control flow: Constructor stores the owning store, shared data copy, and dirty flag. Destructor calls `flush`. `write` asserts the write fits within current size, copies bytes into the local data buffer, and marks dirty. `resize` replaces the data with a resized copy and marks dirty. `flush` writes data back to the store via `updateData` if dirty, then clears the flag.

State and persistence behavior: State is local copied block data and dirty flag. Persistence to the backing fake store occurs on flush/destruction; until then, other loads see the old backing data.

Dependencies and integration points: Created by `FakeBlockStore::makeFakeBlockFromData`. Used heavily as a stricter test double than a direct in-memory store.

Risks: Write bounds assertion uses `offset + size`, which can overflow despite the comment saying it checks overflow; the first conjunct only ensures offset is in range. Destructor flush means test failures or exceptions during update can occur at scope exit. Multiple FakeBlocks for the same ID can overwrite each other based on flush order.

Test signals: Tests should verify write bounds, dirty flush, resize behavior, destructor flush, and independent loaded copies.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/testfake/FakeBlock.cpp` completely for this pass (54 lines, 1284 bytes).
