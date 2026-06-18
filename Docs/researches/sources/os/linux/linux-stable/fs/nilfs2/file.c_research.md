# File Research: sources/os/linux/linux-stable/fs/nilfs2/file.c

## Summary
Defines regular-file operations for NILFS, including fsync and mmap page-write handling.

## Main Responsibilities
- Synchronizes dirty NILFS files through segment construction.
- Handles mmap write faults by allocating hole blocks and marking pages dirty.
- Defines regular file operations and inode operations.

## Important Behavior
`nilfs_sync_file()` constructs either a data-sync segment for the requested range or a full segment, then flushes the backing device. It only constructs a segment when the inode is NILFS-dirty.

`nilfs_page_mkwrite()` rejects writes near disk-full conditions, validates the faulting folio, fills holes inside a transaction via `block_page_mkwrite()`, marks file blocks dirty, commits the transaction, and waits for writeback. Waiting is required because NILFS checksums data blocks during log construction and recovery validation.

Regular file operations use generic read/write/splice/open helpers, NILFS ioctl handlers, `nilfs_sync_file()`, and generic leases. Inode operations provide setattr, permission, fiemap, and file attribute get/set.

## Risks
Writable mmap faults return SIGBUS near disk-full conditions. The page fault path must carefully pair transaction begin/abort/commit and avoid using stale folios after size or mapping changes.
