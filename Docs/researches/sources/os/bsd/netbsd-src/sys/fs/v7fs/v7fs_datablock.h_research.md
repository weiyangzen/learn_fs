# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_datablock.h

## Purpose
Declares the V7FS data-block allocator, iterator, size-changing helpers, and logical block-address map type.

## Main Interfaces
- `v7fs_datablock_allocate()`, `v7fs_datablock_expand()`, `v7fs_datablock_contract()`, and `v7fs_datablock_size_change()` are the mutation API used by file and vnode operations.
- `v7fs_datablock_foreach()` provides a callback iterator for directory scans and file operations.
- `v7fs_datablock_last()` and `v7fs_datablock_addr()` expose block mapping.
- `struct v7fs_daddr_map` stores indirect level and up to three indexes.

## Dependencies
Consumers must provide `struct v7fs_self`, `struct v7fs_inode`, and V7FS address/offset typedefs from the core headers.
