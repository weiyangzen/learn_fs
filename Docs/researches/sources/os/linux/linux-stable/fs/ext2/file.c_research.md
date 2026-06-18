# File Research: sources/os/linux/linux-stable/fs/ext2/file.c

## Summary
Implements ext2 regular file operations, including buffered I/O dispatch, direct I/O through iomap, DAX I/O and faults, fsync, mmap preparation, file open/release, and file inode operations.

## Main Responsibilities
- Selects DAX, direct I/O, or buffered read/write paths.
- Handles DAX mmap faults and write faults.
- Implements direct I/O fallback to buffered writes for unsupported hole writes.
- Discards reservation windows when writable file instances are released.
- Syncs metadata buffer tracking through `mmb_fsync()`.
- Exposes file xattr, ACL, fiemap, attribute, and fileattr operations.

## Key APIs
- `ext2_file_operations`.
- `ext2_file_inode_operations`.
- `ext2_fsync()`.
- `ext2_dio_read_iter()`, `ext2_dio_write_iter()`.
- DAX helpers under `CONFIG_FS_DAX`.

## Important Behavior
DAX reads/writes use `dax_iomap_rw()` under inode locks. DAX faults take pagefault and invalidate-lock protection. Direct writes force synchronous completion for extending or unaligned writes, then may fall back to buffered write for remaining data.

`ext2_file_open()` enables `FMODE_CAN_ODIRECT` and initializes quotas. `ext2_release_file()` discards block reservations for writable file handles under `truncate_mutex`.

## Risks
Direct I/O on non-extent ext2 must avoid stale data exposure when writing holes; the code returns `-ENOTBLK` to force buffered fallback. Reservation lifetime depends on release/truncate/evict paths discarding windows at the right times.
