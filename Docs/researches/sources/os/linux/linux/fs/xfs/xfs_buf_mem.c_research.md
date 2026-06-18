# File Research: sources/os/linux/linux/fs/xfs/xfs_buf_mem.c

Implements memory-backed XFS buffer targets used by online fsck and ephemeral ordered recordsets. Instead of a block device, the buffer target is backed by an unlinked shmem file.

Key behavior:
- `xmbuf_alloc` creates a private shmem file, configures a buftarg with no block device, sets PAGE_SIZE sector geometry, and initializes buffer target state.
- `xmbuf_free` destroys the buftarg and drops the shmem file reference.
- `xmbuf_map_backing_mem` maps exactly one PAGE_SIZE folio for a buffer, marks it dirty to keep it resident, and exposes the folio address through `bp->b_addr`.
- `xmbuf_verify_daddr` validates addresses against the shmem inode maximum size.
- `xmbuf_finalize` discards stale folios or runs buffer structure verification for non-stale buffers.
- `xmbuf_trans_bdetach` forcibly detaches memory-backed buffers from transactions after clearing dirty/logged/stale state, because direct-mapped memory buffers do not need ordinary writeback.

This file adapts the existing XFS buffer cache to in-memory, verifier-checked metadata structures without exposing the backing storage to userspace.
