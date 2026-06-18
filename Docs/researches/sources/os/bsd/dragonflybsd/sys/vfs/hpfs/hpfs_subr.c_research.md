# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_subr.c

Source read: complete file, 868 lines.

Purpose: HPFS support routines for checksums, bitmap loading/flushing/searching/marking, codepage loading and filename comparison, parent directory metadata validation/update, fnode writeback, file size extension/truncation, and typed metadata reads.

Key interfaces:
- `hpfs_checksum()` computes HPFS-style rotating additive checksum.
- `hpfs_bminit()` loads the bitmap index and all bitmap bands, then counts free sectors.
- `hpfs_bmdeinit()` writes dirty in-memory bitmaps back on read-write mounts and frees bitmap memory.
- `hpfs_bmlookup()`, `hpfs_bmfblookup()`, and `hpfs_bmmark()` find free runs, find a single free block, and mark contiguous blocks free or busy.
- `hpfs_cpinit()`, `hpfs_cpload()`, and `hpfs_cpdeinit()` load on-disk codepage data and optional user-provided conversion tables.
- `hpfs_cmpfname()` and `hpfs_cpstrnnicmp()` compare names with HPFS uppercasing and conversion tables.
- `hpfs_validateparent()` searches the parent directory tree to cache a node's dirent name and timestamps.
- `hpfs_updateparent()` writes cached access/modify time and size changes back to the parent dirent.
- `hpfs_update()` writes the fnode to disk and chains parent update if needed.
- `hpfs_truncate()` and `hpfs_extend()` adjust allocation trees and file size.
- `hpfs_breadstruct()` reads a metadata structure and validates its leading magic.

Implementation notes:
- Bitmap bands are 0x4000 sectors each, with one 4-sector bitmap per band.
- `hpfs_bmlookup()` first tries a requested nearby LSN, then scans data bands circularly.
- `hpfs_bmmark()` treats set bits as free and clear bits as busy, updating `hpm_bavail`.
- Codepage tables default to identity mapping for high-half bytes unless `HPFSMNT_TABLES` supplies conversion arrays.
- Parent validation performs a depth-first walk of directory down-pointers and climbs back via `d_parent`.

Integration:
- Used by mount/unmount, vnode read/write/setattr/fsync, lookup, and allocation helpers.

Risks and review notes:
- The source explicitly notes bitmap operations need locking; concurrent allocation/free paths can race without external serialization.
- `hpfs_bmmark()` logs out-of-volume marking but returns success (`0`), which can hide metadata corruption.
- Codepage allocation failure cleanup is incomplete in some `hpfs_cpinit()` error paths; allocated `hpm_cpdblk` can leak if later loads fail before mount teardown handles it.
