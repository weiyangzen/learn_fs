# File Research: sources/local-fs/mtd-utils/ubi-utils/mtdinfo.c

## Role
CLI tool for printing MTD device information and optional UBI layout projections.

## Main Behavior
- Parses `--all`, `--ubi-info`, `--map`, `--help`, and `--version`.
- Opens libmtd and prints general MTD subsystem information.
- Prints per-device metadata: name, type, eraseblock size/count, min I/O size, subpage size, OOB size, region count, major/minor, bad-block support, and writeability.
- Computes default UBI VID/data offsets and LEB size with `ubigen_info_init` when requested.
- Can print erase region maps with locked and bad-block status.

## Interfaces And Dependencies
- Uses `libmtd`, `libubigen`, and `ubiutils-common` formatting helpers.
- Uses MTD ioctls through libmtd helpers.

## Notes
- `--map` requires a concrete MTD node, not `--all`.
- The “Additional erase regions” print uses `mtd.oob_size` instead of `mtd.region_cnt`, which appears suspicious.
