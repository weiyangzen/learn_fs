# File Research: sources/os/linux/linux/fs/smb/server/vfs_cache.h

Declares ksmbd file/inode cache structures, fid constants, lock/stream state, durable owner metadata, and file-table APIs.

Key contents:
- Windows generic access constants and fid sentinel values.
- `ksmbd_lock` for SMB byte-range lock tracking across connection/file/global lists.
- `stream` for alternate data stream xattr state.
- `ksmbd_inode` for per-dentry shared state: locks, refcounts, open lists, oplocks, attributes, delete flags.
- `ksmbd_file` for per-open handle state: file pointer, persistent/volatile IDs, connection/tree, access/share/create options, times, GUIDs, stream, locks, readdir state, durable/resilient/persistent flags, POSIX-context flag, and durable owner.
- `ksmbd_file_table` wrapping an IDR with lock.
- Inline helpers for valid file IDs and stream handles.
- Public APIs for file-table init/destroy, open/close/lookup/put, inode lookup/put/status, durable lookup/open/reopen/scavenger, tree/session close, global file table init/free, fd limit, file state update, durable owner comparison, inode hash lifecycle, delete-on-close flags, and file cache lifecycle.

Role in subsystem:
- Shared type and API definition for ksmbd handle management.
