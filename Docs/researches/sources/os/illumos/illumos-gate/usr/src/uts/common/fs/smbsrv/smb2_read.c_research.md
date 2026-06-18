# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_read.c

Implements SMB2 read handling, including optional zero-copy read support.

Key behavior:
- Decodes SMB2 read requests and validates structure size, length, minimum count, offset, FID, channel, and flags.
- Rejects reads larger than `smb2_max_rwsize`; zero-length reads return success with no data.
- For disk files, rejects directory reads, checks byte-range locks, optionally requests VFS zero-copy buffers, and falls back to allocated mbufs.
- For IPC pipes, reads through `smb_opipe_read()`.
- Handles unbuffered reads by translating the request to `FRSYNC` when `smb_allow_unbuffered` allows it.
- Trims mbufs to transferred length, attaches them to `sr->raw_data`, and updates file seek position.
- Fails with `NT_STATUS_END_OF_FILE` if transferred bytes are below `MinCount`.

Important dependencies:
- Filesystem read path: `smb_fsop_read`, `smb_fsop_reqzcbuf`, `smb_fsop_retzcbuf`.
- Buffering: `smb_mbuf_allocate`, `smb_mbuf_alloc_ext`, `MBC_ATTACH_MBUF`.
- Locking: `smb_lock_range_access`.

Notable details:
- `smb_xuio_t` reference counting ensures borrowed VFS zero-copy buffers are returned only after all external mbufs release them.
