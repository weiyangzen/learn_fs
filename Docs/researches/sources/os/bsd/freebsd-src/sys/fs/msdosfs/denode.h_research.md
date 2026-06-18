# File Research: sources/os/bsd/freebsd-src/sys/fs/msdosfs/denode.h

Defines msdosfs vnode-private state, FAT cache state, denode flags, directory-entry conversion macros, file ID format, and internal function prototypes.

Main responsibilities:
- Documents FAT/MS-DOS directory and root-directory quirks that drive the in-memory denode model.
- Defines `struct denode`, the filesystem-specific vnode payload.
- Defines a small FAT lookup cache for cluster-chain traversal.
- Provides conversion macros between on-disk `struct direntry` and in-memory `struct denode`.
- Declares core denode, FAT, directory, creation, truncation, and lookup helper routines.

Key structures and macros:
- `MSDOSFSROOT_OFS` is a synthetic root-directory entry offset.
- `struct fatcache` and slots `FC_LASTMAP`, `FC_LASTFC`, `FC_NEXTTOLASTFC` cache file-relative to filesystem-relative cluster mappings.
- `struct denode` stores vnode pointer, cluster write state, flags, directory-entry location, search state, refcount, mount pointer, DOS name/attributes/timestamps/start cluster/size, FAT cache, file revision, and synthetic inode number.
- Flags include `DE_UPDATE`, `DE_CREATE`, `DE_ACCESS`, and `DE_MODIFIED`.
- `MSDOSFS_FILESIZE_MAX` caps FAT files at 4 GiB minus 1.
- `DE_INTERNALIZE` and `DE_EXTERNALIZE` move fields between disk directory entries and denodes, including FAT32 high cluster bits.
- `DETIMES` updates FAT date/time fields from timespecs and honors `MSDOSFSMNT_NOWIN95`.
- `DETOI()` constructs stable synthetic inode numbers from directory location.

Important dependencies:
- Depends on FAT type predicates from `fat.h` and directory entry layout from `direntry.h`.
- Exposes internal APIs used by msdosfs vnode ops, lookup, FAT allocation, and mount code.

Notable risks and edge cases:
- FAT has no real inode numbers or link counts, so denode identity is synthesized from directory-entry location and special root handling.
- Multiple directory entries can refer to a directory via `"."`, `".."`, and parent entries; root lacks real dot entries.
- Directory sizes on disk are unreliable in normal directory entries, so runtime code often derives directory length from the FAT chain.
