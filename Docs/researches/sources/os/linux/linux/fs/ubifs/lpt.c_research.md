# File Research: sources/os/linux/linux/fs/ubifs/lpt.c

## Role

Implements UBIFS LEB Properties Tree (LPT) geometry, default creation, packed on-flash encoding, lazy read/lookup, dirty copy-on-write lookup, authenticated hashing, range scanning, and debug validation.

## Key APIs

- `ubifs_calc_lpt_geom()`, `ubifs_create_dflt_lpt()`
- `ubifs_pack_pnode()`, `ubifs_pack_nnode()`, `ubifs_pack_ltab()`, `ubifs_pack_lsave()`
- `ubifs_unpack_bits()`, `ubifs_unpack_nnode()`
- `ubifs_read_nnode()`, `ubifs_get_nnode()`, `ubifs_get_pnode()`
- `ubifs_pnode_lookup()`, `ubifs_lpt_lookup()`, `ubifs_lpt_lookup_dirty()`
- `ubifs_lpt_calc_hash()`, `ubifs_lpt_init()`, `ubifs_lpt_scan_nolock()`
- Debug entry: `dbg_check_lpt_nodes()`

## Important Behavior

The file treats the LPT as a miniature wandering tree stored between the log and orphan areas. It supports a small model, where the whole LPT can be rewritten, and a big model, where LPT garbage collection and the saved-LEB table are needed.

Geometry calculation derives tree height, pnode/nnode counts, packed bit widths, node sizes, ltab/lsave sizes, and minimum LPT space. Default-format creation iteratively chooses `lpt_lebs` and big/small model, then writes pnodes, nnodes, optional lsave, and ltab while calculating the authenticated LPT hash.

Packed LPT nodes do not use normal UBIFS common headers. `pack_bits()` and `ubifs_unpack_bits()` encode tight bit fields plus CRC16. Pnodes store per-main-LEB free/dirty/index state; nnodes store child LPT locations; ltab stores LPT-area free/dirty state; lsave stores useful main-area LEB numbers for faster big-LPT mount.

Runtime lookup lazily reads nnodes and pnodes from flash, validates branch ranges and pnode free/dirty invariants, sets main-area LEB numbers, and inserts loaded pnode lprops into category heaps/lists. Dirty lookup performs COW if a cnode is currently being committed, preserving commit consistency while allowing new lprops changes.

`ubifs_lpt_calc_hash()` walks pnodes, packs each pnode, and hashes them for authenticated mounts. `lpt_check_hash()` compares the calculated hash with the master-node LPT hash.

`ubifs_lpt_scan_nolock()` scans lprops across a requested LEB range with wraparound support. Its callback may request that the current path be materialized into the in-memory LPT and category structures.

## Dependencies

Depends on UBIFS lprops category helpers, UBI LEB read/change/unmap I/O, CRC16, authenticated hash helpers, LPT commit/free functions in `lpt_commit.c`, and debug helpers.

## Research Notes

Correctness depends on exact agreement between LPT geometry, superblock/master metadata, and packed bit widths. CRC/type/range failures abort mount. Dirty COW and category replacement are concurrency-sensitive around commit.
