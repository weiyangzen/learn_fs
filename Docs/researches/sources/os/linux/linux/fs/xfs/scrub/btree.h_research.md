# File Research: sources/os/linux/linux/fs/xfs/scrub/btree.h

## Role
Declares the generic btree scrub interface and its traversal state.

## Main Types and Interfaces
- `xchk_btree_rec_fn`: callback used by `xchk_btree` for caller-specific leaf record validation.
- `struct xchk_btree_key`: remembered key plus validity bit for ordering checks at each non-leaf level.
- `struct xchk_btree`: caller state (`sc`, `cur`, callback, owner info, private data) plus walker state (`lastrec`, deferred owner list, flexible `lastkey[]` array).
- `xchk_btree_sizeof`: computes the allocation size for `struct xchk_btree`, with one key-tracking slot per non-leaf level.
- Error and flag helpers mirror the implementation in `btree.c`.

## Dependencies
Requires XFS scrub context, btree cursor definitions, owner info, and kernel flexible-array sizing helpers.

## Notes
The flexible `lastkey[]` member must remain last. Consumers should allocate via `xchk_btree_sizeof(cur->bc_nlevels)` rather than stack-allocating the structure.
