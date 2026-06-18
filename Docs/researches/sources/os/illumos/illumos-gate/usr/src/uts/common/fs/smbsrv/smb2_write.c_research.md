# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_write.c

Implements SMB2 write handling.

Key behavior:
- Decodes write request fields, skips padding, and shadows write payload into a VDB.
- Rejects writes larger than `smb2_max_rwsize`.
- Looks up FID before DTrace start probe and records read/write parameters.
- Disk/printer writes check byte-range locks, translate unbuffered or write-through flags to `FSYNC`, call `smb_fsop_write()`, break read-cache oplocks, and notify modifications on first write.
- IPC writes use `smb_opipe_write()` unless unbuffered/write-through flags are set.
- Updates open-file seek position and encodes transferred-byte count.

Important dependencies:
- Filesystem write path: `smb_fsop_write`.
- Locking/oplocks: `smb_lock_range_access`, `smb_oplock_break_WRITE`.
- Notifications: `smb_node_notify_modified`.

Notable details:
- `smb_allow_unbuffered` is global and shared with read-side behavior.
