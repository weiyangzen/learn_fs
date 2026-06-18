# Research: sources/storage-engines/wiredtiger/test/catch2/wrappers/block_mods.h

## sources/storage-engines/wiredtiger/test/catch2/wrappers/block_mods.h

Purpose: Header declaring the `block_mods` test wrapper for `WT_CKPT_BLOCK_MODS`.

Important API: class `block_mods` exposes constructor/destructor, `get_wt_block_mods`, private `init_block_mods`, and private `_block_mods` storage.

Control flow/state: no implementation flow in the header, but the contract is RAII ownership of the internal WT checkpoint block modifications structure. `get_wt_block_mods` returns a mutable pointer for test code.

Dependencies/integration: includes `wt_internal.h`, so consumers get full internal type definitions. Risks include exposing a mutable pointer that callers can populate inconsistently or with memory not compatible with the destructor. Test signals are indirect through tests using an initialized and automatically freed WT structure.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/block_mods.h -->
