# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/autofs/auto_vfsops.c

## Purpose

`auto_vfsops.c` registers autofs as a kernel filesystem and syscall provider, defines autofs mount options, manages per-zone autofs global state, and implements autofs VFS operations: mount, unmount, root, and statvfs.

## File Shape

- Size: 832 lines, 20,992 bytes.
- SHA-256: `a3bde715e28ff1e1d605e7f6c831130b0b96ddc8768b615efc988e337f21c5b4`.
- Module entry points: `_init()`, `_fini()`, `_info()`.
- VFS init and operations: `autofs_init()`, `auto_mount()`, `auto_unmount()`, `auto_root()`, `auto_statvfs()`.
- Per-zone lifecycle: `autofs_zone_init()` and `autofs_zone_destructor()`.

## Core Behavior

- Registers both filesystem ops and the `autofssys` syscall, including 32-bit syscall registration when `_SYSCALL32_IMPL` is enabled.
- Defines mount options for `direct`, `indirect`, `ignore`, `nest`, `browse`, `nobrowse`, and `restrict`, with mutually canceling direct/indirect and browse/nobrowse options.
- `autofs_zone_init()` allocates `autofs_globals`, creates the persistent per-zone root fnnode, initializes daemon and unmount-thread locks, and starts the zone's periodic unmounter thread.
- `autofs_zone_destructor()` asserts only the persistent root fnnode remains, releases any daemon door handle, adjusts the root vnode count for `auto_freefnnode()`, destroys locks, and frees globals.
- `autofs_restrict_opts()` appends inherited restricted mount options to option strings when the `restrict` option is present.
- `auto_mount()` enforces mount privilege, rejects cross-zone global-zone mounts, rejects zone shutdown, initializes zone globals, copies native or 32-bit mount arguments, supports remount updates for directness/timeouts/options/map, allocates and fills `fninfo_t`, creates a unique device ID, copies address/path/options/map/subdir/key, initializes loopback `knconf`, creates the root fnnode, and links user-level mounts into the per-zone top-level autofs list.
- `auto_unmount()` denies forced unmount, checks root vnode/dirent busyness, unlinks root fnnodes from the per-zone list when applicable, releases the root node, and frees `fninfo_t` allocations.
- `auto_statvfs()` returns synthetic empty filesystem stats with the autofs type name and `MAXNAMELEN`.

## Dependencies And Contracts

- Uses `zone_key_create()` for per-zone global state but avoids a constructor because zone-specific construction starts kernel threads.
- Relies on `auto_makefnnode()` and `auto_do_unmount()` from `auto_subr.c` and `auto_vnodeops_template` from `auto_vnops.c`.
- Uses `/dev/ticotsord` lookup to populate loopback transport config for automountd-related communication.

## Maintenance Notes

The module intentionally cannot unload (`_fini()` returns `EBUSY`). Mount argument copying is split for kernel-space, native user-space, and 32-bit user-space callers; all three paths must stay structurally aligned with `struct autofs_args`. The global zone path check prevents mounting autofs for a different zone through a visible zone path.
