# File Research: sources/os/linux/linux/fs/udf/file.c

## Purpose
Implements UDF regular file operations, mmap page-fault write allocation, ioctl handling, write path integration, fsync, release-time cleanup, and setattr.

## Main Functions
- `udf_page_mkwrite()`: handles writable mmap faults, allocating blocks for non-in-ICB files and dirtying the folio.
- `udf_file_write_iter()`: performs generic write checks, expands in-ICB files when needed, writes data, updates in-ICB allocation length, syncs if required.
- `udf_ioctl()`: supports volume ID, block relocation, extended attribute size/block retrieval.
- `udf_release_file()`: on last writer close, discards preallocation and truncates tail extent.
- `udf_file_mmap()`: installs UDF vm ops.
- `udf_fsync()`: syncs file data plus metadata buffer tracking via `mmb_fsync`.
- `udf_setattr()`: validates ownership restrictions, handles truncate/extend via `udf_setsize()`, updates extra permissions, copies attrs.
- `udf_file_operations`, `udf_file_inode_operations`: VFS operations tables.

## Important Design Points
- In-ICB files are expanded to normal allocation descriptors when a write would no longer fit in the file entry.
- `page_mkwrite` coordinates with pagefault accounting and mapping invalidation locks.
- UID/GID changes can be blocked when mount options force fixed UID/GID.
- Release-time preallocation cleanup only runs for the final writer.

## Cross-File Relationships
- Calls `udf_expand_file_adinicb()`, `udf_get_block()`, `udf_setsize()`, `udf_discard_prealloc()`, and `udf_truncate_tail_extent()` from inode/truncate code.
- Uses `udf_relocate_blocks()` from relocation support outside this group.
- `inode.c` assigns these operations to regular files.

## Risks / Review Notes
- `udf_ioctl()` requires read permission for all supported commands and `CAP_SYS_ADMIN` for block relocation.
- `udf_page_mkwrite()` returns `VM_FAULT_NOPAGE` if the folio no longer maps valid file content.
- In-ICB expansion must be done under inode lock; this file honors that in write path.
