# File Research: sources/os/linux/linux/fs/smb/client/cifs_debug.h

CIFS debug macro and declaration header.

It sets CIFS log formatting, declares dump helpers and global debug flags, and defines message classes `VFS`, `FYI`, optional `NOISY`, and `ONCE`.

With `CONFIG_CIFS_DEBUG`, `cifs_dbg()`, `cifs_server_dbg()`, and `cifs_tcon_dbg()` dispatch to rate-limited or once-only printk variants, include contextual server/tcon names where applicable, and respect `cifsFYI` for FYI output. Without debug, most macros compile to inert `if (0) pr_debug(...)` forms while `cifs_info()` remains active.
