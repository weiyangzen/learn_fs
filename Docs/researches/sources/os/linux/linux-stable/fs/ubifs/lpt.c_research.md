# File Research: sources/os/linux/linux-stable/fs/ubifs/lpt.c

## Summary
Implements UBIFS LEB Properties Tree (LPT) geometry, on-flash packing/unpacking, lazy in-memory loading, lookup, copy-on-write dirtying, authenticated hashing, scanning, and debug validation.

## Key APIs
- `ubifs_calc_lpt_geom()`, `ubifs_create_dflt_lpt()`.
- `ubifs_pack_pnode()`, `ubifs_pack_nnode()`, `ubifs_pack_ltab()`, `ubifs_pack_lsave()`.
- `ubifs_unpack_bits()`, `ubifs_unpack_nnode()`.
- `ubifs_read_nnode()`, `ubifs_get_nnode()`, `ubifs_get_pnode()`.
- `ubifs_pnode_lookup()`, `ubifs_lpt_lookup()`, `ubifs_lpt_lookup_dirty()`.
- `ubifs_lpt_calc_hash()`, `ubifs_lpt_init()`, `ubifs_lpt_scan_nolock()`.
- Debug entry: `dbg_check_lpt_nodes()`.

## Important Behavior
The file treats the LPT as a small self-contained wandering tree stored between the log and orphan area. It supports a small model, where the whole LPT can be rewritten, and a big model, where LPT garbage collection and the saved-LEB table are needed.

Geometry calculation derives tree height, pnode/nnode counts, packed bit widths, node sizes, ltab/lsave sizes, and minimum LPT space. Default-format creation iteratively chooses `lpt_lebs` and the big/small model, then writes pnodes, nnodes, optional lsave, and ltab while calculating the authenticated LPT hash.

Packed LPT nodes do not use normal UBIFS common headers. `pack_bits()` and `ubifs_unpack_bits()` encode tight bit fields plus CRC16. Pnodes store per-main-LEB free/dirty/index state; nnodes store child LPT locations; ltab stores LPT-area free/dirty state; lsave stores useful main-area LEB numbers for faster big-LPT mount.

Runtime lookup lazily reads nnodes and pnodes from flash, validates branch ranges and pnode free/dirty invariants, sets main-area LEB numbers, and inserts loaded pnode lprops into category heaps/lists. Dirty lookup performs COW if a cnode is currently being committed, preserving concurrent commit consistency.

`ubifs_lpt_scan_nolock()` walks lprops over a requested LEB range with wraparound support. Its callback may request path materialization into the in-memory tree and category structures.

## Dependencies
Depends on UBIFS lprops category helpers, UBI LEB read/change/unmap I/O, CRC16, authenticated hash helpers, LPT commit/free functions in `lpt_commit.c`, and debug helpers.

## Risks
Correctness depends on exact geometry and bit-width agreement with superblock/master metadata. Invalid LPT CRC/type/range checks abort mount. Dirty COW and category replacement are concurrency-sensitive around commit. The scanner can return `-ENOSPC` when no callback match is found before `end_lnum`.
