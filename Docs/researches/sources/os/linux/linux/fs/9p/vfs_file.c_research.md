# File Research: sources/os/linux/linux/fs/9p/vfs_file.c

Implements 9p regular file operations, locking, mmap behavior, cached/unbuffered I/O selection, and fsync.

Key behavior:
- `v9fs_file_open()`:
  - Converts Linux open flags to legacy/u or dotl open modes.
  - Clones a dentry FID if `file->private_data` is not already set by atomic create.
  - With writeback caching and write-only opens, tries to open as read/write to support read-modify-write cache paths; if that fails, disables caching for that FID.
  - Uses FS-Cache cookies when enabled.
  - Applies FID cache mode flags and stores the open FID on the inode.
- Legacy `v9fs_file_lock()` only flushes/invalidates pages before local lock changes.
- Dotl locking maps POSIX and flock locks to 9p lock/getlock RPCs:
  - `v9fs_file_do_lock()` sends blocking/nonblocking `TLOCK` requests and maps server status to Linux errors.
  - `v9fs_file_getlock()` combines local conflict testing with server `TGETLOCK`.
  - Failed remote locks roll back local lock state.
- `v9fs_file_read_iter()` chooses unbuffered netfs read for `P9L_DIRECT`, otherwise cached netfs read.
- `v9fs_file_write_iter()` chooses unbuffered write for direct/no-write-cache FIDs, otherwise cached netfs write.
- `v9fs_file_splice_read()` selects copy-based splice for direct mode and filemap splice otherwise.
- Legacy fsync sends a blank `wstat`; dotl fsync sends `p9_client_fsync()`.
- mmap:
  - Non-writeback mounts only allow read-only mmap preparation.
  - Writeback mounts install vm ops that use filemap faults and `netfs_page_mkwrite()`.
  - Shared VMA close flushes the mapped byte range.

Important interactions:
- FID mode bits from `v9fs_fid_add_modes()` are the central switch for cached vs direct behavior.
- The dotl operations table includes remote lock/flock and writeback-aware mmap; legacy table has local lock behavior and read-only mmap preparation.
