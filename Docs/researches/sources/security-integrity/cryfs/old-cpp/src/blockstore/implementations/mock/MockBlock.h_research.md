# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/mock/MockBlock.h

Purpose: Declares `MockBlock`, a `Block` wrapper that forwards data access to a base block while informing `MockBlockStore` about writes and resizes.

Important APIs and types: Constructor takes `unique_ref<Block>` and `MockBlockStore*`. It overrides `data`, `write`, `size`, and `resize`, and exposes `releaseBaseBlock` for removal forwarding.

Control flow: Non-mutating methods forward directly to `_baseBlock`; mutating methods are defined in the `.cpp` to record counters first. `releaseBaseBlock` moves the wrapped block out.

State and persistence behavior: Holds a unique reference to the base block and a raw pointer to the owning store. It does not own persistence itself; the base block does.

Dependencies and integration points: Created by `MockBlockStore::tryCreate` and `load`. Friend access lets the store unwrap during flush/remove.

Risks: The raw store pointer must remain valid for the lifetime of every mock block. `releaseBaseBlock` leaves the wrapper moved-from and should only be used in controlled removal paths.

Test signals: Access-count tests should verify forwarding plus counter vectors for write/resize.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/mock/MockBlock.h` completely for this pass (47 lines, 1310 bytes).
