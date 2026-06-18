# File Research: sources/os/bsd/freebsd-src/sbin/mount/mount.c

## Summary
Main implementation of FreeBSD’s generic `mount` utility. It lists mounted filesystems, mounts all eligible fstab entries, mounts by fstab lookup, remounts mounted filesystems, delegates legacy filesystem types to `mount_*` helpers, or performs direct `nmount()` through `mount_fs()`.

## Main Responsibilities
- Parses global options: all mounts, debug, alternate fstab, force, late mounts, options, fstab-style output, read-only/read-write, update, verbose, and type filters.
- Handles `mount -a`, `mount -p`, plain listing, one-argument fstab/current lookup, and two-argument direct mount forms.
- Infers NFS for `host:path` or `path@host`-style specs when no type is specified.
- Maintains compatibility with external helpers for `cd9660`, `mfs`, `msdosfs`, `nfs`, `nullfs`, `smbfs`, `udf`, and `unionfs`.
- Converts fstab/current meta-options, removes contradictory options, and strips boot-only options before mounting.
- Emits mount listing through `libxo`.
- Signals mountd via `/var/run/mountd.pid` after successful root-initiated mounts.

## Key Functions
- `use_mountprog()` / `exec_mountprog()`: decide and execute helper programs.
- `specified_ro()`: detects explicit read-only options.
- `ismounted()` / `isremountable()`: avoid duplicate `mount -a` mounts.
- `allow_file_mount()`: permits file mountpoints for nullfs.
- `hasopt()`: option presence with `no` inversion semantics.
- `mountfs()`: resolves paths, prepares helper argv, chooses helper vs direct mount.
- `mangle()`: converts comma options into helper-style arguments and handles `mountprog`.
- `update_options()`, `remopt()`, `flags2opts()`: option normalization.
- `prmount()` and `putfsent()`: output current mounts.

## Dependencies And Integration
Uses fstab APIs, `getmntinfo`, `getmntpoint`, `checkpath`, `checkpath_allow_file`, `rmslashes`, `libxo`, `libutil`, and helper programs searched through `_PATH_SYSPATH`.

## Research Notes
The code has important policy boundaries: `noauto`, `late`, `failok`, and quota options are consumed by `mount` and not passed to filesystems; `mountprog=` can force a helper. Direct mount support remains delegated to `mount_fs()`.
