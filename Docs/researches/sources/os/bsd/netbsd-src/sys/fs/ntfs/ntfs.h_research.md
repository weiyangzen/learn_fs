# File Research: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs.h

Defines core NTFS on-disk structures, mount state, constants, conversion hooks, and internal macros.

Key contents:
- On-disk format definitions:
  - Boot sector (`struct bootfile`), MFT file records, fixup headers, attributes, attribute lists, file-name attributes, index root/allocation entries, and attribute definitions.
- NTFS constants:
  - System inode numbers such as `$MFT`, `$Volume`, `$AttrDef`, root, bitmap, boot, bad cluster, and upcase.
  - Attribute type constants like `$STANDARD_INFORMATION`, `$FILE_NAME`, `$DATA`, `$INDEX_ROOT`, and `$INDEX_ALLOCATION`.
  - File flags and index flags.
- `struct ntfsmount`:
  - Holds mount pointer, bootfile, device vnode/dev_t, pinned system vnodes, MFT record size, mount uid/gid/mode/flags, free-cluster count, loaded attribute definitions, and Unicode conversion callbacks.
- Macros for converting clusters, bytes, blocks, mount/vnode/fnode pointers, and debug printing.
- Declares NTFS malloc types and vnode op vector.

Role:
- This is the foundational NTFS header shared across VFS, vnode, and subroutine files.
- It mixes public-ish installed definitions with kernel-internal structures.
