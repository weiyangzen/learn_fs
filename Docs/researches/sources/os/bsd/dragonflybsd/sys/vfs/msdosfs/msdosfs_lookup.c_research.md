# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_lookup.c

## Role

Implements MSDOSFS pathname lookup and directory-entry mutation helpers. It bridges VFS component names to FAT short names and Win95 long-name directory slots, records insertion/removal offsets in parent denodes, and provides directory safety checks used by create, delete, rename, mkdir, and rmdir paths.

## Major Entry Points

- `msdosfs_lookup()` searches a directory for a component, handles root `.`/`..` fakery, translates Unix names to DOS names, matches Win95 long-name slots, and returns locked vnodes according to old lookup flags.
- `createde()` writes a new FAT directory entry and any needed long-name entries into the parent directory.
- `dosdirempty()` scans a directory and verifies that it contains only `.` and `..`.
- `doscheckpath()` prevents renaming a directory into one of its own descendants.
- `readep()` and `readde()` load the disk block containing a particular directory entry.
- `removede()` marks a directory entry and preceding Win95 long-name slots deleted.
- `uniqdosname()` generates a collision-free short 8.3 name, with generation suffixes for long names.

## Implementation Notes

- Lookup stores `de_fndoffset` and `de_fndcnt` in the parent denode so later create, rename, or remove operations know where to write or delete directory slots.
- Long-name matching uses `mbnambuf`, `win2unixfn()`, `winChkName()`, and checksum validation against the following short entry.
- `MSDOSFSMNT_SHORTNAME` disables long-name search and forces a single short-name slot.
- Empty-slot tracking is active only for create and rename, since only those paths need insertion space.
- Root directory `.` and `..` are synthesized because non-FAT32 DOS root directories have no real entries for them.
- FAT32 root cluster aliases are normalized between `MSDOSFSROOT` and `pm_rootdirblk`.
- Lookup releases the directory block before `deget()` to avoid deadlocks reading the same entry back through the denode cache.
- `msdosfs_lookup_checker()` guards against corrupted filesystems that make a non-dot lookup resolve to the directory vnode itself.
- `doscheckpath()` walks upward through `..` entries, dropping and reacquiring denodes as it climbs, and always releases the target denode before returning.
- `removede()` deliberately deletes preceding Win95 entries aggressively because unmatched long-name entries are considered invalid orphan slots.

## Dependencies

Depends on FAT block mapping (`pcbmap()`), denode lookup/cache (`deget()`), FAT directory format helpers, Win95 long-name conversion/checksum helpers, buffer-cache I/O, and old DragonFly namei/VOP lookup conventions.

## Research Notes

This file is the namespace consistency core for MSDOSFS. Its main invariant is that directory blocks and in-memory denodes are kept synchronized by reading the directory block before mutation, then updating both disk entry state and denode-derived lookup state in a controlled order.
