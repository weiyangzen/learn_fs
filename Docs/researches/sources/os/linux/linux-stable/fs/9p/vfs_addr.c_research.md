# File Research: sources/os/linux/linux-stable/fs/9p/vfs_addr.c
- Purpose: Implements 9P address-space operations through the kernel netfs library.
- Main functions: `v9fs_begin_writeback`, `v9fs_issue_write`, `v9fs_issue_read`, `v9fs_init_request`, `v9fs_free_request`.
- Netfs integration: Provides `v9fs_req_ops` callbacks and `v9fs_addr_operations` using `netfs_read_folio`, `netfs_readahead`, `netfs_dirty_folio`, `netfs_writepages`, and related helpers.
- FID handling: Finds or references a suitable FID for reads/writes, stores it in `rreq->netfs_priv`, and releases it when the request completes.
- I/O behavior: Uses `p9_client_read` and `p9_client_write`, sizing requests by `msize`, protocol header size, and optional fid iounit.
- Risks: Read-for-write and writeback require a FID with correct access mode; missing open FIDs trigger warnings and I/O errors.
