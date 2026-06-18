# sources/security-integrity/cryfs/old-cpp/src/blockstore/interface/Block.h

Purpose: Defines the abstract block handle interface for the legacy C++ blockstore layer.

Important APIs and types: `Block` declares virtual `data`, `write`, `size`, and `resize`, plus nonvirtual `blockId`. It stores a const `BlockId` initialized by protected constructor.

Control flow: Concrete implementations provide storage-specific data access and mutation. `blockId` returns the immutable ID held by the base.

State and persistence behavior: The base class only stores identity. Persistence and flush semantics are implementation-specific: fake blocks flush on destruction, wrappers forward, real stores may write immediately or lazily.

Dependencies and integration points: All C++ blockstores return `unique_ref<Block>` through `BlockStore`. Higher blob/filesystem layers use this as the unit of encrypted block data.

Risks: `data()` returns a raw pointer with lifetime and mutability semantics defined only by implementations. `write` and `resize` have no base-level bounds/error contract beyond implementation assertions. TODO notes a potential design change to make `Block` non-virtual and store a pointer to its blockstore for write-back.

Test signals: Every concrete block implementation and blockstore test validates this interface indirectly.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/interface/Block.h` completely for this pass (39 lines, 949 bytes).
