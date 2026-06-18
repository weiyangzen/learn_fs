# File Research: sources/os/linux/linux-stable/fs/hpfs/ea.c

## Purpose

Handles HPFS extended attributes stored in fnodes, external sector runs, or anode-backed storage.

## Main Entry Points

- `hpfs_ea_ext_remove()`
- `hpfs_read_ea()`
- `hpfs_get_ea()`
- `hpfs_set_ea()`

## Control Flow And State

EA lookup first scans fnode-resident EAs, then external EAs referenced by `ea_secno` and `ea_size_l`. Indirect EAs are read through the sector/anode pointer encoded in the EA value. `hpfs_set_ea()` updates existing EAs only when the size matches; otherwise it appends a new EA to fnode storage if it fits, migrates fnode EAs to external storage if needed, and grows or relocates external sector runs.

## Dependencies

Uses EA read/write helpers from `anode.c`, allocation helpers, fnode layout accessors, and HPFS global metadata rules.

## Risks

The code explicitly cannot resize existing EAs and contains rarely used fallback paths for large external EA growth. EA-anode creation is commented out, so fragmented growth relocates data instead. Corrupt EA length/name fields can stop reads or removals with filesystem errors.
