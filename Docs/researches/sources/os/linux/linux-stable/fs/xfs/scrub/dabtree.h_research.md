# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/dabtree.h

## Role

Interface and state definition for generic directory/attribute btree scrubbing.

## Key Definitions

- `struct xchk_da_btree` carries DA args, per-level hash/max-record state, DA state path, scrub context, private callback data, expected block range, and current tree level.
- `xchk_da_btree_rec_fn` is the callback type for leaf record validation.

## API Surface

- DA error and flag helpers: `xchk_da_process_error`, `xchk_da_set_corrupt`, `xchk_da_set_preen`.
- Hash and tree walkers: `xchk_da_btree_hash`, `xchk_da_btree`.

## Research Notes

There is a duplicated `xchk_da_set_preen` declaration, but it is harmless. This header is shared by directory and attribute scrubbers that need DA btree traversal.
