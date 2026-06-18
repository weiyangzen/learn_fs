# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_vtops.c

This file implements dynamic vnode operations for the `/dev/vt` directory. It builds and validates virtual terminal device nodes and special symlinks.

Core responsibilities:
- Defines `devvt_vnodeops_tbl`, overriding lookup, readdir, create, and disallowing mutation operations for `/dev/vt`.
- Exposes `devvt_getvnodeops()` for installing these operations on the dynamic directory.
- Creates numeric VT character-device entries with default mode `0600`.
- Creates `active` and `console_user` symlink entries.
- Validates cached `/dev/vt` entries against the current VT subsystem state.

Important operations:
- `devvt_str2minor` parses numeric entry names into VT minor numbers.
- `devvt_validate` classifies cached entries as valid, invalid, stale, or skipped. It checks `vt_wc_attached()`, `vt_minor_valid()`, and compares symlink targets for `active` and `console_user`.
- `devvt_create_rvp` is the lookup callback used by `devname_lookup_func`; it returns either a device vattr or a symlink target buffer.
- `devvt_lookup` chooses `SDEV_VLINK` for special symlink names and `SDEV_VATTR` for numeric devices, then verifies the returned vnode type.
- `devvt_create_snode` creates missing cached entries during directory refresh.
- `devvt_rebuild_stale_link` updates stale symlink targets in-place while holding the directory write lock.
- `devvt_prunedir` removes invalid cached entries and refreshes stale links.
- `devvt_cleandir` refreshes the whole directory on first read: prune, add valid numeric terminal nodes, and ensure `active` and `console_user` links exist.
- `devvt_readdir` triggers `devvt_cleandir` when reading from offset zero, then delegates to `devname_readdir_func`.
- `devvt_create` implements read-only create semantics: opening existing entries can succeed, but new creation returns `EROFS`, exclusive create returns `EEXIST`, and writable directory create returns `EISDIR`.

Mutation policy:
- Remove, mkdir, rmdir, symlink, and setsecattr are all `fs_nosys`.
- This directory is dynamically generated from VT state, not user-modifiable.

Research notes:
- `/dev/vt` is a compact example of sdev dynamic-directory design: validator, lookup callback, prune/rebuild, and read-only create semantics.
- `devvt_create_snode` creates symlink nodes for both special link names, but its `SDEV_VLINK` path obtains the active VT target. Validation/rebuild later distinguishes `console_user`; this is worth checking if investigating `/dev/vt/console_user` freshness or initial target behavior.
