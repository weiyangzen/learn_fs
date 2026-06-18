# File Research: sources/os/linux/linux-stable/fs/smb/client/smb1misc.c

This file provides SMB1 header assembly, oplock-break/dnotify response detection, and SMB packet size calculation.

Key functions:
- `header_assemble()` zeros the SMB header area, fills the SMB protocol signature, command, flags, PID, TID, UID, MID, word count, Unicode/status/signing/DFS/caseless flags, and returns the fixed request length including BCC.
- `is_valid_oplock_break()` recognizes SMB1 NT transact change-notify responses and locking-andx oplock breaks. It validates word count and lock type, locates the relevant session/tree/file by TID and FID, updates inode/file oplock state, queues oplock-break handling, and treats certain invalid-handle/bad-fid races as harmless.
- `smbCalcSize()` computes SMB message size from header size, word count, BCC field, and byte-count payload.

Concurrency and state:
- Oplock handling walks session/tcon/file lists under `cifs_tcp_ses_lock` and `tcon->open_file_lock`.
- It marks `CIFS_INODE_PENDING_OPLOCK_BREAK`, resets oplock epoch, stores the new oplock level, clears cancellation state, and calls `cifs_queue_oplock_break()`.

Dependencies:
- Uses SMB1 PDU structures, error constants, CIFS inode/file state, and server/channel helpers.
