# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/objfs/objfs_root.c

## Purpose
Implements the root directory of objfs, listing one directory per currently loaded kernel module.

## Main Entry Points
- `objfs_create_root()` creates the GFS root vnode with custom lookup/readdir callbacks.
- `objfs_root_getattr()` reports root directory attributes, including link count based on loaded object count.
- `objfs_root_do_lookup()` resolves a module name to an object-directory vnode.
- `objfs_root_do_readdir()` emits loaded module names as directory entries.
- `objfs_root_readdir()` wraps GFS directory iteration.
- `objfs_tops_root[]` registers root VOPs.

## Internal Mechanics
Lookup walks the global `modules` circular list under `mod_lock` and matches loaded modules by `mod_modname`. It drops `mod_lock` around vnode allocation because `modctl` structures are persistent.

Readdir uses module ids as offsets/cookies. It compares against `last_module_id` for EOF, skips unloaded modules, emits `mod_modname`, and assigns inode numbers with `OBJFS_INO_ODIR()`.

## Dependencies
Uses GFS root/directory helpers, global module list state, `mod_lock`, `last_module_id`, objfs inode macros, and common objfs directory helpers.

## Risks and Notes
Directory contents are live views of currently loaded modules. Readdir offset logic assumes module ids are monotonic and persistent enough for cookie-style iteration.
