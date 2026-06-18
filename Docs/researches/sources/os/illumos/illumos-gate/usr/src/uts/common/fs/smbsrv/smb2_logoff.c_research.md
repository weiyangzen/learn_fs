# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_logoff.c

Read completely. This file implements SMB2 `LOGOFF`.

`smb2_logoff()` decodes the 4-byte request structure, validates `StructSize == 4`, requires an active `uid_user`, emits DTrace probes, sets `sr->uid_user->preserve_opens = SMB2_DH_PRESERVE_ALL`, and calls `smb_user_logoff()`. The preservation flag is important for durable handle policy in `smb_dh_should_save()`: protocol logoff requests preserve durable opens for reconnect instead of destroying them.

On success it encodes a minimal SMB2 Logoff reply with structure size 4 and reserved zero. The command suppresses tree requirements in the dispatch table but still requires a user session.
