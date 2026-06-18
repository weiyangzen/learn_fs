# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/autofs/auto_vnops.c

## Purpose

`auto_vnops.c` defines vnode operations for autofs. Its primary role is to trigger mounts on demand and then forward ordinary vnode operations to the mounted filesystem, while providing local behavior for unresolved autofs directories, readdir, symlinks, inactive cleanup, and locking.

## File Shape

- Size: 1,540 lines, 34,874 bytes.
- SHA-256: `9dff016484193c69dda9d89ef5b7ffa5c1fe5cd2ce3f9c3e9a8030f132970c12`.
- Defines `auto_vnodeops` and `auto_vnodeops_template`.
- Implements vnode ops including open, close, getattr, setattr, access, lookup, create, remove, link, rename, mkdir, rmdir, readdir, symlink, readlink, fsync, inactive, rwlock, rwunlock, and seek.
- Core helper: `auto_trigger_mount()`.

## Core Behavior

- Most mutating and passthrough vnode ops call `auto_trigger_mount()` on the relevant autofs vnode. If a real filesystem is mounted there, the operation forwards to the mounted root; otherwise unsupported operations return `ENOSYS` or appropriate errors.
- `auto_getattr()` can pre-trigger on `ATTR_TRIGGER`, forwards attributes to mounted roots when present, and has recursion protection using `fn_seen` and `fn_thread`.
- `auto_lookup()` implements direct and indirect map lookup semantics. It handles `.`, `..`, covered vnodes, existing fnnodes, creation of indirect-map placeholder nodes, daemon lookup requests, daemon mount requests, and waiting/retry behavior for concurrent lookup/mount work.
- `auto_readdir()` emits synthetic `.`/`..` and existing kernel fnnodes first, then optionally calls automountd for browse entries using `AUTOFS_READDIR`. It filters daemon entries that duplicate in-kernel entries and honors global `autofs_nobrowse`, per-mount `nobrowse`, direct maps, existing triggers, and delayed indirect behavior.
- `auto_readlink()` serves symlink targets materialized by daemon lookup actions and updates access/reference times.
- `auto_inactive()` disconnects and frees fnnodes when the last vnode reference disappears and the node has no subdirectories.
- `auto_trigger_mount()` enforces same-zone mount triggering, waits for existing lookup/mount work, detects already covered vnodes, recovers from forcibly unmounted mountpoints with triggers, and starts mount worker threads for direct or delayed-indirect triggers.

## Dependencies And Contracts

- Depends on fnnode flags and synchronization from `auto_subr.c`.
- Uses `auto_wait4mount()`, `auto_lookup_aux()`, `auto_new_mount_thread()`, `auto_search()`, `auto_enter()`, `auto_disconnect()`, `auto_freefnnode()`, `auto_nobrowse_option()`, and `unmount_subtree()`.
- Uses VFS root crossing, vnode VFS locks, VOP forwarding, and `fs_subr` default error handlers.

## Maintenance Notes

This file is race-sensitive. Lookup and trigger behavior depends on exact interactions among `MF_LOOKUP`, `MF_INPROG`, vnode holds, fnnode rwlocks, and VFS locks. Cross-zone trigger rejection in `auto_trigger_mount()` is a security constraint. `auto_readdir()` offset handling must remain compatible with both kernel-created entries and daemon cookies beginning at `AUTOFS_DAEMONCOOKIE`.
