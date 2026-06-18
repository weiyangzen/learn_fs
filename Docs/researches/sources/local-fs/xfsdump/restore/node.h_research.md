# File Research: sources/local-fs/xfsdump/restore/node.h

## Summary
Declares the persistent node pool abstraction used by restore tree code.

## Main Contents
- `nh_t` as a 32-bit node handle and `NH_NULL` sentinel.
- `node_init()` for creating a node pool inside an existing backing file.
- `node_sync()` for reconnecting to persisted node state.
- `node_alloc()`, `node_map()`, `node_unmap()`, and `node_free()`.

## Risks
Mapped node pointers are valid only until `node_unmap()` and may pin scarce windows while held.

Callers must pass a node size, alignment, and housekeeping-byte index compatible with `node.c`’s internal free-list and validation requirements.
