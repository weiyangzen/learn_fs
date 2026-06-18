# File Research: sources/local-fs/mtd-utils/ubi-utils/ubimkvol.c

## Purpose
Implements the `ubimkvol` command-line utility for creating a UBI volume on an existing UBI device node.

## Main Entry Points
- `parse_opt()` parses volume ID, name, byte size, LEB count, max-available-size mode, alignment, and static/dynamic volume type.
- `param_sanity_check()` enforces that a volume name is present and exactly one size mode is selected.
- `main()` opens libubi, validates that the supplied node is a UBI device node, gathers device geometry, constructs `struct ubi_mkvol_request`, calls `ubi_mkvol()`, and prints the created volume summary.

## Control Flow
The utility requires one UBI device node plus a volume name and size. Size can be supplied directly in bytes/KiB/MiB via `ubiutils_get_bytes()`, by LEB count via `-S`, or as all available space via `-m`. For LEB-count sizing, it computes bytes from the device LEB size adjusted by the requested alignment. After creation, it queries the new volume by device number and assigned volume ID to report ID, LEB count, byte size, LEB size, type, name, and alignment.

## Dependencies
Depends on `libubi` for UBI probing, device info, volume creation, and volume info lookup. Uses local `common.h` diagnostics/version helpers and `ubiutils-common.h` byte parsing/printing helpers.

## Risks and Notes
`args.lebs` is an `int` but is assigned from `simple_strtoull()`, so very large values may truncate before later byte-size computation. Alignment is only checked as positive by this file; invalid geometry combinations are left for lower layers to reject. The max-available-size path uses `dev_info.avail_bytes` directly, while the LEB-count path adjusts usable bytes for alignment.
