# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/lufs.c

## Purpose

`lufs.c` is the top-level UFS logging control file. It enables and disables UFS logging, allocates/frees log extents, reconstructs in-core log state at mount/remount, provides the logging strategy hook for buffer I/O, initializes kstats/caches, and manages log header identity generation.

## Main Interfaces

Important routines include `lufs_snarf`, `lufs_unsnarf`, `lufs_enable`, `lufs_disable`, `lufs_read_strategy`, `lufs_write_strategy`, `lufs_strategy`, `lufs_hd_genid`, and `lufs_init`. Static helpers allocate/free on-disk log space and initialize the first log state sectors.

## Behavior And Data Flow

`lufs_enable()` computes a safe log size from requested size, filesystem size, cylinder group count, and tunables, then write-locks the filesystem, allocates contiguous-ish log extents through a dummy shadow inode, initializes log state, calls `lufs_snarf()`, starts logging support threads, and marks the superblock `FSLOG`.

`lufs_disable()` write-locks and quiesces the filesystem, flushes outstanding transactions, stops delete/reclaim/roll activity as needed, tears down in-core log state, frees on-disk log extents, marks the superblock active/no-log, and unlocks the filesystem.

`lufs_snarf()` reads and checksums the log extent table, builds an in-core extent table, reads duplicated log state sectors, validates version/checksum/bad-log state, creates delta/log/mata maps, scans existing log records, and starts the roll thread for read-write mounts.

## Logged I/O Strategy

`lufs_read_strategy()` overlays logmap deltas on reads. If no overlapping deltas exist, it reads the master device directly; otherwise it may read the master first, then calls `ldl_read()` to apply logged deltas.

`lufs_write_strategy()` removes matching deltas from the deltamap and moves them to the logmap with `logmap_add()` or cached roll buffers. Writes without metadata deltas pass through to the device or snapshot layer, with debug checks preventing unlogged metadata writes.

## Dependencies And Risks

This file depends on the transaction layer in `lufs_top.c`, map/logmap code in `lufs_map.c`, log-device code in `lufs_log.c`, UFS lockfs/quiesce/thread helpers, snapshots, and kstats.

High-risk areas are enable/disable ordering, superblock state transitions, log extent allocation rollback, bad-log handling on read-only mounts, `ufs_scan_lock` synchronization while linking/unlinking `vfs_log`, and the strategy paths that decide whether data must be served from master, log, or both.
