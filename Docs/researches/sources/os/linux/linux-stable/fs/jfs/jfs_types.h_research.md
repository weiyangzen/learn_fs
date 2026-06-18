# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_types.h

## Role

Provides basic JFS type definitions and on-disk extent helper structures used across the filesystem.

## Key Definitions

- `tid_t` and `lid_t` are 16-bit transaction and lock identifiers.
- `struct timestruc_t` is a little-endian on-disk time pair.
- `pxd_t` is a physical extent descriptor with 24-bit length and 40-bit address encoding split across two little-endian words.
- Inline helpers `PXDlength`, `PXDaddress`, `lengthPXD`, and `addressPXD` construct and decode `pxd_t`.
- `struct pxdlist` stores up to `MAXTREEHEIGHT` physical extents.
- `dxd_t` describes extended attribute or ACL storage, with flags for inline, extent, file, index, and corrupt states.
- DXD helper macros reuse PXD address/length encoding and expose size helpers.
- `struct component_name` represents a UCS directory component.
- `struct dasd` stores OS/2 DASD quota/usage fields, with macros to get/set 40-bit limit and used values.

## Design Notes

This header is foundational and must be included early by JFS code. Its packed extent encodings are used by superblock, log, inode, xtree, xattr, and map update paths.
