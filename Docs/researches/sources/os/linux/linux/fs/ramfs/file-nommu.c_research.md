# File Research: sources/os/linux/linux/fs/ramfs/file-nommu.c

NOMMU ramfs file operation and mmap support. It implements direct/shared mappings from physically contiguous ramfs pages, plus NOMMU-specific truncate/resize behavior.

Key responsibilities:
- Defines `ramfs_file_operations` for NOMMU:
  - mmap capabilities,
  - NOMMU mmap prepare,
  - NOMMU unmapped-area lookup,
  - generic read/write,
  - splice read/write,
  - generic llseek.
- Defines `ramfs_file_inode_operations` with NOMMU-specific `setattr`.
- `ramfs_nommu_expand_for_mapping()` expands a zero-size inode into a contiguous page allocation for shared mapping.
- `ramfs_nommu_resize()` handles truncate growth/shrink, including `nommu_shrink_inode_mappings()` on shrink.
- `ramfs_nommu_setattr()` handles size-changing attributes and timestamp updates.
- `ramfs_nommu_get_unmapped_area()` checks that requested file pages exist and are physically contiguous.
- `ramfs_nommu_mmap_prepare()` accepts only NOMMU shared mappings and installs `generic_file_vm_ops`.

Important behavior:
- Growth from zero assumes the file is being prepared for shared mmap and allocates a high-order contiguous page range.
- Extra pages from the high-order allocation are freed after splitting.
- Pages are inserted into the file mapping, marked dirty and uptodate, and kept unevictable by ramfs inode setup.
- If requested pages are missing or non-contiguous, `get_unmapped_area` returns `-ENOSYS`.

Research notes:
- This file is linked only when `CONFIG_MMU` is not set.
