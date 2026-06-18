# File Research: sources/local-fs/mtd-utils/ubi-utils/ubinfo.c

## Purpose
Implements the `ubinfo` utility for printing general UBI subsystem information, per-UBI-device information, and per-volume information.

## Main Entry Points
- `parse_opt()` accepts device number, volume ID, volume name, `--all`, optional node path, help, and version options.
- `translate_dev()` converts a supplied UBI device or volume character node into `args.devn` and possibly `args.vol_id`.
- `get_vol_id_by_name()` resolves a volume name to a volume ID on a given UBI device.
- `print_vol_info()`, `print_dev_info()`, and `print_general_info()` format volume, device, and global UBI information.
- `main()` decides which report to print based on parsed selectors.

## Control Flow
Without arguments, the utility prints global UBI version, device count, control-device major/minor, and present devices. With `-a`, it expands global output into every UBI device and optionally every volume. With `-d`, it prints a selected device; with `-d` plus `-n` or `-N`, it prints a selected volume. If a node path is supplied, the utility probes whether it is a device node or volume node and derives the corresponding numeric selectors.

## Dependencies
Uses `libubi` inventory/probing APIs, `common.h` diagnostics/version helpers, and `ubiutils-common.h` byte formatting.

## Risks and Notes
`-N <volume name>` is resolved with the current `args.devn`; if the caller supplies a volume name without a device selector, the subsequent lookup targets device `-1` and fails through libubi rather than being caught as a front-end validation error. Some calls such as `print_vol_info()` in the direct volume path are not checked before returning through the success label, so an error there may be printed but not propagated as the process exit status.
