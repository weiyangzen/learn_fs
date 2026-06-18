# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/btree.h

## Role

Public interface and state definition for the generic XFS scrub btree walker.

## Key Definitions

- `xchk_btree_rec_fn` is the caller callback type for validating each leaf record.
- `struct xchk_btree_key` tracks the last key seen per internal level.
- `struct xchk_btree` stores scrub context, btree cursor, owner info, callback/private data, last leaf record, deferred owner checks, and flexible per-level key state.
- `xchk_btree_sizeof()` computes the heap allocation size for the flexible key array.

## API Surface

- Error and flag helpers: `xchk_btree_process_error`, `xchk_btree_xref_process_error`, `xchk_btree_set_corrupt`, `xchk_btree_xref_set_corrupt`, `xchk_btree_set_preen`.
- Main traversal API: `xchk_btree()`.

## Research Notes

The header keeps btree scrub callers decoupled from traversal internals while preserving enough callback context to validate btree-specific records.
