# File Research: sources/os/bsd/openbsd-src/sbin/disklabel/editor.c

## Purpose
Implements the interactive `disklabel(8)` partition editor. It manages label mutation, undo state, OpenBSD area bounds, free-space discovery, auto-allocation policy, fstab mountpoint naming, size parsing, and partition alignment.

## Key Behavior
- `editor()` is the command loop. Commands include add, delete, modify, change size, set bounds, auto-partition, reset to defaults, write, quit, undo, restore original, save to file, print, show manual, and edit disklabel UID.
- Keeps three disklabel/mountpoint snapshots: original, last, and temporary undo buffers. If a command makes no effective change, undo state is restored.
- Ensures a raw `c` partition exists and covers the disk if absent.
- Refuses to start when existing partitions overlap unless overlaps can be resolved interactively by disabling one side.
- `editor_allocspace()` and allocation helpers apply OpenBSD default layouts (`alloc_big`, `alloc_medium`, `alloc_small`, `alloc_stupid`) or parsed custom auto-allocation tables.
- Auto-allocation picks the largest free chunk, assigns fstypes from mountpoint semantics (`swap`, `raid`, `/path`), and adjusts swap/var sizing based on physical memory.
- `editor_resize()` supports resizing auto-allocated FFS/swap layouts and repacks subsequent partitions.
- `free_chunks()`, `sort_partitions()`, `max_partition_size()`, and `editor_countfree()` provide the editor’s free-space model within `starting_sector` and `ending_sector`.
- `getuint64()`, `parse_sizespec()`, `apply_unit()`, `parse_sizerange()`, and `parse_pct()` parse sizes, ranges, percentages, relative changes, and units.
- `alignpartition()` centralizes offset/size rounding and overlap checks.
- `mpsave()` writes fstab entries, sorting mountpoints so parents precede children and optionally using DUID device names.

## Interfaces And Dependencies
- Depends on global state declared in `extern.h`: `lab`, `dkname`, `specname`, `fstabfile`, `mountpoints`, flags, display helpers, and `writelabel()`.
- Uses OpenBSD disklabel macros and structures from `<sys/disklabel.h>`.
- Uses UFS/FFS constants for fragment/block defaulting.
- Uses `DIOCGPDINFO` to reload prototype/default label data.

## Notes
This file is the behavioral center of `disklabel` editing. It mixes UI prompting, storage geometry policy, fstab generation, and disklabel structure mutation in one module.
