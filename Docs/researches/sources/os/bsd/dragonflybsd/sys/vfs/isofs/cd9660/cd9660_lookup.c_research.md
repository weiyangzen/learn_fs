# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_lookup.c

Source read: complete file, 477 lines.

Purpose: cd9660 pathname lookup and directory block access helpers. It searches ISO directory records, handles ISO/Rock Ridge/Joliet-style names, resolves special entries, and provides buffer helpers for directory contents from vnode or device buffers.

Key interfaces:
- `cd9660_lookup()` implements old-style VOP lookup for ISO directories.
- `cd9660_blkatoff()` reads a block through the directory vnode and ensures buffer `bio2.bio_offset` is mapped.
- `cd9660_devblkatoff()` maps through VOP_BMAP and reads the underlying device vnode directly, putting the device offset in `bio1.bio_offset`.

Lookup implementation notes:
- Handles associated files when a component begins with `=` and Rock Ridge is not active.
- Uses `i_diroff` as a lookup cache for repeated lookup operations and may do two passes if starting from a cached offset.
- Reads directory entries block by block, rejects zero-length padding by advancing to the next block, and stops on malformed entries that are too short or cross block boundaries.
- Compares normal ISO/Joliet names through `isofncmp()` and RRIP names through `cd9660_rrip_getname()`.
- For directories, inode numbers come from `isodirino()`; for files, they can be derived from the physical directory entry offset.
- Returns `EROFS` for create/rename misses because cd9660 is read-only.
- Handles `..` by unlocking the current directory before `cd9660_vget_internal()` to avoid parent/child vnode deadlocks.
- Passes a relocated flag to `cd9660_vget_internal()` when a directory's effective inode differs from the entry-derived inode.

Integration:
- Depends on `iso.h`, `cd9660_node.h`, and `iso_rrip.h`.
- Used by cd9660 vnode operation tables outside this group.
- Directory helpers are used both by lookup and by other metadata paths that need direct directory record access.

Risks and review notes:
- The malformed-entry checks stop search but do not necessarily distinguish corruption from not-found in all cases.
- `cd9660_devblkatoff()` warns that callers must read device offsets from `bio1.bio_offset`, not `bio2.bio_offset`.
- Name sorting optimizations are conditional around `NOSORTBUG`; media with unsorted directory entries may need that compatibility behavior.
