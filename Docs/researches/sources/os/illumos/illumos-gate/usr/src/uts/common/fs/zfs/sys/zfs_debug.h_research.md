# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_debug.h

Defines ZFS debug flags, debug printf plumbing, panic recovery hook, and debug-message buffering interfaces.

Key elements:
- `ZFS_DEBUG` is enabled for debug builds or non-kernel builds.
- Global controls include `zfs_flags`, `zfs_recover`, and `zfs_free_leak_on_eio`.
- Debug flag bits cover dprintf, dbuf/dnode verification, snapnames, modify, zio free, histogram, metaslab, indirect remap, trim, and log spacemap verification.
- `dprintf_zfs()` emits through `__dprintf()` when `ZFS_DEBUG_DPRINTF` is set.
- `zfs_dbgmsg_t` stores timestamped variable-length debug messages.

Main dependencies and interactions:
- Used broadly by txg and storage code for conditional diagnostics.
- Non-kernel builds expose `dprintf_find_string()`.

Implementation notes:
- `dprintf_zfs()` compiles to no-op outside debug mode.
