# File Research: sources/os/linux/linux/fs/jfs/jfs_types.h

Provides basic JFS type definitions and compact descriptor helpers shared across the filesystem.

Key types:
- `tid_t` and `lid_t` are 16-bit transaction and lock identifiers. Comments warn that widening them affects transaction lock overlay layout.
- `struct timestruc_t` is the JFS little-endian on-disk time pair.
- `pxd_t` is the physical extent descriptor with 24 bits of length and a 40-bit address split across two little-endian fields.
- `struct pxdlist` stores a fixed stack of PXD descriptors up to `MAXTREEHEIGHT`.
- `dxd_t` is a data extent descriptor for inline, extent, index, file, or corrupt EA/ACL-style data.
- `struct component_name` stores a UCS name and length for directory operations.
- `struct dasd` stores OS/2-compatible directory DASD quota/usage fields.

Helpers:
- `PXDlength`, `PXDaddress`, `lengthPXD`, and `addressPXD` pack/unpack PXD fields.
- DXD macros wrap PXD helpers and size conversion.
- DASD macros pack/unpack 40-bit limit/used values.

Integration:
- Used by superblock, log records, inode/extent trees, EA descriptors, Unicode name handling, and transaction maplocks.
