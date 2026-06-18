# File Research: sources/os/linux/linux-stable/fs/gfs2/sys.h

## Scope

This header declares the small public interface for GFS2 sysfs setup, teardown, global kset lifecycle, and journal recovery triggering.

## APIs

- `gfs2_sys_fs_add()` creates per-mount sysfs entries.
- `gfs2_sys_fs_del()` removes per-mount sysfs entries and waits for kobject release.
- `gfs2_sys_init()` creates the global `gfs2` kset.
- `gfs2_sys_uninit()` unregisters the global kset.
- `gfs2_recover_set()` triggers recovery for a journal id.

## Dependencies And Invariants

Callers pass a live `struct gfs2_sbd`. `gfs2_sys_fs_del()` assumes `gfs2_sys_fs_add()` succeeded far enough to initialize the kobject and groups. Recovery triggering is implemented in `sys.c` but depends on journal readiness and recovery state outside this header.
