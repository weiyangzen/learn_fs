# File Research: sources/os/linux/linux/fs/smb/server/mgmt/ksmbd_ida.c

This file wraps Linux IDA allocation for KSMBD protocol IDs.

Functions:
- `ksmbd_acquire_smb2_tid()` allocates SMB2 tree IDs in range `1..0xFFFFFFFE`.
- `ksmbd_acquire_smb2_uid()` allocates SMB2 session/user IDs from 1 and skips reserved `0xFFFE`.
- `ksmbd_acquire_async_msg_id()` allocates async message IDs from 1.
- `ksmbd_acquire_id()` allocates a generic ID.
- `ksmbd_release_id()` frees an ID.

The wrapper keeps protocol-reserved ID rules centralized.
