# File Research: sources/os/linux/linux-stable/fs/9p/vfs_file.c
- Purpose: Implements 9P regular-file open/read/write/mmap/fsync/locking operations.
- Main functions: `v9fs_file_open`, lock helpers, `v9fs_file_read_iter`, `v9fs_file_write_iter`, `v9fs_file_fsync`, `v9fs_file_fsync_dotl`, `v9fs_file_mmap_prepare`, `v9fs_vm_page_mkwrite`.
- Open flow: Clones or looks up a FID, opens it with the right 9P mode, stores it in `file->private_data`, initializes cache usage, and records open FIDs for writeback.
- I/O flow: Cached modes use generic/netfs paths; direct behavior issues 9P client reads/writes through the open FID.
- Locking: Supports legacy 9P lock protocol and dotl `getlock`/`lock`/`flock` behavior with VFS lock structures.
- Mmap behavior: Prepares cached mappings and handles page write faults for writeback-capable mappings.
- Risks: File flag to protocol-mode mapping, fscache cookie use/unuse, and FID lifetime around open/writeback are correctness-sensitive.
