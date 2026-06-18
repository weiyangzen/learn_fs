# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/dir.h

## Purpose
Defines UFS directory entry format, directory block sizing, record sizing macros, file type conversions, and templates for `.` / `..` initialization.

## Key Contents
- Directory offset type:
  - `doff_t` as `int32_t`
  - `MAXDIRSIZE`
- Directory block and name limits:
  - `DIRBLKSIZ` equals `DEV_BSIZE`
  - `UFS_MAXNAMLEN` is 255
- `struct direct`:
  - `d_ino`, `d_reclen`, `d_type`, `d_namlen`, `d_name`
- Directory file type values:
  - `DT_UNKNOWN`, `DT_FIFO`, `DT_CHR`, `DT_DIR`, `DT_BLK`, `DT_REG`, `DT_LNK`, `DT_SOCK`, `DT_WHT`
- Conversion macros:
  - `IFTODT(mode)`
  - `DTTOIF(dirtype)`
- Directory record sizing:
  - `DIR_ROUNDUP`
  - `DIRECTSIZ(namlen)`
  - `DIRSIZ(oldfmt, dp)`, with little-endian compatibility for old directory format.
  - `OLDDIRFMT`, `NEWDIRFMT`
- Directory templates:
  - `struct dirtemplate`
  - `struct odirtemplate`

## Interactions
- Used by directory lookup, insertion, deletion, and dirhash code.
- `ufs_dirhash.c` uses `DIRSIZ`, `DIRBLKSIZ`, and `struct direct` heavily.
- ACL/extattr code includes it because those paths interact with UFS vnode/inode directory support.
