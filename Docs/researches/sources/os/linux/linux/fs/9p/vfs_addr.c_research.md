# File Research: sources/os/linux/linux/fs/9p/vfs_addr.c

Implements 9p address-space operations through the kernel netfs library.

Key behavior:
- `v9fs_init_request()` selects a FID for netfs read/write requests:
  - Uses `file->private_data` when a file is present.
  - Otherwise searches open inode FIDs, requiring writability for write-style origins.
  - Computes request `wsize` from client `msize`, limited by FID `iounit`.
- Writeback delays choosing a write FID until dirty data actually needs upload.
- `v9fs_begin_writeback()` finds a writable open FID for writeback and attaches it to the netfs request.
- `v9fs_issue_read()` issues `p9_client_read()`, marks clear-tail for buffered reads, notes EOF, and completes the netfs subrequest.
- `v9fs_issue_write()` issues `p9_client_write()` and completes the netfs subrequest.
- `v9fs_free_request()` drops the FID reference stored in `netfs_priv`.
- `v9fs_addr_operations` wires folio read, readahead, dirtying, release, invalidation, direct I/O placeholder, writepages, and migration to netfs/filemap helpers.

Important interactions:
- The address-space operations are installed by `v9fs_init_inode()`.
- FID mode decisions from `fid.h` determine when file operations enter these cached netfs paths.
