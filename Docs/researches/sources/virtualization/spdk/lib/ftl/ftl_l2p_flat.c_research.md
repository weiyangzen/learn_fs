# File Research: sources/virtualization/spdk/lib/ftl/ftl_l2p_flat.c

## Purpose
Implements the simple flat in-memory L2P backend, backed directly by the L2P metadata buffer.

## Behavior
- `ftl_l2p_flat_init()` allocates a small backend object and points `l2p_flat->l2p` at the L2P metadata buffer.
- `set` and `get` store/load packed FTL addresses using `ftl_addr_store()` and `ftl_addr_load()`.
- `pin` and `unpin` only assert range validity; all entries are already resident.
- `clear` fills the buffer with `FTL_ADDR_INVALID` and persists metadata.
- `restore` and `persist` forward to `ftl_md_restore()`/`ftl_md_persist()`.
- `trim`, `process`, `halt`, and `resume` are no-ops; `is_halted()` always returns true.

## Dependencies
Uses FTL L2P/core/band/utils/flat header and address packing utilities.
