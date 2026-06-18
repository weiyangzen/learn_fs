# File Research: sources/os/linux/linux/fs/smb/server/mgmt/ksmbd_ida.h

This header declares KSMBD IDA helpers and documents SMB protocol ID restrictions.

Important notes:
- TID `0xFFFF` must not be used as a valid SMB1-style TID.
- UID `0xFFFE` is reserved by LAN Manager history and should not be used.
- Exposes helpers for SMB2 TID, SMB2 UID, async message ID, generic ID, and release.

It is used by session, tree connection, and async work management.
