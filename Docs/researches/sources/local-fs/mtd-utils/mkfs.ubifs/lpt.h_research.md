# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/lpt.h

## Purpose
Declares the mkfs.ubifs LPT geometry and creation functions.

## Main API
- `calc_dflt_lpt_geom(struct ubifs_info *c, int *main_lebs, int *big_lpt)`.
- `create_lpt(struct ubifs_info *c)`.

## Dependencies
Requires `struct ubifs_info` to be visible from includers, normally via `mkfs.ubifs.h`.

## Risks and Notes
This header is intentionally minimal; all LPT structure layout details stay in `lpt.c` and UBIFS shared headers.
