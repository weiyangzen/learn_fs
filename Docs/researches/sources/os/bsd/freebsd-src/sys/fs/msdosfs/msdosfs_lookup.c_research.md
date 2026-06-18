# File Research: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfs_lookup.c

Implements msdosfs directory lookup, creation-entry insertion, directory emptiness checks, rename path safety, directory-entry reads, removal, and unique short-name generation.

Main responsibilities:
- `msdosfs_lookup()` delegates cached lookup to `msdosfs_lookup_ino()`.
- `msdosfs_lookup_ino()` scans directory entries, matches DOS 8.3 and VFAT long names, handles create/rename/delete lookup semantics, and returns target denodes.
- `createde()` writes a new short directory entry plus optional preceding VFAT long-name entries.
- `dosdirempty()` checks whether a directory contains only `"."` and `".."`.
- `doscheckpath()` prevents moving a directory into its own subtree.
- `readep()` and `readde()` read directory-entry blocks.
- `removede()` marks short and preceding long-name entries deleted.
- `uniqdosname()` finds a collision-free generated 8.3 name.

Key implementation details:
- Root `"."` and `".."` are faked because FAT root directories do not contain real dot entries.
- Lookup first converts the requested component with `unix2dosfn()` and computes required VFAT slot count with `winSlotCnt()` unless short-name mode forces 8.3-only behavior.
- Directory scanning uses `pcbmap()` cluster by cluster, reads backing device blocks, and tracks reusable empty/deleted slots for create/rename.
- VFAT entries are accumulated with `mbnambuf`; a valid long-name checksum match wins, otherwise a short 8.3 match is used when allowed.
- Volume label and VFAT entries are ignored as normal file targets.
- For create/rename miss at last component, the parent directory write permission is checked and `de_fndoffset`/`de_fndcnt` record where new entries should be written.
- For delete and rename hit cases, root deletion is rejected and parent write access is required.
- Dot-dot lookup uses `vn_vget_ino_gen()` and then revalidates that `".."` still maps to the same synthetic inode after parent locking was dropped.
- `createde()` extends the directory when the chosen slot is beyond current size, writes the short entry, then writes LFN entries backward across block boundaries as needed.
- `removede()` decrements the denode refcount and aggressively deletes preceding Win95 entries that appear associated or invalid.
- `uniqdosname()` iterates generation numbers and scans the directory for exact short-name collisions.

Important dependencies:
- Name conversion from `msdosfs_conv.c`.
- Cluster mapping/allocation from `msdosfs_fat.c`.
- Denode creation from `msdosfs_denode.c`.
- VFS namei flags and vnode locking semantics.

Notable risks and edge cases:
- Negative namecache insertion is disabled because the cache does not understand FAT case-insensitivity and 8.3 aliasing.
- Corrupted filesystems can violate directory hardlink assumptions; `msdosfs_lookup_checker()` detects target vnode equal to parent and reports integrity errors.
- `doscheckpath()` may return a wait cluster when it cannot immediately lock an ancestor denode.
