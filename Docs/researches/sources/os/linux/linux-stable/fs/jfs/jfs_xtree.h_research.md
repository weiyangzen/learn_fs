# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_xtree.h

## Purpose

Defines the on-disk/in-memory extent allocation descriptor types and public xtree APIs used by JFS file mapping, growth, update, append, and truncation code.

## Main Definitions

- `xad_t` is a 16-byte extent descriptor with flags, a 40-bit logical offset split across `off1/off2`, and a `pxd_t` physical location/length.
- `MAXXLEN` caps an XAD length at 24 bits.
- `XADoffset`, `XADaddress`, and `XADlength` construct descriptor fields; `offsetXAD`, `addressXAD`, and `lengthXAD` extract them.
- XAD flags include `XAD_NEW`, `XAD_EXTENDED`, `XAD_COMPRESSED`, `XAD_NOTRECORDED`, and `XAD_COW`.
- Root/page sizing constants define inline root capacities, page capacity, and `XTENTRYSTART == 2`.
- `struct xtheader`, `xtroot_t`, and `xtpage_t` define xtree page headers and arrays.

## Exported Surface

The header declares `xtLookup`, `xtInitRoot`, `xtInsert`, `xtExtend`, `xtUpdate`, `xtTruncate`, `xtTruncate_pmap`, and `xtAppend`. These are the primary xtree services used by JFS inode, write, symlink, resize, and removal paths.

## Notes

The field macros encode endian and bit-width assumptions directly. Callers must pass filesystem-block units, not bytes, for offsets, addresses, and lengths.
