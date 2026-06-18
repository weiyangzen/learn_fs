# File Research: sources/os/bsd/freebsd-src/sys/fs/autofs/autofs_vnops.c

## Purpose
Vnode operations and synthetic node management for autofs directories.

## Main Elements
- `autofs_getattr()` returns synthetic directory attributes and can trigger mounts on `stat(2)` when configured.
- `autofs_trigger_vn()` drops the vnode lock, holds a reference, triggers automountd, relocks, and returns the mounted filesystem root if a mount appeared.
- `autofs_lookup()` handles `.`, `..`, cache checks, automount triggers, wildcard/dynamic entries, and synthetic child lookup/creation behavior.
- `autofs_mkdir()` permits only automountd descendants to create synthetic directories.
- `autofs_readdir()` triggers as needed, emits `.`, `..`, and child directory entries, and validates directory offsets.
- `autofs_reclaim()` clears vnode linkage but leaves node freeing to unmount/node deletion.
- VOP vector disables unsupported mutation operations except daemon-controlled mkdir.
- `autofs_node_new()`, `autofs_node_find()`, `autofs_node_delete()`, and `autofs_node_vn()` manage RB-tree nodes, callouts, locks, and vnode creation/reuse.

## Dependencies And Integration
Uses VFS lookup, vnode locking, `vn_vget_ino_gen`, mounted-here transitions, dirent formatting, RB trees, and autofs trigger APIs.

## Risk Notes
The lock dance around triggering is critical because the daemon may mount over the vnode while lookup/stat/readdir waits.
