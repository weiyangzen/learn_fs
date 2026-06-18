# File Research: sources/local-fs/mtd-utils/ubi-utils/ubirename.c

## Purpose
Implements the `ubirename` utility for atomically renaming one or more UBI volumes on a UBI device.

## Main Entry Points
- `get_vol_id()` scans present volumes on a device and resolves a volume name to its volume ID.
- `main()` validates argument pairing, opens libubi, validates the supplied node as a UBI device node, resolves all old names, builds `struct ubi_rnvol_req`, and calls `ubi_rnvols()`.

## Control Flow
The command expects a UBI device node followed by old/new name pairs. It rejects odd argument counts and more than the UBI rename limit. It probes the node to ensure it is not a volume node, reads device info to get the volume ID range, resolves each old name by scanning existing volumes, fills rename entries with volume ID and new name, sets the count, and submits the atomic rename request.

## Dependencies
Depends on `libubi` probing, device info, volume info, and atomic rename APIs. Uses local `common.h` diagnostic helpers.

## Risks and Notes
The limit check compares `argc` to `UBI_MAX_RNVOL + 2`, but each rename consumes two arguments after the node. This appears to cap the command below the documented maximum number of rename entries rather than allowing up to `2 * UBI_MAX_RNVOL` names. New volume names are copied with `strcpy()` into the libubi request entry without a local length check, relying on external structure sizing and lower-level validation.
