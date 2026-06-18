# File Research: sources/os/linux/linux-stable/fs/udf/udf_i.h

## Summary
Defines UDF per-inode in-memory state and extent-position/cache helpers.

## Main Responsibilities
- Defines `struct extent_position` for current allocation descriptor location.
- Defines `struct udf_ext_cache` for cached logical extent position.
- Defines `struct udf_inode_info`, embedding the VFS inode and UDF-specific metadata.
- Provides `UDF_I()` container accessor.

## Important Behavior
The comments define the locking contract: regular-file and symlink allocation metadata is protected by `i_data_sem` and inode mutex; directory allocation metadata is protected by inode mutex.

## Risks
Many UDF paths rely on `i_lenEAttr`, `i_lenAlloc`, `i_lenExtents`, `i_alloc_type`, and `i_data` being coherent. Extent cache access is protected by `i_extent_cache_lock`.
