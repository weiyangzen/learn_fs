# File Research: sources/local-fs/mtd-utils/ubi-utils/ubiblock.c

## Role
CLI tool to create or remove a block device interface for a UBI volume.

## Main Behavior
- Parses create/remove operation and a UBI volume node.
- Opens libubi and probes the node to ensure it is a volume, not a UBI device.
- Opens the volume and calls either `ubi_vol_block_create` or `ubi_vol_block_remove`.
- Reports missing/unsupported UBI block functionality based on errno.

## Interfaces And Dependencies
- Uses `libubi`, `getopt_long`, and `common.h`.

## Notes
- The `case 'c'` intentionally falls through to `case 'r'` to set `args.node`.
- Long options and short options require an argument for create/remove, matching usage `--create /dev/ubi0_0`.
