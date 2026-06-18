# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_init.c

## Role

Maintains the global filesystem-type registry and module event path for FreeBSD VFS implementations. It also fills default `vfsops` methods and wraps selected filesystem operations with signal-stop deferral for filesystems marked with `VFCF_SBDRY`.

## Main Entry Points

- `vfs_byname()` finds a registered filesystem type by name and increments `vfc_refcount`; it aliases `ffs` to `ufs`.
- `vfs_byname_kld()` tries `vfs_byname()`, attempts `kern_kldload()` on miss, then looks up again and may unload the module if registration failed.
- `vfs_unref_vfsconf()` releases a registry reference.
- `vfs_modevent()` handles `MOD_LOAD` by calling `vfs_register()` and `MOD_UNLOAD` by calling `vfs_unregister()`.

## Registration Flow

`vfs_register()` validates `VFS_VERSION`, prevents duplicate names, assigns `vfc_typenum`, appends to the global `vfsconf` TAILQ, fills missing `vfsops` methods with standard implementations, optionally installs the signal-defer wrapper table, calls filesystem `vfs_init`, registers jail support, and renumbers matching `vfs.<fstype>` sysctl nodes to match the filesystem type number.

When `vfs.typenumhash` is enabled, type numbers are derived from an FNV-1 hash of `vfc_name` and collision-resolved in the 1..255 range where possible. This is meant to keep NFS file handles stable across different module load orders.

`vfs_unregister()` refuses removal when the filesystem is unknown or has outstanding references, calls `vfs_uninit`, removes the entry, and recomputes `maxvfsconf`.

## Signal-Deferral Wrappers

The `vfsops_sigdefer` table wraps mount, unmount, root, cachedroot, quotactl, statfs, sync, vget, fhtovp, checkexp, extattrctl, sysctl, purge, and lock-report operations. Each wrapper calls `sigdeferstop(SIGDEFERSTOP_SILENT)` around the underlying filesystem method and restores stop handling afterward.

## Locking And Lifetime

The registry is protected by `vfsconf_sx`. Reference counts are manipulated while holding this sx lock. Registration and unregistration also coordinate with sysctl locking when modifying filesystem sysctl OIDs.

## Dependencies

This file is central to mount-time lookup in `vfs_mount.c` and root-mount lookup in `vfs_mountroot.c`. It depends on linker KLD loading, prison/jail VFS registration, sysctl internals, and standard VFS fallback methods.

## Notes

The design supports third-party extension of operation vectors by normalizing missing methods at registration time and allows binary-compatible additions through multiple operation-vector descriptors, as described in the file comments.
