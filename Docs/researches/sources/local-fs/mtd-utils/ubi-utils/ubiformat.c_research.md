# File Research: sources/local-fs/mtd-utils/ubi-utils/ubiformat.c

## Role
Destructive CLI tool to format MTD devices for UBI and optionally flash a UBI image.

## Main Behavior
- Parses geometry overrides, VID offset, no-volume-table mode, flash image/stdin, image size, erase counter override, UBI version, image sequence, yes/quiet/verbose.
- Opens libmtd, validates MTD metadata, writeability, subpage constraints, and VID offset.
- Refuses to format an MTD device currently attached to UBI.
- Scans eraseblocks with `ubi_scan` to preserve/infer erase counters and detect bad/empty/corrupted/non-UBI blocks.
- Prompts before overwriting non-UBI data or questionable erase-counter state unless `--yes`.
- Formats eraseblocks by erasing, writing EC headers, reserving two good PEBs for layout volume, and writing an empty volume table unless disabled.
- When flashing an image, rewrites EC headers with new image sequence and selected erase counter, writes image PEBs, handles write failures by torturing/marking bad blocks, then formats the remaining blocks.

## Interfaces And Dependencies
- Uses `libmtd`, `libubi`, `libscan`, `libubigen`, UBI media headers, CRC helpers, and `ubiutils-common`.
- Calls MTD operations: erase, write, mark bad, torture, and bad-block checks.
- Uses `ubigen_info_init`, `ubigen_init_ec_hdr`, `ubigen_create_empty_vtbl`, and `ubigen_write_layout_vol`.

## Notes
- Consecutive bad-block marking is capped by `MAX_CONSECUTIVE_BAD_BLOCKS`.
- `--image-seq` is documented and parsed in a `case 'Q'`, but `Q` is missing from both `long_options` and the getopt option string in this file.
- `flash_image()` has an unreachable `goto out_close` after a `return sys_errmsg(...)` in the unaligned-image-size branch.
