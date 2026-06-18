# File Research: sources/os/linux/linux-stable/fs/nilfs2/ifile.h

## Summary
Declares the NILFS inode-file API and provides inline mapping helpers for raw inode entries.

## Main Contents
- `nilfs_ifile_map_inode()` and `nilfs_ifile_unmap_inode()`.
- Inode create, delete, block lookup, free-count, and read declarations.

## Important Details
`nilfs_ifile_map_inode()` computes the palloc entry offset for an inode number and maps the containing folio locally. The caller must unmap with `nilfs_ifile_unmap_inode()`.

## Risks
Mapped raw inode pointers are only valid until the local kmap is released and must not escape the caller's critical section.
