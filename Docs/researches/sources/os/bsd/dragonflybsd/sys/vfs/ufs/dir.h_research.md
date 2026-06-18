# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/dir.h

UFS directory entry format header.

Key responsibilities:
- Defines `doff_t` as a 32-bit directory offset and caps practical directory size at `MAXDIRSIZE`.
- Defines directory block size `DIRBLKSIZ` as `DEV_BSIZE` and maximum name length `MAXNAMLEN` as 255.
- Defines `struct direct`, the UFS directory record with inode number, record length, file type, name length, and NUL-terminated name buffer.
- Defines directory entry type constants compatible with `dirent`-style `DT_*` values.
- Defines conversion macros between inode mode file type bits and directory type values: `IFTODT` and `DTTOIF`.
- Defines `DIRECTSIZ` and endian-aware `DIRSIZ` for calculating minimal aligned directory record length, including old-directory-format support on little-endian systems.
- Defines directory templates for new and old `.`/`..` entry layouts.

Dependencies:
- Requires system constants/types such as `DEV_BSIZE`, `BYTE_ORDER`, and `__offsetof`.
- Used by UFS directory manipulation and dirhash code.

Notable risks:
- Directory parsing depends on record length and name length integrity; malformed on-disk entries can corrupt traversal unless callers validate.
- Old/new directory format handling is endian-sensitive.
- Directory block layout assumes 4-byte alignment and atomic transfer-sized directory blocks.
