# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/main_grow.c

This file implements the `gfs2_grow` command, which expands an existing mounted GFS2 filesystem after its underlying device has grown.

Main behavior:
- Parses options: help, quiet/verbose, test mode, version, skip discard, and developer-only override device size.
- Opens a mounted GFS2 filesystem and its backing device.
- Reads device info and superblock.
- Mounts the GFS2 metafs.
- Opens the metafs `rindex` file.
- Reads existing resource groups from rindex.
- Calculates current filesystem end and growth size.
- Plans new resource groups with topology-derived alignment from blkid.
- Optionally discards the new device range.
- Writes new resource group headers/bitmaps to the new portion.
- Appends new rindex entries to the live metafs `rindex` file.
- Handles test mode by planning without changing filesystem data.

Important helpers:
- `rgrps_init()` probes blkid topology and initializes aligned rgrp planning.
- `filesystem_size()` derives filesystem end from the last resource group.
- `initialize_new_portion()` creates and writes new resource groups.
- `fix_rindex()` appends new rindex entries and truncates partial writes when possible.
- `open_rindex()` opens the metafs rindex path.

Integration role:
- Uses libgfs2 geometry, constants, superblock, resource group planning/writing, and mount helpers.
- Uses metafs helpers to safely access GFS2 system files while mounted.

Risk notes:
- Directly mutates on-disk resource groups and the mounted filesystem's rindex.
- Partial rindex write handling is careful but still high risk.
- `devflags` is computed before option parsing sets `test`, so test-mode read-only intent may not apply as written.
- `lgfs2_rgrps_write_final()` is called even in paths where test mode skipped individual writes.
- Discard errors are ignored by `initialize_new_portion()`.
