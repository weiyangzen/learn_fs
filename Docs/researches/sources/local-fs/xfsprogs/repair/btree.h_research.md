# File Research: sources/local-fs/xfsprogs/repair/btree.h

## Purpose

`btree.h` declares the repair-local generic in-memory B-tree API for unsigned long keys and pointer values.

## Public API

The header declares:

- lifecycle: `btree_init`, `btree_destroy`, `btree_clear`
- state: `btree_is_empty`
- lookup: `btree_lookup`, `btree_find`
- cursor-relative lookup: `btree_peek_prev`, `btree_peek_next`, `btree_lookup_next`, `btree_lookup_prev`
- mutation: `btree_insert`, `btree_delete`, `btree_update_key`, `btree_update_value`
- optional `btree_print_stats` under `BTREE_STATS`

## Important Invariants

- The root type is opaque to callers.
- Values passed to insert/update must be non-null.
- Cursor-relative functions depend on a valid prior lookup/find operation.

## Research Notes

This API is intentionally small and repair-oriented. It exposes enough ordered-map behavior for repair subsystems without exposing node layout or balancing internals.
