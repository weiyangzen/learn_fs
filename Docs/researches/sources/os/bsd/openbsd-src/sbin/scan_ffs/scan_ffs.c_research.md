# File Research: sources/os/bsd/openbsd-src/sbin/scan_ffs/scan_ffs.c

This file implements `scan_ffs`, a raw-device scanner that searches for FFS superblocks and reports candidate filesystem offsets.

Key APIs:
- `main()`: parses `-l`, `-s`, `-v`, `-b begin`, `-e end`, opens the target device with `opendev()`, tightens pledge, and calls `ufsscan()`.
- `ufsscan()`: reads chunks of raw sectors, scans every 512-byte offset for `FS_MAGIC`, tracks adjacent primary/alternate superblock patterns, and prints candidate filesystems.
- `print_info()`: prints either disklabel-style lines or human-readable FFS location/size/mount/time data.
- `usage()`: command help.

Behavior and integration:
- Reads `SBSIZE * SBCOUNT` windows, with `SBCOUNT` fixed at 64.
- The “smart” mode skips ahead by the filesystem size after detecting a candidate.
- Label mode emits a disklabel-like `4.2BSD` partition line.
- Uses `pledge("stdio rpath disklabel")` before device open and `pledge("stdio")` after.

Risk notes:
- It only checks `FS_MAGIC` and nearby superblock spacing; findings are heuristic.
- The smart-skip adjustment is arithmetic-sensitive and assumes sane superblock size fields.
- FFS time output has an explicit 2038-era comment for old timestamp handling.
