# File Research: sources/local-fs/mtd-utils/ubi-utils/ubirmvol.c

## Purpose
Implements the `ubirmvol` utility for removing a UBI volume by volume ID or volume name from a UBI device.

## Main Entry Points
- `parse_opt()` parses `--vol_id`, `--name`, help, version, and the required UBI device node.
- `param_sanity_check()` requires exactly one of volume ID or volume name.
- `main()` opens libubi, validates the node as a UBI device, resolves a name to a volume ID when needed, and calls `ubi_rmvol()`.

## Control Flow
The utility accepts one UBI device node and either `-n <id>` or `-N <name>`. For name-based removal, it first gets device information and then calls `ubi_get_vol_info1_nm()` to resolve the volume name to an ID on that UBI device. It then removes the volume by ID through libubi.

## Dependencies
Uses `libubi` for node probing, device metadata, name-based volume lookup, and volume removal. Uses `common.h` diagnostics and version printing.

## Risks and Notes
Name length is not locally validated, but lookup is delegated to libubi. Like the other UBI device mutators, this tool rejects volume character nodes and requires the parent UBI device node.
