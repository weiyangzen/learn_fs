# File Research: sources/os/linux/linux/fs/udf/udf_i.h

Purpose: UDF per-inode in-memory state.

Key contents:
- `struct extent_position` tracks current allocation descriptor buffer, offset, and logical block.
- `struct udf_ext_cache` caches extent position and logical byte start.
- `struct udf_inode_info` extends VFS inode with UDF metadata: creation time, physical location, unique ID, EA/allocation/extent lengths, allocation hints, checkpoint, extra permissions, allocation type bits, EFE/use/stream/hidden flags, inline data pointer, stream directory info, extent synchronization, metadata buffer-head tracking, and extent cache lock.
- `UDF_I()` converts VFS inode to UDF inode info.

Integration:
- Used across all UDF inode, directory, allocation, symlink, truncate, partition, and superblock code.
- The comment defines locking discipline: regular file/symlink allocation state is protected by `i_data_sem` and inode mutex; directories rely on inode mutex.

Risks and invariants:
- `i_alloc_type`, `i_lenEAttr`, `i_lenAlloc`, and `i_data` jointly determine where inline data and allocation descriptors live.
- Extent cache is protected separately by `i_extent_cache_lock`.
