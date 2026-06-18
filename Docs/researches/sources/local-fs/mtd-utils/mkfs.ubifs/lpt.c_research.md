# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/lpt.c

## Purpose
Calculates and writes the UBIFS Logical Properties Tree (LPT) area for a newly created UBIFS image.

## Main Entry Points
- `calc_dflt_lpt_geom()` iteratively determines the default number of LPT LEBs, main-area LEBs, and whether the filesystem needs the big LPT model.
- `create_lpt()` serializes pnodes, nnodes, optional lsave, and ltab data into LPT LEBs.

## Geometry Calculation
`do_calc_lpt_geom()` derives pnode and nnode counts, tree height, bit widths for space, LPT LEB number, offset, pnode count, and main LEB number fields. It then computes packed node sizes and total LPT size, adding expected per-LEB wastage and min-I/O alignment.

`calc_dflt_lpt_geom()` starts with minimum LPT LEBs and small-LPT assumptions, switches to big LPT if needed, and repeats until the computed geometry fits within the number of reserved LPT LEBs.

## Serialization
`pack_bits()` writes variable-width fields into byte streams. `pack_pnode()`, `pack_nnode()`, `pack_ltab()`, and `pack_lsave()` encode LPT records and prepend CRC-16 checksums. `create_lpt()` lays out pnodes first, then internal nnodes bottom-up, records root/head/ltab/lsave addresses in `struct ubifs_info`, maintains LPT LEB free/dirty accounting through `set_ltab()`, aligns writes to min I/O size, fills unwritten bytes with `0xff`, and emits buffers via `write_leb()`.

## Dependencies
Depends on UBIFS constants/types from `mkfs.ubifs.h`, `crc16()`, `fls()`/`do_div()` from `defs.h`, alignment macros, and the image writer `write_leb()`.

## Risks and Notes
The packing code assumes the geometry bit widths have already been calculated consistently. `create_lpt()` allocates temporary pnode/nnode/buffer/lsave objects and returns negative errno-style failures on allocation or write errors.
