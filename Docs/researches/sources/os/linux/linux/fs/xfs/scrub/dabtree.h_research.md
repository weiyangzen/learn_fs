# File Research: sources/os/linux/linux/fs/xfs/scrub/dabtree.h

## Role
Declares the DA btree scrub state and callback API.

## Main Types and Interfaces
- `struct xchk_da_btree`: embeds DA args, per-level hash and max-record tracking, DA state, scrub context, private callback data, valid DA block range, and current logical tree level.
- `xchk_da_btree_rec_fn`: callback type for leaf record validation.
- `xchk_da_process_error`, `xchk_da_set_corrupt`, `xchk_da_set_preen`: shared DA scrub helpers.
- `xchk_da_btree_hash` and `xchk_da_btree`: hash checker and full walker.

## Notes
The header contains a duplicate declaration of `xchk_da_set_preen`; it is harmless but redundant. Consumers use this interface for both directory and attribute btree validation.
