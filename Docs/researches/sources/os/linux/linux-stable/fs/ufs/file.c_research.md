# File Research: sources/os/linux/linux-stable/fs/ufs/file.c

## Summary
Defines regular file operations for the UFS filesystem using generic Linux file helpers.

## Main Responsibilities
- Provides generic seek, read, write, mmap preparation, open, fsync, splice read/write, and lease operations.
- Delegates actual block mapping and page-cache behavior to UFS inode address-space operations.

## Important Behavior
No custom read/write logic lives here; UFS-specific allocation and mapping are in `inode.c`.

## Risks
Write behavior is only as safe as the configured UFS write support and the address-space operations backing these generic file operations.
