# File Research: sources/os/linux/linux-stable/fs/ecryptfs/read_write.c

## Summary
Contains lower-file read/write helpers and a page-by-page eCryptfs write helper used outside the normal mmap path.

## Main Responsibilities
- Performs `kernel_write()` and `kernel_read()` against the lower file.
- Maps folios for lower page segment read/write.
- Implements arbitrary-offset writes with hole zeroing and optional encryption.
- Updates encrypted inode-size metadata after extending writes.

## Key APIs
- `ecryptfs_write_lower()`
- `ecryptfs_write_lower_page_segment()`
- `ecryptfs_write()`
- `ecryptfs_read_lower()`
- `ecryptfs_read_lower_page_segment()`

## Important Behavior
`ecryptfs_write()` starts at the old EOF when writing past EOF, fills gaps with zeros, copies requested data once the target offset is reached, encrypts full pages when needed, and grows `i_size` after successful writes.

## Risks
The helper assumes a valid lower file pointer in inode-private state. In the unencrypted branch of `ecryptfs_write()`, the size passed to `ecryptfs_write_lower_page_segment()` is based on cumulative copied data, so this path deserves caution when auditing partial or multi-page unencrypted writes.
