# File Research: sources/local-fs/mtd-utils/ubi-utils/ubirsvol.c

## Purpose
Implements the `ubirsvol` utility for resizing a UBI volume by ID or name.

## Main Entry Points
- `parse_opt()` parses volume ID, volume name, byte size, LEB-count size, help, version, and UBI device node.
- `param_sanity_check()` requires exactly one volume selector and exactly one size selector.
- `main()` opens libubi, validates the UBI device, resolves the target volume, converts LEB count to bytes when requested, and calls `ubi_rsvol()`.

## Control Flow
The command takes a UBI device node, either `-n` or `-N`, and either `-s` byte size or `-S` LEB count. It probes the node, gets UBI device information, resolves the volume info by name or ID, then resizes by bytes. If the user supplied LEB count, the byte target is `vol_info.leb_size * args.lebs`.

## Dependencies
Uses `libubi` probing, device info, volume info, and resize APIs. Uses `common.h` diagnostics/version helpers and `ubiutils-common.h` byte parsing.

## Risks and Notes
If `ubi_probe_node()` returns a negative error other than the volume-node case, the code reports the error but does not jump to cleanup, so it continues into `ubi_get_dev_info()` on a node already known to have failed probing. `args.lebs` is an `int` loaded from `simple_strtoull()`, so very large LEB counts can truncate. The LEB-to-byte multiplication also uses integer-sized `vol_info.leb_size` before assignment to `long long`.
