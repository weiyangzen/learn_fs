# File Research: sources/os/linux/linux-stable/fs/ramfs/file-nommu.c

## Purpose
Defines ramfs regular-file operations for no-MMU systems, including support for direct/shared mappings backed by physically contiguous pages.

## Main Components
- `ramfs_mmap_capabilities()`: advertises direct, copy, read, write, and exec no-MMU mapping capabilities.
- `ramfs_nommu_expand_for_mapping()`: allocates contiguous pages for a file grown from size zero, splits high-order allocation, zeros pages, inserts them into page cache, and marks them dirty/uptodate.
- `ramfs_nommu_resize()`: handles truncation/growth and prevents shrinking over active shared mappings via `nommu_shrink_inode_mappings()`.
- `ramfs_nommu_setattr()`: handles size-changing attribute updates and normal attribute copying.
- `ramfs_nommu_get_unmapped_area()`: verifies requested pages exist and are physically contiguous, then returns a direct address or `-ENOSYS`.
- `ramfs_nommu_mmap_prepare()`: allows only no-MMU shared mappings and installs `generic_file_vm_ops`.

## File Operations
Provides read/write/splice/llseek/fsync plus no-MMU mapping hooks.

## Edge Cases
- Growth from zero is treated as likely shared mmap setup.
- Overlarge high-order allocations return `-EFBIG`.
- If page-cache folios are missing or not physically adjacent, direct mapping is refused with `-ENOSYS`.
