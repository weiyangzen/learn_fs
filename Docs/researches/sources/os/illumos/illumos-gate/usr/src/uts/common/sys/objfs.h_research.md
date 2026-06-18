# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/objfs.h

## Purpose

`objfs.h` is the public header for illumos object filesystem metadata. It defines the objfs root path, a helper to recover a module ID from an objfs inode number, and the private `.info` payload structure exposed by objfs data files.

## Main Definitions

`OBJFS_ROOT` is `/system/object`. `OBJFS_MODID(ino)` masks the low 32 bits of an inode number to obtain the module ID, with undefined results for the root inode. `objfs_info_t` currently contains one field, `objfs_info_primary`, representing the primary/private data stored in the `.info` section.

## Integration Notes

The implementation header `objfs_impl.h` builds inode numbers as a high 32-bit type plus low 32-bit module ID. This public header exposes only the low-bit module ID extraction, not the internal type encoding.

## Research Notes

This is a small public contract. Compatibility risk is high if `objfs_info_t` or `OBJFS_ROOT` changes, because consumers may rely on the path and structure layout.
