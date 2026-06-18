# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/extdirent.h

## Role

`extdirent.h` defines a kernel-only extended directory entry format used when `VOP_READDIR()` requests per-entry flags through `V_RDDIR_ENTFLAGS` and the filesystem supports them.

## Definitions

- `edirent_t` contains inode number, disk directory offset, per-entry flags, record length, and variable-length name.
- `EDIRENT_RECLEN()` computes 8-byte-aligned record length for a name length.
- `EDIRENT_NAMELEN()` derives name storage length from record length.
- Defines `ED_CASE_CONFLICT`, indicating that disregarding case, the entry is not unique.
- `ED_CASE_CONFLICTS()` tests the case-conflict flag.

## Filesystem Relevance

This is a VFS/filesystem ABI extension for case-insensitive or case-preserving filesystems that need to report directory-entry metadata beyond standard `dirent64`.
